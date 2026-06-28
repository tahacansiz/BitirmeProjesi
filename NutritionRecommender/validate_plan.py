"""
validate_plan.py
================
MILP çıktısını BAĞIMSIZ olarak doğrular.

Önemli: Bu modül, kısıtları KURAN koddan (meal_planner.milp_kur_ve_coz)
ayrı yazılmıştır. Her kısıtı sıfırdan, plan üzerinde yeniden hesaplar.
Böylece MILP kurulumundaki bir hata burada yakalanır.

Doğrulanan kısıtlar:
- Slot doluluk (zorunlu slot dolu, opsiyonel ≤ 1)
- Slot kcal aralıkları
- Günlük kalori bandı (±%5)
- Günlük makro bantları (protein/yağ/karbonhidrat)
- Günlük sodyum/şeker üst sınırı
- Çeşitlilik (aynı tarif haftada ≤ 2)
- Hard sağlık kuralları (çölyak/laktoz/böbrek/karaciğer)
- Soft sağlık haftalık ortalama
- Fiyat haftalık ortalama
- Mevsim uygunluğu
"""

from dataclasses import dataclass, field
import pandas as pd

from nutrition_targets import UserProfile, hesapla_hedefler
from meal_planner import (
    SLOT_CONFIG, MAX_AYNI_TARIF, HARD_HEALTH_RULES,
    SOFT_HEALTH_RULES, FIYAT_LIMITS, mevcut_mevsim, kcal_olcek_hesapla,
)


@dataclass
class DogrulamaSonuc:
    gecti: bool
    kontroller: list = field(default_factory=list)  # (ad, gecti, detay)

    def ozet(self):
        toplam = len(self.kontroller)
        basarili = sum(1 for _, g, _ in self.kontroller if g)
        print(f"\n{'='*64}")
        print(f"DOĞRULAMA: {basarili}/{toplam} kontrol geçti  "
              f"→  {'✓ GEÇERLİ PLAN' if self.gecti else '✗ İHLAL VAR'}")
        print('='*64)
        for ad, g, detay in self.kontroller:
            isaret = "✓" if g else "✗"
            print(f"  {isaret} {ad}")
            if not g and detay:
                for d in detay:
                    print(f"       → {d}")


def dogrula(
    user: UserProfile,
    plan: list[dict],
    df: pd.DataFrame,
    mevsim: str | None = None,
    tolerans: float = 1e-6,
) -> DogrulamaSonuc:
    """Planı bağımsız olarak doğrular."""

    targets = hesapla_hedefler(user)
    if mevsim is None:
        mevsim = mevcut_mevsim()

    # recipe_id -> tüm besin değerleri (df'ten bağımsız okuma)
    df_idx = df.set_index("recipe_id")

    kontroller = []

    def ekle(ad, gecti, detay=None):
        kontroller.append((ad, gecti, detay or []))

    # Plandaki tüm (gün, slot, recipe_id) üçlülerini topla
    secimler = []  # (gun, slot, rid)
    for gun in plan:
        for slot, o in gun["ogunler"].items():
            if o is not None:
                secimler.append((gun["gun"], slot, o["recipe_id"]))

    def besin(rid, kol):
        return float(df_idx.loc[rid, kol])

    # ---------- 1. Slot doluluk ----------
    detay = []
    for gun in plan:
        for slot, cfg in SLOT_CONFIG.items():
            dolu = gun["ogunler"].get(slot) is not None
            if cfg["zorunlu"] and not dolu:
                detay.append(f"Gün {gun['gun']}: zorunlu '{slot}' boş")
    ekle("Slot doluluk (zorunlu slotlar dolu)", len(detay) == 0, detay)

    # ---------- 2. Slot kcal aralıkları ----------
    # Planlayıcıyla aynı ölçek: yüksek kalori hedefinde üst tavan büyür.
    olcek = kcal_olcek_hesapla(targets.kalori)
    detay = []
    for gun, slot, rid in secimler:
        cfg = SLOT_CONFIG[slot]
        kcal = besin(rid, "calories_pp")
        ust = cfg["kcal_max"] * olcek
        if not (cfg["kcal_min"] <= kcal <= ust + tolerans):
            detay.append(f"Gün {gun} {slot}: {rid} = {kcal:.0f} kcal "
                         f"(beklenen {cfg['kcal_min']}-{ust:.0f})")
    ekle("Slot kcal aralıkları", len(detay) == 0, detay)

    # ---------- 3. Günlük kalori bandı ----------
    detay = []
    for gun in plan:
        toplam = sum(besin(o["recipe_id"], "calories_pp")
                     for o in gun["ogunler"].values() if o)
        alt, ust = targets.kalori * 0.95, targets.kalori * 1.05
        if not (alt - tolerans <= toplam <= ust + tolerans):
            detay.append(f"Gün {gun['gun']}: {toplam:.0f} kcal "
                         f"(bant {alt:.0f}-{ust:.0f})")
    ekle(f"Günlük kalori bandı (±%5, hedef {targets.kalori:.0f})",
         len(detay) == 0, detay)

    # ---------- 4. Günlük makro bantları ----------
    makrolar = [
        ("protein_g_pp", targets.protein_g_min, targets.protein_g_max, "Protein"),
        ("fat_g_pp",     targets.fat_g_min,     targets.fat_g_max,     "Yağ"),
        ("carbs_g_pp",   targets.carbs_g_min,   targets.carbs_g_max,   "Karbonhidrat"),
    ]
    for kol, vmin, vmax, ad in makrolar:
        detay = []
        for gun in plan:
            toplam = sum(besin(o["recipe_id"], kol)
                         for o in gun["ogunler"].values() if o)
            if not (vmin - tolerans <= toplam <= vmax + tolerans):
                detay.append(f"Gün {gun['gun']}: {toplam:.1f}g "
                             f"(bant {vmin:.0f}-{vmax:.0f})")
        ekle(f"Günlük {ad} bandı", len(detay) == 0, detay)

    # ---------- 5. Günlük sodyum/şeker üst sınırı ----------
    for kol, ust, ad in [("sodium_mg_pp", targets.sodium_mg_max, "Sodyum"),
                          ("sugar_g_pp", targets.sugar_g_max, "Şeker")]:
        detay = []
        for gun in plan:
            toplam = sum(besin(o["recipe_id"], kol)
                         for o in gun["ogunler"].values() if o)
            if toplam > ust + tolerans:
                detay.append(f"Gün {gun['gun']}: {toplam:.0f} (üst sınır {ust})")
        ekle(f"Günlük {ad} üst sınırı", len(detay) == 0, detay)

    # ---------- 6. Çeşitlilik ----------
    sayim = {}
    for _, _, rid in secimler:
        sayim[rid] = sayim.get(rid, 0) + 1
    asanlar = {r: c for r, c in sayim.items() if c > MAX_AYNI_TARIF}
    ekle(f"Çeşitlilik (aynı tarif ≤ {MAX_AYNI_TARIF})",
         len(asanlar) == 0,
         [f"{r}: {c} kez" for r, c in asanlar.items()])

    # ---------- 7. Hard sağlık kuralları ----------
    detay = []
    for kosul in user.saglik_kosullari:
        if kosul not in HARD_HEALTH_RULES:
            continue
        op, val = HARD_HEALTH_RULES[kosul]
        for gun, slot, rid in secimler:
            skor = besin(rid, kosul)
            ihlal = (op == "eq" and skor != val) or (op == "ge" and skor < val)
            if ihlal:
                detay.append(f"Gün {gun} {slot}: {rid} {kosul}={skor:.2f} (kural {op} {val})")
    ekle("Hard sağlık kuralları (asla ihlal edilemez)", len(detay) == 0, detay)

    # ---------- 8. Soft sağlık haftalık ortalama ----------
    detay = []
    n_secim = len(secimler)
    for kosul in user.saglik_kosullari:
        if kosul not in SOFT_HEALTH_RULES:
            continue
        esik = SOFT_HEALTH_RULES[kosul]
        ort = sum(besin(rid, kosul) for _, _, rid in secimler) / n_secim
        if ort < esik - tolerans:
            detay.append(f"{kosul}: haftalık ort {ort:.3f} < eşik {esik}")
    ekle("Soft sağlık haftalık ortalama", len(detay) == 0, detay)

    # ---------- 9. Fiyat haftalık ortalama ----------
    detay = []
    limit = FIYAT_LIMITS[user.fiyat_tercihi]
    if limit is not None:
        ort = sum(besin(rid, "maliyet_norm") for _, _, rid in secimler) / n_secim
        if ort > limit + tolerans:
            detay.append(f"Haftalık ort maliyet {ort:.3f} > limit {limit}")
    ekle(f"Fiyat haftalık ortalama ({user.fiyat_tercihi})", len(detay) == 0, detay)

    # ---------- 10. Mevsim uygunluğu ----------
    detay = []
    for gun, slot, rid in secimler:
        if besin(rid, mevsim) != 1:
            detay.append(f"Gün {gun} {slot}: {rid} {mevsim} mevsiminde uygun değil")
    ekle(f"Mevsim uygunluğu ({mevsim})", len(detay) == 0, detay)

    gecti = all(g for _, g, _ in kontroller)
    return DogrulamaSonuc(gecti=gecti, kontroller=kontroller)


if __name__ == "__main__":
    from meal_planner import milp_kur_ve_coz

    df = pd.read_parquet("recipes_normalized.parquet")

    user = UserProfile(yas=30, cinsiyet="erkek", boy_cm=178, kilo_kg=75,
                       aktivite="orta", fiyat_tercihi="orta")

    print("Plan üretiliyor...")
    sonuc = milp_kur_ve_coz(user, df, verbose=False, mevsim="yaz")
    print(f"MILP durumu: {sonuc.durum}")

    if sonuc.plan:
        rapor = dogrula(user, sonuc.plan, df, mevsim="yaz")
        rapor.ozet()
