"""
nutrition_targets.py
====================
Kullanıcı profilinden günlük kalori, makro ve mikro besin hedeflerini hesaplar.
Bu modülün çıktısı MILP'in günlük kısıt değerleri olarak kullanılır.

Temel yöntem:
- BMR: Mifflin-St Jeor formülü
- TDEE: BMR × aktivite faktörü
- Hedef kalori: TDEE + (kilo hedefine göre düzenleme)
- Makro/mikro: Genel beslenme rehberleri + hastalığa özel ayarlamalar

NOT: Bu modüldeki hastalığa özel ayarlamalar genel klinik rehberlere dayanır
(ADA, AHA, KDIGO, WHO). Bireysel hastalar için diyetisyen onayı şarttır.
"""

from dataclasses import dataclass, field
from typing import Literal


# ============================================================
# SABİTLER
# ============================================================

# Aktivite faktörleri (TDEE = BMR × bu faktör)
ACTIVITY_MULTIPLIERS = {
    "sedanter": 1.2,    # ofis işi, çok az/hiç egzersiz
    "hafif":    1.375,  # haftada 1-3 gün hafif egzersiz
    "orta":     1.55,   # haftada 3-5 gün orta yoğunluk
    "yogun":    1.725,  # haftada 6-7 gün yoğun egzersiz
}

# Kilo hedefi düzenlemesi (kcal/gün)
WEIGHT_GOAL_ADJUSTMENT = {
    "verme":  -500,  # ~0.45 kg/hafta kayıp
    "koruma":    0,
    "alma":   +400,  # kontrollü kilo alma
}

# Güvenli günlük kalori alt sınırı (sağlık otoriteleri kabul değeri)
# Bu değerin altına inilirse besin yetersizliği ve metabolik yavaşlama riski.
GUVENLI_KALORI_TABANI = {"kadin": 1200, "erkek": 1500}


# ============================================================
# VERİ YAPILARI
# ============================================================

@dataclass
class UserProfile:
    """MILP'e giren kullanıcı profili."""

    # Demografi (zorunlu)
    yas: int                                                  # yıl
    cinsiyet: Literal["erkek", "kadin"]
    boy_cm: float
    kilo_kg: float

    # Aktivite ve hedef
    aktivite: Literal["sedanter", "hafif", "orta", "yogun"] = "orta"
    kilo_hedefi: Literal["verme", "koruma", "alma"] = "koruma"

    # Sağlık koşulları (veri setindeki kolon adlarıyla aynı)
    # "celiac", "lactose_intolerance", "kidney_disease", "liver_disease",
    # "diabetes", "hypertension", "obesity", "cardiovascular_disease",
    # "anemia", "pregnancy"
    saglik_kosullari: list[str] = field(default_factory=list)

    # Tercihler
    vejetaryen: bool = False
    vegan: bool = False
    fiyat_tercihi: Literal["ucuz", "orta", "pahali"] = "orta"
    # Onboarding'de seçilen yemek türü grupları (kişiselleştirme başlangıcı)
    onboarding_gruplari: list[str] = field(default_factory=list)


@dataclass
class DailyTargets:
    """MILP'in günlük kısıtlarına dönüşecek hedef değerler."""

    # Enerji
    kalori: float                       # kcal

    # Makrolar — bant aralığı (g)
    protein_g_min: float
    protein_g_max: float
    fat_g_min: float
    fat_g_max: float
    carbs_g_min: float
    carbs_g_max: float

    # Diğer makrolar
    fiber_g_min: float
    sugar_g_max: float
    sodium_mg_max: float

    # Mikrolar
    calcium_mg_min: float
    iron_mg_min: float
    potassium_mg_min: float

    # Bilgi alanları (raporlamada gösterilir)
    bmr: float
    tdee: float
    notlar: list[str] = field(default_factory=list)


# ============================================================
# HESAPLAMA FONKSİYONLARI
# ============================================================

def hesapla_bmr(p: UserProfile) -> float:
    """Mifflin-St Jeor formülü.

    Erkek: 10×kilo + 6.25×boy - 5×yas + 5
    Kadın: 10×kilo + 6.25×boy - 5×yas - 161
    """
    base = 10 * p.kilo_kg + 6.25 * p.boy_cm - 5 * p.yas
    return base + 5 if p.cinsiyet == "erkek" else base - 161


def hesapla_tdee(p: UserProfile) -> float:
    """TDEE = BMR × aktivite çarpanı."""
    return hesapla_bmr(p) * ACTIVITY_MULTIPLIERS[p.aktivite]


def hesapla_hedefler(p: UserProfile) -> DailyTargets:
    """Profilden günlük hedefleri üretir."""

    bmr = hesapla_bmr(p)
    tdee = hesapla_tdee(p)
    kalori = tdee + WEIGHT_GOAL_ADJUSTMENT[p.kilo_hedefi]

    kosullar = set(p.saglik_kosullari)
    notlar: list[str] = []

    # -------------------- GÜVENLİK TABANI --------------------
    # Kilo verme açığı, güvenli alt sınırın altına itmemeli.
    taban = GUVENLI_KALORI_TABANI[p.cinsiyet]
    if kalori < taban:
        notlar.append(
            f"Hesaplanan hedef ({kalori:.0f} kcal) güvenli alt sınırın "
            f"altındaydı; {taban} kcal'e yükseltildi. Daha hızlı kilo "
            f"kaybı için diyetisyen/doktor gözetimi gerekir."
        )
        kalori = taban

    # -------------------- PROTEİN --------------------
    # Genel: sedanter 1.0, aktif 1.4-2.0, yaşlı 1.2-1.6 g/kg
    # Hastalığa özel: KBH'da kısıtlı (0.6-0.8 g/kg)
    if "kidney_disease" in kosullar:
        protein_g_min = 0.6 * p.kilo_kg
        protein_g_max = 0.8 * p.kilo_kg
        notlar.append("Böbrek hastalığı: protein 0.6-0.8 g/kg ile kısıtlandı")
    elif p.yas >= 65:
        protein_g_min = 1.0 * p.kilo_kg
        protein_g_max = 1.4 * p.kilo_kg
    elif p.aktivite in ("orta", "yogun"):
        protein_g_min = 1.0 * p.kilo_kg
        protein_g_max = 1.6 * p.kilo_kg
    else:
        protein_g_min = 0.8 * p.kilo_kg
        protein_g_max = 1.2 * p.kilo_kg

    if "pregnancy" in kosullar:
        protein_g_min += 25
        protein_g_max += 25
        kalori += 350
        notlar.append("Gebelik: +350 kcal, +25 g protein eklendi")

    # -------------------- YAĞ --------------------
    # Genel: kalorinin %25-35'i
    # Hastalığa özel: KVH/karaciğer'de düşürülür (%20-25)
    if "cardiovascular_disease" in kosullar or "liver_disease" in kosullar:
        fat_pct_min, fat_pct_max = 0.20, 0.25
        notlar.append("KVH/karaciğer: yağ oranı %20-25 ile kısıtlandı")
    else:
        fat_pct_min, fat_pct_max = 0.25, 0.35
    fat_g_min = (kalori * fat_pct_min) / 9
    fat_g_max = (kalori * fat_pct_max) / 9

    # -------------------- KARBONHİDRAT --------------------
    # Genel: kalorinin %45-55'i
    # Hastalığa özel: diyabet'te düşürülür (%40-45)
    if "diabetes" in kosullar:
        carbs_pct_min, carbs_pct_max = 0.40, 0.45
        notlar.append("Diyabet: karbonhidrat %40-45 ile kısıtlandı")
    else:
        carbs_pct_min, carbs_pct_max = 0.45, 0.55
    carbs_g_min = (kalori * carbs_pct_min) / 4
    carbs_g_max = (kalori * carbs_pct_max) / 4

    # -------------------- LİF --------------------
    # AHA: 14 g / 1000 kcal, minimum 25 g
    fiber_g_min = max(25, 14 * kalori / 1000)

    # -------------------- ŞEKER --------------------
    # WHO: kalorinin %10'undan az; diyabet/obezite'de daha sıkı
    if "diabetes" in kosullar or "obesity" in kosullar:
        sugar_g_max = 25
    else:
        sugar_g_max = 50

    # -------------------- SODYUM --------------------
    # Genel: 2300 mg; hipertansiyon/böbrek'te DASH önerisi 1500 mg
    if "hypertension" in kosullar or "kidney_disease" in kosullar:
        sodium_mg_max = 1500
    else:
        sodium_mg_max = 2300

    # -------------------- KALSİYUM --------------------
    # 50+ kadın için artırılır (osteoporoz önleme)
    if p.yas >= 50 and p.cinsiyet == "kadin":
        calcium_mg_min = 1200
    else:
        calcium_mg_min = 1000

    # -------------------- DEMİR --------------------
    # Üreme yaşındaki kadında yüksek, anemi/gebelik'te daha yüksek
    if "pregnancy" in kosullar:
        iron_mg_min = 27
    elif "anemia" in kosullar:
        iron_mg_min = 18 if p.cinsiyet == "kadin" else 12
        notlar.append("Anemi: demir hedefi artırıldı")
    elif p.cinsiyet == "kadin" and 19 <= p.yas <= 50:
        iron_mg_min = 18
    else:
        iron_mg_min = 8

    # -------------------- POTASYUM --------------------
    # AHA: 3500 mg; hipertansiyon'da 4700 mg (DASH)
    # NOT: KBH'da potasyum YÜKSEK olamaz, ama bu modül min hedef için.
    # MILP'te kidney_disease varsa ayrıca üst sınır da koymak gerek.
    if "kidney_disease" in kosullar:
        potassium_mg_min = 2000   # düşük tutmak için min düşük
        notlar.append("Böbrek: potasyum üst sınırı MILP'te ayrıca kısıtlanmalı")
    elif "hypertension" in kosullar:
        potassium_mg_min = 4700
    else:
        potassium_mg_min = 3500

    return DailyTargets(
        kalori=kalori,
        protein_g_min=protein_g_min, protein_g_max=protein_g_max,
        fat_g_min=fat_g_min,         fat_g_max=fat_g_max,
        carbs_g_min=carbs_g_min,     carbs_g_max=carbs_g_max,
        fiber_g_min=fiber_g_min,
        sugar_g_max=sugar_g_max,
        sodium_mg_max=sodium_mg_max,
        calcium_mg_min=calcium_mg_min,
        iron_mg_min=iron_mg_min,
        potassium_mg_min=potassium_mg_min,
        bmr=bmr, tdee=tdee, notlar=notlar,
    )


# ============================================================
# DEMO
# ============================================================

def _print_hedefler(p: UserProfile, h: DailyTargets) -> None:
    print(f"\n{'='*64}")
    print(f"{p.cinsiyet.upper()}, {p.yas} yaş, {p.kilo_kg:.0f} kg, {p.boy_cm:.0f} cm")
    print(f"Aktivite: {p.aktivite}  |  Hedef: {p.kilo_hedefi}")
    print(f"Sağlık: {', '.join(p.saglik_kosullari) or 'yok'}")
    print(f"{'-'*64}")
    print(f"BMR: {h.bmr:6.0f} kcal   TDEE: {h.tdee:6.0f} kcal   Hedef: {h.kalori:6.0f} kcal")
    print(f"Protein:    {h.protein_g_min:5.0f} - {h.protein_g_max:5.0f} g")
    print(f"Yağ:        {h.fat_g_min:5.0f} - {h.fat_g_max:5.0f} g")
    print(f"Karbonhdt:  {h.carbs_g_min:5.0f} - {h.carbs_g_max:5.0f} g")
    print(f"Lif:       ≥{h.fiber_g_min:5.0f} g    Şeker: ≤{h.sugar_g_max:.0f} g")
    print(f"Sodyum:    ≤{h.sodium_mg_max:5.0f} mg  Kalsiyum: ≥{h.calcium_mg_min:.0f} mg")
    print(f"Demir:     ≥{h.iron_mg_min:5.0f} mg   Potasyum: ≥{h.potassium_mg_min:.0f} mg")
    if h.notlar:
        print(f"\nNotlar:")
        for n in h.notlar:
            print(f"  • {n}")


if __name__ == "__main__":
    ornekler = [
        # Sağlıklı genç erkek
        UserProfile(yas=28, cinsiyet="erkek", boy_cm=178, kilo_kg=75,
                    aktivite="orta"),

        # Kilo vermek isteyen, diyabet + hipertansiyon olan kadın
        UserProfile(yas=45, cinsiyet="kadin", boy_cm=165, kilo_kg=78,
                    aktivite="hafif", kilo_hedefi="verme",
                    saglik_kosullari=["diabetes", "hypertension"]),

        # Çölyak + anemi olan genç kadın
        UserProfile(yas=32, cinsiyet="kadin", boy_cm=170, kilo_kg=65,
                    aktivite="orta",
                    saglik_kosullari=["celiac", "anemia"]),

        # Yaşlı, böbrek hastalığı olan erkek
        UserProfile(yas=68, cinsiyet="erkek", boy_cm=172, kilo_kg=80,
                    aktivite="sedanter",
                    saglik_kosullari=["kidney_disease", "hypertension"]),

        # Hamile kadın
        UserProfile(yas=30, cinsiyet="kadin", boy_cm=168, kilo_kg=70,
                    aktivite="hafif",
                    saglik_kosullari=["pregnancy"]),
    ]

    for p in ornekler:
        _print_hedefler(p, hesapla_hedefler(p))
