"""
meal_planner.py
===============
Haftalık yemek planı üreten MILP optimizatörü (PuLP/CBC tabanlı).

Akış:
1. Tarifleri slot havuzlarına böl (kahvaltı, ana, yan, ara öğün)
2. Hard sağlık kurallarını ön-filtre olarak uygula
3. MILP'i kur: değişkenler, kısıtlar, amaç fonksiyonu
4. Çöz ve haftalık planı çıkar
"""

from dataclasses import dataclass, field
from pathlib import Path
import pandas as pd
import pulp

from nutrition_targets import UserProfile, DailyTargets, hesapla_hedefler


# ============================================================
# YAPILANDIRMA
# ============================================================

# Slot tanımları: zorunlu/opsiyonel + kcal alt/üst sınır (porsiyon tutarsızlıklarını eler)
SLOT_CONFIG = {
    "kahvalti":  {"zorunlu": True,  "kcal_min": 150, "kcal_max": 700},
    "ogle_ana":  {"zorunlu": True,  "kcal_min": 250, "kcal_max": 850},
    "ogle_yan":  {"zorunlu": False, "kcal_min": 40,  "kcal_max": 300},
    "aksam_ana": {"zorunlu": True,  "kcal_min": 250, "kcal_max": 850},
    "aksam_yan": {"zorunlu": False, "kcal_min": 40,  "kcal_max": 300},
    "ara_ogun":  {"zorunlu": True,  "kcal_min": 50,  "kcal_max": 250},
}

OPSIYONEL_SLOTLAR = [s for s, cfg in SLOT_CONFIG.items() if not cfg["zorunlu"]]


# Yüksek kalori hedefinde slot tavanlarını ölçeklemek için.
# Referans ~2400 kcal; bunun üstündeki hedeflerde porsiyon tavanı büyür.
# Slot tavanları toplamı 3250 kcal → ölçeksiz ~3250'nin üstü infeasible olur.
KCAL_OLCEK_REFERANS = 2400


def kcal_olcek_hesapla(hedef_kalori: float) -> float:
    """Hedef kaloriye göre slot tavan ölçeği (sadece yukarı, ≥1.0)."""
    return max(1.0, hedef_kalori / KCAL_OLCEK_REFERANS)

# Kategori -> slot eşlemesi
KAHVALTI_CATS = ["Kahvaltılık", "Tost", "Sandviç", "Poğaça", "Çörek"]
ANA_CATS = ["Sebze", "Tavuk", "Et", "Makarna", "Köfte", "Pilav", "Balık",
            "Bakliyat", "Mantı", "Deniz Ürünleri", "Sakatat", "Kebap",
            "Sulu Yemek", "Hamburger", "Zeytinyağlı", "Dolma Sarma",
            "Kızartma", "Pizza", "Pide", "Börek"]
YAN_CATS = ["Çorba", "Ekmek", "Meze", "Salata"]
ARA_OGUN_CATS = ["Tuzlu Atıştırmalık", "Atıştırmalık", "Tatlı Atıştırmalık",
                 "Meyveli Tatlı", "Tatlı Kek", "Tatlı Kurabiye", "Tatlı",
                 "Kek", "Kurabiye", "Sütlü Tatlı", "Diyet Tatlı"]

# Hard sağlık kuralları: aday havuzundan ÖN-FİLTRE olarak çıkarılır
HARD_HEALTH_RULES = {
    "celiac":              ("eq", 1),
    "lactose_intolerance": ("eq", 1),
    "kidney_disease":      ("ge", 0.7),
    "liver_disease":       ("ge", 0.7),
}

# Soft sağlık kuralları: HAFTALIK ORTALAMA olarak MILP kısıtı
SOFT_HEALTH_RULES = {
    "diabetes":               0.6,
    "hypertension":           0.6,
    "obesity":                0.5,
    "cardiovascular_disease": 0.6,
    "anemia":                 0.5,
    "pregnancy":              0.5,
}

# Fiyat tercihi -> haftalık ortalama maliyet_norm üst sınır
FIYAT_LIMITS = {"ucuz": 0.35, "orta": 0.60, "pahali": None}

# Amaç fonksiyonu ağırlıkları (başlangıç sezgisel)
ALPHA = 1.0   # soft sağlık skoru ağırlığı
BETA  = 0.3   # tamlık bonusu (opsiyonel slot doldurulması)
GAMMA = 0.5   # maliyet penaltısı
DELTA = 0.05  # lif ödülü (her ekstra g lif için)
EPSILON = 2.0 # kişisel tercih skoru ağırlığı (cold start'ta etkisiz)

# Çeşitlilik: aynı tarif haftada en fazla kaç kez (slot tipine göre)
# Ana yemekler tekrar etmesin (1); kahvaltı/yan/ara tekrar edebilir (2).
MAX_AYNI_TARIF = 2  # genel varsayılan (geriye dönük uyumluluk)
SLOT_CESITLILIK = {
    "kahvalti": 2,
    "ogle_ana": 1,
    "ogle_yan": 2,
    "aksam_ana": 1,
    "aksam_yan": 2,
    "ara_ogun": 2,
}


# ============================================================
# 1. HAVUZ HAZIRLAMA
# ============================================================

def slot_havuzlari(
    df: pd.DataFrame,
    kcal_olcek: float = 1.0,
) -> dict[str, pd.DataFrame]:
    """Veri setini slot havuzlarına böler.

    - Kategoriye göre temel havuzlar kurulur.
    - Her slota per-slot kcal aralığı uygulanır (kcal_olcek ile ölçeklenir).

    Not: Eski "Hamur İşi" kategorisi veri hazırlığında gerçek kategorilere
    (Kahvaltılık / Tatlı / Mantı / Pide) yeniden atandığından, ayrı bir
    override mekanizmasına gerek kalmamıştır.
    """
    # Kategoriye göre slot havuzları
    kahvalti  = df[df["category"].isin(KAHVALTI_CATS)]
    ana       = df[df["category"].isin(ANA_CATS)]
    yan       = df[df["category"].isin(YAN_CATS)]
    ara_ogun  = df[df["category"].isin(ARA_OGUN_CATS)]

    raw = {
        "kahvalti":  kahvalti,
        "ogle_ana":  ana,
        "ogle_yan":  yan,
        "aksam_ana": ana,
        "aksam_yan": yan,
        "ara_ogun":  ara_ogun,
    }
    out = {}
    for slot, pool in raw.items():
        cfg = SLOT_CONFIG[slot]
        # Yüksek kalori hedefinde üst tavanı ölçekle (büyük porsiyonlar için).
        # Alt sınır sabit kalır (küçük/atıştırmalık dengesini korur).
        ust = cfg["kcal_max"] * kcal_olcek
        out[slot] = pool[
            (pool["calories_pp"] >= cfg["kcal_min"]) &
            (pool["calories_pp"] <= ust)
        ].reset_index(drop=True)
    return out


def hard_filtre_uygula(
    havuzlar: dict[str, pd.DataFrame],
    user: UserProfile
) -> dict[str, pd.DataFrame]:
    """Hard sağlık kurallarına göre havuzları daraltır."""
    filtreli = {}
    for slot, pool in havuzlar.items():
        out = pool
        for kosul in user.saglik_kosullari:
            if kosul not in HARD_HEALTH_RULES:
                continue
            op, val = HARD_HEALTH_RULES[kosul]
            if op == "eq":
                out = out[out[kosul] == val]
            elif op == "ge":
                out = out[out[kosul] >= val]
        filtreli[slot] = out.reset_index(drop=True)
    return filtreli


# Ay -> mevsim eşlemesi (Kuzey Yarımküre / Türkiye)
AY_MEVSIM = {3: "ilkbahar", 4: "ilkbahar", 5: "ilkbahar",
             6: "yaz", 7: "yaz", 8: "yaz",
             9: "sonbahar", 10: "sonbahar", 11: "sonbahar",
             12: "kış", 1: "kış", 2: "kış"}

MEVSIM_KOLONLARI = {"ilkbahar", "yaz", "sonbahar", "kış"}


def mevcut_mevsim(tarih=None) -> str:
    """Verilen tarihten (yoksa bugünden) mevsimi döndürür."""
    import datetime
    if tarih is None:
        tarih = datetime.date.today()
    return AY_MEVSIM[tarih.month]


def mevsim_filtrele(df: pd.DataFrame, mevsim: str) -> pd.DataFrame:
    """Sadece verilen mevsimde uygun tarifleri tutar."""
    if mevsim not in MEVSIM_KOLONLARI:
        raise ValueError(f"Geçersiz mevsim: {mevsim}. "
                         f"Seçenekler: {MEVSIM_KOLONLARI}")
    return df[df[mevsim] == 1].reset_index(drop=True)


# ============================================================
# 2. MILP KURULUMU
# ============================================================

@dataclass
class PlanSonuc:
    """MILP çıktısı."""
    durum: str               # 'Optimal', 'Infeasible', vs.
    amac_degeri: float | None
    plan: list[dict] = field(default_factory=list)  # 7 günlük plan
    metrikler: dict = field(default_factory=dict)


def milp_kur_ve_coz(
    user: UserProfile,
    df_tarifler: pd.DataFrame,
    verbose: bool = False,
    havuz_orneklem: int | None = None,
    seed: int = 42,
    cozucu: str = "GUROBI",   # "HiGHS", "GUROBI", veya "CBC"
    mevsim: str | None = None,   # None → bugünün mevsimi otomatik
    tercih_skorlari: dict | None = None,  # {recipe_id: skor}; None → cold start
) -> PlanSonuc:
    """Kullanıcı + veri setiyle haftalık MILP'i kurar ve çözer.
                    
    """

    targets = hesapla_hedefler(user)

    # Mevsim filtresi (bugünün mevsimi veya elle verilen)
    if mevsim is None:
        mevsim = mevcut_mevsim()
    df_mevsim = mevsim_filtrele(df_tarifler, mevsim)
    if verbose:
        print(f"Mevsim: {mevsim}  →  {len(df_mevsim)}/{len(df_tarifler)} tarif uygun")

    havuzlar = slot_havuzlari(df_mevsim, kcal_olcek=kcal_olcek_hesapla(targets.kalori))
    havuzlar = hard_filtre_uygula(havuzlar, user)

    # Performans için havuzları örnekle
    if havuz_orneklem is not None:
        import random
        random.seed(seed)
        for slot in havuzlar:
            pool = havuzlar[slot]
            if len(pool) > havuz_orneklem:
                havuzlar[slot] = pool.sample(
                    n=havuz_orneklem, random_state=seed
                ).reset_index(drop=True)

    if verbose:
        print("Filtrelenmiş + örneklenmiş havuz boyutları:")
        for s, p in havuzlar.items():
            print(f"  {s:12s}: {len(p):4d}")

    days = range(7)
    prob = pulp.LpProblem("HaftalikPlan", pulp.LpMaximize)

    # ---------- Karar değişkenleri ----------
    # x[(d, slot, idx)] = bu tarif o gün o slotta seçildi mi?
    x = {}
    for d in days:
        for slot, pool in havuzlar.items():
            for idx in pool.index:
                x[(d, slot, idx)] = pulp.LpVariable(
                    f"x_{d}_{slot}_{idx}", cat=pulp.LpBinary
                )

    if verbose:
        print(f"Toplam ikili değişken: {len(x)}")

    # ---------- Yardımcı: bir günün toplamı (besin kolonu) ----------
    def gunluk_toplam(d, col):
        return pulp.lpSum(
            x[(d, slot, idx)] * havuzlar[slot].loc[idx, col]
            for slot in havuzlar
            for idx in havuzlar[slot].index
        )

    # ---------- Slot ataması ----------
    for d in days:
        for slot, cfg in SLOT_CONFIG.items():
            slot_sum = pulp.lpSum(x[(d, slot, idx)]
                                  for idx in havuzlar[slot].index)
            if cfg["zorunlu"]:
                prob += slot_sum == 1, f"slot_{d}_{slot}"
            else:
                prob += slot_sum <= 1, f"slot_{d}_{slot}"

    # ---------- Günlük kalori (±5% bant) ----------
    for d in days:
        kcal = gunluk_toplam(d, "calories_pp")
        prob += kcal >= targets.kalori * 0.95, f"kcal_min_{d}"
        prob += kcal <= targets.kalori * 1.05, f"kcal_max_{d}"

    # ---------- Günlük makrolar ----------
    makro_kisitlari = [
        ("protein_g_pp", targets.protein_g_min, targets.protein_g_max),
        ("fat_g_pp",     targets.fat_g_min,     targets.fat_g_max),
        ("carbs_g_pp",   targets.carbs_g_min,   targets.carbs_g_max),
    ]
    for d in days:
        for col, vmin, vmax in makro_kisitlari:
            total = gunluk_toplam(d, col)
            prob += total >= vmin, f"{col}_min_{d}"
            prob += total <= vmax, f"{col}_max_{d}"

    # ---------- Günlük sodyum, şeker (hard üst sınırlar) ----------
    # Lif hard kısıt DEĞİL — dataset'ten her gün karşılanması güç.
    # Amaç fonksiyonunda ödül olarak yer alır.
    # ---------- Günlük sodyum, şeker (hard üst sınırlar) ----------
    for d in days:
        prob += gunluk_toplam(d, "sodium_mg_pp") <= targets.sodium_mg_max, f"sodium_{d}"
        prob += gunluk_toplam(d, "sugar_g_pp")   <= targets.sugar_g_max,   f"sugar_{d}"
       # ---------- Gelişmiş Glisemik Vekil Skor Günlük Taban Kısıtı ----------
        if "diabetes" in user.saglik_kosullari:
            for slot in havuzlar:
                # Kısıt çakışmasını önlemek için isimlendirmeyi kısa tutuyoruz (Örn: gi_d0_kahvalti)
                slot_safe_name = slot.replace("ı", "i").replace("ğ", "g").replace("ş", "s").replace("o", "o").replace("ü", "u")
                
                prob += pulp.lpSum(
                    x[(d, slot, idx)] * havuzlar[slot].loc[idx, "diabetes"]
                    for idx in havuzlar[slot].index
                ) >= 0.70 * pulp.lpSum(x[(d, slot, idx)] for idx in havuzlar[slot].index), f"gi_d{d}_{slot_safe_name}"

                # ---------- YENİ: Mutlak karbonhidrat tavanı (öğün başına) ----------
                # Yüksek nişasta yükünü engelle: diyabet hastasında her öğün ≤ 50g karb.
                for idx in havuzlar[slot].index:
                    if havuzlar[slot].loc[idx, "carbs_g_pp"] > 50:
                        prob += x[(d, slot, idx)] == 0, \
                            f"max_carbs_d{d}_{slot_safe_name}_{idx}"

    # ---------- Çeşitlilik: aynı recipe_id haftada ≤ MAX_AYNI_TARIF ----------
    # Aynı tarif birden fazla slotta görünebilir (örn. enginar-salatası
    # hem öğle_yan hem akşam_yan'da). Tüm kullanımı toplam sayarız.
    # Performans: recipe_id -> [(slot, idx), ...] eşlemesi önceden hazırla.
    rid_konumlari: dict[str, list] = {}
    for slot, pool in havuzlar.items():
        for idx in pool.index:
            rid = pool.loc[idx, "recipe_id"]
            rid_konumlari.setdefault(rid, []).append((slot, idx))

    for i, (rid, konumlar) in enumerate(rid_konumlari.items()):
        toplam_kullanim = pulp.lpSum(
            x[(d, slot, idx)]
            for d in days
            for slot, idx in konumlar
        )
        # Tarifin göründüğü slotların en katı sınırı (ana yemekse 1)
        cap = min(SLOT_CESITLILIK[slot] for slot, _ in konumlar)
        prob += toplam_kullanim <= cap, f"variety_{i}"

    # ---------- Soft sağlık (haftalık ortalama ≥ eşik) ----------
    # avg = sum(x*score) / sum(x) >= t  →  sum(x*score) >= t * sum(x)
    soft_kosullar = [k for k in user.saglik_kosullari if k in SOFT_HEALTH_RULES]
    for kosul in soft_kosullar:
        t = SOFT_HEALTH_RULES[kosul]
        skor_top = pulp.lpSum(
            x[(d, slot, idx)] * havuzlar[slot].loc[idx, kosul]
            for d in days for slot in havuzlar for idx in havuzlar[slot].index
        )
        secim_top = pulp.lpSum(
            x[(d, slot, idx)]
            for d in days for slot in havuzlar for idx in havuzlar[slot].index
        )
        prob += skor_top >= t * secim_top, f"soft_{kosul}"

    # ---------- Fiyat tercihi (haftalık ortalama) ----------
    if FIYAT_LIMITS[user.fiyat_tercihi] is not None:
        limit = FIYAT_LIMITS[user.fiyat_tercihi]
        maliyet_top = pulp.lpSum(
            x[(d, slot, idx)] * havuzlar[slot].loc[idx, "maliyet_norm"]
            for d in days for slot in havuzlar for idx in havuzlar[slot].index
        )
        secim_top = pulp.lpSum(
            x[(d, slot, idx)]
            for d in days for slot in havuzlar for idx in havuzlar[slot].index
        )
        prob += maliyet_top <= limit * secim_top, "fiyat_avg"

    # ---------- AMAÇ FONKSİYONU ----------
    # α × soft_saglik_skoru + β × tamlik_bonusu - γ × maliyet
    soft_amac = pulp.lpSum(
        x[(d, slot, idx)] *
        sum(havuzlar[slot].loc[idx, k] for k in soft_kosullar) /
        max(len(soft_kosullar), 1)
        for d in days for slot in havuzlar for idx in havuzlar[slot].index
    ) if soft_kosullar else 0

    tamlik_amac = pulp.lpSum(
        x[(d, slot, idx)]
        for d in days for slot in OPSIYONEL_SLOTLAR for idx in havuzlar[slot].index
    )

    maliyet_amac = pulp.lpSum(
        x[(d, slot, idx)] * havuzlar[slot].loc[idx, "maliyet_norm"]
        for d in days for slot in havuzlar for idx in havuzlar[slot].index
    )

    lif_amac = pulp.lpSum(
        x[(d, slot, idx)] * havuzlar[slot].loc[idx, "fiber_g_pp"]
        for d in days for slot in havuzlar for idx in havuzlar[slot].index
    )

    # Kişisel tercih skoru (cold start'ta None → terim 0)
    if tercih_skorlari:
        tercih_amac = pulp.lpSum(
            x[(d, slot, idx)] *
            tercih_skorlari.get(havuzlar[slot].loc[idx, "recipe_id"], 0.5)
            for d in days for slot in havuzlar for idx in havuzlar[slot].index
        )
    else:
        tercih_amac = 0

    prob += (ALPHA * soft_amac + BETA * tamlik_amac - GAMMA * maliyet_amac
             + DELTA * lif_amac + EPSILON * tercih_amac)

    # ---------- Çöz ----------
    if verbose:
        print(f"\nMILP çözülüyor ({cozucu})...")

    if cozucu == "HiGHS":
        solver = pulp.HiGHS(msg=verbose, timeLimit=120, gapRel=0.05)
    elif cozucu == "GUROBI":
        solver = pulp.GUROBI(msg=verbose, timeLimit=120, gapRel=0.05)
    else:
        solver = pulp.PULP_CBC_CMD(msg=verbose, timeLimit=300)

    prob.solve(solver)

    durum = pulp.LpStatus[prob.status]
    # Gerçek çözüm var mı? Sadece amaç değeri değil, en az bir değişken
    # gerçekten atanmış mı kontrol et (zorunlu slotlar dolu olmalı).
    atanan_var = any(
        (v.value() or 0) > 0.5 for v in x.values()
    )
    has_solution = atanan_var and prob.objective is not None
    if not has_solution:
        # Çözüm bulunamadı (infeasible ya da zaman aşımı, geçerli çözüm yok)
        return PlanSonuc(
            durum="Infeasible/Çözülemedi" if durum != "Optimal" else durum,
            amac_degeri=None,
        )
    if durum != "Optimal":
        durum = "Feasible (gap toleransı içinde)"

    # ---------- Çözümü topla ----------
    plan = []
    for d in days:
        gun = {"gun": d + 1, "ogunler": {}}
        for slot in SLOT_CONFIG:
            pool = havuzlar[slot]
            secilen = None
            for idx in pool.index:
                if x[(d, slot, idx)].value() and x[(d, slot, idx)].value() > 0.5:
                    secilen = pool.loc[idx]
                    break
            if secilen is not None:
                gun["ogunler"][slot] = {
                    "recipe_id": secilen["recipe_id"],
                    "kategori":  secilen["category"],
                    "kcal":      float(secilen["calories_pp"]),
                    "protein":   float(secilen["protein_g_pp"]),
                    "maliyet":   float(secilen["maliyet_norm"]),
                }
            else:
                gun["ogunler"][slot] = None
        plan.append(gun)

    # ---------- Metrikler ----------
    metrikler = {"toplam_kcal_gunluk": [], "toplam_protein_gunluk": []}
    for gun in plan:
        kcal = sum(o["kcal"] for o in gun["ogunler"].values() if o)
        prot = sum(o["protein"] for o in gun["ogunler"].values() if o)
        metrikler["toplam_kcal_gunluk"].append(round(kcal, 1))
        metrikler["toplam_protein_gunluk"].append(round(prot, 1))

    return PlanSonuc(
        durum=durum,
        amac_degeri=pulp.value(prob.objective),
        plan=plan,
        metrikler=metrikler,
    )


def oneri_alternatifleri(
    user: UserProfile,
    plan: list[dict],
    gun_no: int,
    slot: str,
    df: pd.DataFrame,
    tercih_skorlari: dict | None = None,
    mevsim: str | None = None,
    n: int = 3,
) -> list[dict]:
    """Bir öğünü değiştirmek için, günü dengede tutan N alternatif döndürür.

    'Öğünü değiştir' UI'sının ihtiyaç duyduğu fonksiyon. Aday tarifler:
    - O slotun havuzunda (mevsim + sağlık filtreli)
    - Günün geri kalanıyla birlikte kalori/makro/sodyum/şeker bandında tutar
    - Çeşitlilik sınırını aşmaz, reddedilen tarif değildir
    - Tercih skoruna göre sıralanır
    """
    from collections import Counter

    targets = hesapla_hedefler(user)
    if mevsim is None:
        mevsim = mevcut_mevsim()

    df_mevsim = mevsim_filtrele(df, mevsim)
    havuzlar = hard_filtre_uygula(
        slot_havuzlari(df_mevsim, kcal_olcek=kcal_olcek_hesapla(targets.kalori)), user)
    pool = havuzlar[slot]

    df_idx = df.set_index("recipe_id")
    def besin(rid, kol):
        return float(df_idx.loc[rid, kol])

    gun = next(g for g in plan if g["gun"] == gun_no)
    mevcut = gun["ogunler"].get(slot)
    reddedilen = mevcut["recipe_id"] if mevcut else None

    # Günün geri kalanının (değişen slot hariç) besin toplamı
    kolonlar = ["calories_pp", "protein_g_pp", "fat_g_pp",
                "carbs_g_pp", "sodium_mg_pp", "sugar_g_pp"]
    kalan = {k: 0.0 for k in kolonlar}
    for s, o in gun["ogunler"].items():
        if s == slot or o is None:
            continue
        for k in kolonlar:
            kalan[k] += besin(o["recipe_id"], k)

    # Alternatifin sığması gereken pencere
    pencere = {
        "calories_pp": (targets.kalori * 0.95 - kalan["calories_pp"],
                        targets.kalori * 1.05 - kalan["calories_pp"]),
        "protein_g_pp": (targets.protein_g_min - kalan["protein_g_pp"],
                         targets.protein_g_max - kalan["protein_g_pp"]),
        "fat_g_pp": (targets.fat_g_min - kalan["fat_g_pp"],
                     targets.fat_g_max - kalan["fat_g_pp"]),
        "carbs_g_pp": (targets.carbs_g_min - kalan["carbs_g_pp"],
                       targets.carbs_g_max - kalan["carbs_g_pp"]),
    }
    sodyum_max = targets.sodium_mg_max - kalan["sodium_mg_pp"]
    seker_max = targets.sugar_g_max - kalan["sugar_g_pp"]

    # Haftalık çeşitlilik sayımı (reddedileni düşerek)
    sayim = Counter(o["recipe_id"] for g in plan
                    for o in g["ogunler"].values() if o)
    if reddedilen:
        sayim[reddedilen] -= 1

    adaylar = []
    tol = 1e-6
    slot_cap = SLOT_CESITLILIK.get(slot, MAX_AYNI_TARIF)
    for idx in pool.index:
        rid = pool.loc[idx, "recipe_id"]
        if rid == reddedilen:
            continue
        if sayim.get(rid, 0) >= slot_cap:
            continue
        uygun = True
        for k, (lo, hi) in pencere.items():
            v = pool.loc[idx, k]
            if not (lo - tol <= v <= hi + tol):
                uygun = False
                break
        if not uygun:
            continue
        if pool.loc[idx, "sodium_mg_pp"] > sodyum_max + tol:
            continue
        if pool.loc[idx, "sugar_g_pp"] > seker_max + tol:
            continue
        if "diabetes" in user.saglik_kosullari:
            # Önerilecek alternatif tarifin glisemik indeks skoru 0.70'ten düşükse (yani riskliyse) pas geç
            if pool.loc[idx, "diabetes"] < 0.70:
                continue
            if pool.loc[idx, "carbs_g_pp"] > 50:
                continue
        skor = (tercih_skorlari or {}).get(rid, 0.5)
        adaylar.append({
            "recipe_id": rid,
            "kategori": pool.loc[idx, "category"],
            "kcal": float(pool.loc[idx, "calories_pp"]),
            "tercih_skoru": float(skor),
        })

    adaylar.sort(key=lambda a: -a["tercih_skoru"])
    return adaylar[:n]


# ============================================================
# DEMO
# ============================================================

def _yazdir_plan(sonuc: PlanSonuc, targets: DailyTargets):
    print(f"\n{'='*72}")
    if sonuc.amac_degeri is None:
        print(f"DURUM: {sonuc.durum} (çözüm bulunamadı)")
        return
    print(f"DURUM: {sonuc.durum}    AMAÇ DEĞERİ: {sonuc.amac_degeri:.3f}")
    print(f"Günlük kalori hedefi: {targets.kalori:.0f} kcal "
          f"(bant: {targets.kalori*0.95:.0f}-{targets.kalori*1.05:.0f})")
    print('='*72)

    for gun in sonuc.plan:
        print(f"\n— GÜN {gun['gun']} —")
        for slot, o in gun["ogunler"].items():
            if o:
                print(f"  {slot:11s}: {o['recipe_id'][:45]:45s} "
                      f"| {o['kcal']:5.0f} kcal | {o['kategori']}")
            else:
                print(f"  {slot:11s}: -- (opsiyonel, boş)")
        kcal = sonuc.metrikler['toplam_kcal_gunluk'][gun['gun']-1]
        prot = sonuc.metrikler['toplam_protein_gunluk'][gun['gun']-1]
        print(f"  TOPLAM: {kcal:.0f} kcal | {prot:.0f} g protein")


if __name__ == "__main__":
    # Normalize edilmiş veri varsa onu kullan, yoksa ham xlsx'ten oku
    norm_path = Path(__file__).parent / "recipes_normalized.parquet"
    if norm_path.exists():
        df = pd.read_parquet(norm_path)
        print(f"Yüklendi (normalize): {len(df)} tarif")
    else:
        df = pd.read_excel("/mnt/user-data/uploads/Final_Veri_Seti_Gu_ncel.xlsx")
        nutrient_cols = ["calories_pp", "protein_g_pp", "fat_g_pp", "carbs_g_pp",
                         "fiber_g_pp", "sugar_g_pp", "sodium_mg_pp",
                         "calcium_mg_pp", "iron_mg_pp", "potassium_mg_pp"]
        df = df.dropna(subset=nutrient_cols).reset_index(drop=True)
        print(f"Yüklendi (ham): {len(df)} tarif — normalize için normalize_data.py çalıştırın")

    user = UserProfile(
        yas=30, cinsiyet="erkek", boy_cm=178, kilo_kg=75,
        aktivite="orta", fiyat_tercihi="orta",
    )
    targets = hesapla_hedefler(user)
    print(f"\nKullanıcı hedefi: {targets.kalori:.0f} kcal/gün")

    sonuc = milp_kur_ve_coz(user, df, verbose=True)
    _yazdir_plan(sonuc, targets)
