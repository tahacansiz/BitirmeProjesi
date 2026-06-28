"""
personalization.py
==================
Aşama 1: İçerik-tabanlı (content-based) tercih skorlama.

Her tarif bir özellik vektörüyle temsil edilir:
  [besin değerleri (norm99) | kategori (one-hot) | maliyet_norm]

Kullanıcı tercih vektörü = beğendiği tariflerin (puan-ağırlıklı) ortalaması.
Tercih skoru = kullanıcı vektörü ile her tarif arasındaki cosine benzerliği.

Cold start: kullanıcının hiç geri bildirimi yoksa nötr skor (0.5) döner —
yani MILP'in tercih terimi etkisiz kalır, sadece sağlık/kalori kısıtları çalışır.

Aşama 2 (sonra): contextual bandits (LinUCB) bu skorun üstüne keşif ekler.
"""

import numpy as np
import pandas as pd


NUTRIENT_NORM_COLS = [
    "calories_pp_norm99", "protein_g_pp_norm99", "fat_g_pp_norm99",
    "carbs_g_pp_norm99", "fiber_g_pp_norm99", "sugar_g_pp_norm99",
    "sodium_mg_pp_norm99", "calcium_mg_pp_norm99", "iron_mg_pp_norm99",
    "potassium_mg_pp_norm99",
]

# Özellik grubu ağırlıkları — kategori one-hot boyut olarak baskın olduğu
# için ağırlıklandırılır, yoksa benzerlik sadece kategoriye indirgenir.
W_BESIN = 1.0
W_KATEGORI = 0.6
W_MALIYET = 0.3


# Onboarding için yemek türü grupları (53 kategori → ~11 anlaşılır grup)
YEMEK_GRUPLARI = {
    "Et yemekleri":      ["Et", "Köfte", "Kebap", "Sakatat", "Hamburger"],
    "Tavuk/Kümes":       ["Tavuk"],
    "Deniz ürünleri":    ["Balık", "Deniz Ürünleri"],
    "Sebze yemekleri":   ["Sebze", "Zeytinyağlı", "Dolma Sarma"],
    "Makarna/Hamur":     ["Makarna", "Mantı", "Pizza", "Pide", "Börek"],
    "Baklagil/Kuru":     ["Bakliyat", "Pilav"],
    "Çorbalar":          ["Çorba"],
    "Salata/Meze":       ["Salata", "Meze"],
    "Tatlılar":          ["Tatlı", "Sütlü Tatlı", "Şerbetli Tatlı", "Kek",
                          "Pasta", "Kurabiye", "Tatlı Kek", "Tatlı Kurabiye",
                          "Meyveli Tatlı", "Çikolatalı Tatlı", "Cheesecake Tarifleri"],
    "Kahvaltılıklar":    ["Kahvaltılık", "Tost", "Sandviç", "Poğaça", "Çörek"],
    "Atıştırmalıklar":   ["Tuzlu Atıştırmalık", "Atıştırmalık", "Tatlı Atıştırmalık"],
}


class ContentBasedScorer:
    """İçerik-tabanlı tercih skorlayıcı."""

    def __init__(self, df: pd.DataFrame):
        self.recipe_ids = df["recipe_id"].values
        self.rid_to_row = {rid: i for i, rid in enumerate(self.recipe_ids)}
        self.kategoriler = df["category"].values
        self.X = self._ozellik_matrisi(df)

    def _ozellik_matrisi(self, df: pd.DataFrame) -> np.ndarray:
        """Tarif özellik matrisini kurar ve satırları birim uzunluğa getirir."""
        # Besin değerleri (zaten 0-1 normalize)
        X_besin = df[NUTRIENT_NORM_COLS].fillna(0).values * W_BESIN

        # Kategori one-hot
        X_kat = pd.get_dummies(df["category"]).values.astype(float) * W_KATEGORI
        self._kategori_kolonlari = pd.get_dummies(df["category"]).columns

        # Maliyet
        X_mal = df[["maliyet_norm"]].fillna(0).values * W_MALIYET

        X = np.hstack([X_besin, X_kat, X_mal])

        # Cosine için satırları birim uzunluğa normalize et
        normlar = np.linalg.norm(X, axis=1, keepdims=True)
        normlar[normlar == 0] = 1.0
        return X / normlar

    def kullanici_vektoru(
        self,
        begenilen_idler: list[str],
        puanlar: list[float] | None = None,
    ) -> np.ndarray | None:
        """Beğenilen tariflerin (puan-ağırlıklı) ortalama vektörü.

        Cold start: liste boşsa None döner.
        puanlar: opsiyonel, her tarif için ağırlık (örn. 1-5 yıldız).
        """
        if not begenilen_idler:
            return None

        satirlar, agirliklar = [], []
        for i, rid in enumerate(begenilen_idler):
            if rid in self.rid_to_row:
                satirlar.append(self.X[self.rid_to_row[rid]])
                agirliklar.append(puanlar[i] if puanlar else 1.0)

        if not satirlar:
            return None

        satirlar = np.array(satirlar)
        agirliklar = np.array(agirliklar).reshape(-1, 1)
        vec = (satirlar * agirliklar).sum(axis=0) / agirliklar.sum()

        # Kullanıcı vektörünü de birim uzunluğa getir
        norm = np.linalg.norm(vec)
        return vec / norm if norm > 0 else vec

    def onboarding_vektoru(self, secilen_gruplar: list[str]) -> np.ndarray | None:
        """Onboarding'de seçilen yemek gruplarından başlangıç tercih vektörü.

        Seçilen grupların kategorilerindeki tüm tariflerin ortalama vektörü.
        (Tek vektör — geriye dönük uyumluluk için. Çoklu zevk için
        onboarding_vektorleri + max-benzerlik kullanılır.)
        """
        if not secilen_gruplar:
            return None
        hedef_kategoriler = set()
        for grup in secilen_gruplar:
            hedef_kategoriler.update(YEMEK_GRUPLARI.get(grup, []))
        satir_idx = [i for i, kat in enumerate(self.kategoriler)
                     if kat in hedef_kategoriler]
        if not satir_idx:
            return None
        vec = self.X[satir_idx].mean(axis=0)
        norm = np.linalg.norm(vec)
        return vec / norm if norm > 0 else vec

    def onboarding_vektorleri(self, secilen_gruplar: list[str]) -> list[np.ndarray]:
        """Her seçilen grup için AYRI bir merkez vektör döndürür.

        Çoklu zevk problemi için: et + deniz ürünü seçen kullanıcıda
        ortalama almak yerine her grubu ayrı prototip olarak tutarız.
        """
        vektorler = []
        for grup in secilen_gruplar:
            kategoriler = YEMEK_GRUPLARI.get(grup, [])
            satir_idx = [i for i, kat in enumerate(self.kategoriler)
                         if kat in kategoriler]
            if not satir_idx:
                continue
            v = self.X[satir_idx].mean(axis=0)
            norm = np.linalg.norm(v)
            vektorler.append(v / norm if norm > 0 else v)
        return vektorler

    def skorla(
        self,
        begenilen_idler: list[str] | None = None,
        puanlar: list[float] | None = None,
        onboarding_gruplari: list[str] | None = None,
    ) -> dict[str, float]:
        """Her tarif için tercih skoru döner (0-1).

        Öncelik sırası:
        1. Beğenilen tarifler varsa onlardan (etkileşim sonrası)
        2. Yoksa onboarding gruplarından (ilk gün)
        3. İkisi de yoksa nötr 0.5 (gerçek cold start)
        """
        uvec = None
        if begenilen_idler:
            uvec = self.kullanici_vektoru(begenilen_idler, puanlar)

        # Onboarding: çoklu-prototip (her grup ayrı merkez, max-benzerlik)
        if uvec is None and onboarding_gruplari:
            vektorler = self.onboarding_vektorleri(onboarding_gruplari)
            if vektorler:
                # Her grup benzerliğini kendi içinde [0,1]'e normalize et
                # (gruplar arası homojenlik farkını dengeler), sonra max al.
                normalize_simler = []
                for v in vektorler:
                    sim = self.X @ v
                    lo, hi = sim.min(), sim.max()
                    if hi > lo:
                        sim = (sim - lo) / (hi - lo)
                    else:
                        sim = np.full_like(sim, 0.5)
                    normalize_simler.append(sim)
                skorlar = np.stack(normalize_simler).max(axis=0)
                return {rid: float(s)
                        for rid, s in zip(self.recipe_ids, skorlar)}

        if uvec is None:
            return {rid: 0.5 for rid in self.recipe_ids}

        benzerlik = self.X @ uvec
        skorlar = (benzerlik + 1.0) / 2.0
        return {rid: float(s) for rid, s in zip(self.recipe_ids, skorlar)}


# ============================================================
# AŞAMA 2: Contextual Bandit (LinUCB)
# ============================================================

# Swap sebep etiketleri -> ödül
# None = sinyal yok (modele yansıtılmaz)
SEBEP_ODUL = {
    "sevmedim":        0.0,    # güçlü negatif: tercih modelini güncelle
    "canim_istemedi":  None,   # anlık ruh hali: sinyal yok
    "yakinda_yedim":   None,   # zamansal: çeşitliliğin işi, tercih değil
}
SECILEN_ODUL = 1.0   # değiştirirken seçilen alternatif: güçlü pozitif
KORUNAN_ODUL = 0.6   # hiç dokunulmayan, planda kalan: hafif pozitif


class LinUCBPersonalizer:
    """Paylaşımlı-parametreli LinUCB contextual bandit.

    Tarif özellik vektörü x için beklenen ödül ≈ θ·x.
    Skor (UCB) = θ·x + α·√(xᵀ A⁻¹ x)  (sömürü + keşif).
    Geri bildirimle A ve b güncellenir; θ = A⁻¹ b.
    """

    def __init__(self, scorer: ContentBasedScorer, alpha: float = 1.0):
        self.scorer = scorer
        self.X = scorer.X
        self.d = self.X.shape[1]
        self.alpha = alpha
        self.A = np.identity(self.d)
        self.b = np.zeros(self.d)
        self._A_inv = np.identity(self.d)
        self._guncel = True

    def _x(self, recipe_id: str) -> np.ndarray | None:
        i = self.scorer.rid_to_row.get(recipe_id)
        return self.X[i] if i is not None else None

    def guncelle(self, recipe_id: str, odul: float):
        """Tek bir geri bildirim gözlemi: A += xxᵀ, b += r·x."""
        x = self._x(recipe_id)
        if x is None:
            return
        self.A += np.outer(x, x)
        self.b += odul * x
        self._guncel = False

    def onboarding_tohumu(self, gruplar: list[str], guc: float = 3.0):
        """Onboarding gruplarını sahte pozitif gözlem olarak ekler.

        guc: tohum gözleminin ağırlığı (kaç gözleme denk sayılsın).
        """
        uvec = self.scorer.onboarding_vektoru(gruplar)
        if uvec is None:
            return
        # Tohum vektörünü 'guc' kadar pozitif gözlem gibi ekle
        self.A += guc * np.outer(uvec, uvec)
        self.b += guc * SECILEN_ODUL * uvec
        self._guncel = False

    def _A_inv_guncelle(self):
        if not self._guncel:
            self._A_inv = np.linalg.inv(self.A)
            self._guncel = True

    def skorla(self) -> dict[str, float]:
        """Tüm tarifler için UCB skoru (0-1'e min-max ölçeklenmiş)."""
        self._A_inv_guncelle()
        theta = self._A_inv @ self.b
        ortalama = self.X @ theta
        # Keşif bonusu: her tarif için √(xᵀ A⁻¹ x)
        bonus = np.sqrt(np.einsum("ij,jk,ik->i", self.X, self._A_inv, self.X))
        ucb = ortalama + self.alpha * bonus
        # MILP'in EPSILON terimi için [0,1]'e ölçekle
        lo, hi = ucb.min(), ucb.max()
        if hi > lo:
            ucb = (ucb - lo) / (hi - lo)
        else:
            ucb = np.full_like(ucb, 0.5)
        return {rid: float(s) for rid, s in zip(self.scorer.recipe_ids, ucb)}


def swap_geri_bildirim(
    bandit: LinUCBPersonalizer,
    reddedilen_id: str,
    sebep: str,
    secilen_id: str | None = None,
):
    """Bir 'öğünü değiştir' etkileşimini bandit'e işler.

    - reddedilen + sebep → sebebe göre ödül (veya sinyal yok)
    - seçilen alternatif → güçlü pozitif
    """
    odul = SEBEP_ODUL.get(sebep)
    if odul is not None:
        bandit.guncelle(reddedilen_id, odul)
    if secilen_id:
        bandit.guncelle(secilen_id, SECILEN_ODUL)


def korunan_geri_bildirim(bandit: LinUCBPersonalizer, korunan_idler: list[str]):
    """Planda kalan (değiştirilmeyen) tarifler → hafif pozitif."""
    for rid in korunan_idler:
        bandit.guncelle(rid, KORUNAN_ODUL)


# ============================================================
# DEMO / TEST: Sentetik kullanıcı ile katmanın adapte olduğunu göster
# ============================================================

if __name__ == "__main__":
    df = pd.read_parquet("recipes_normalized.parquet")
    scorer = ContentBasedScorer(df)

    print("=" * 64)
    print("TEST 1: Cold start (geri bildirim yok)")
    print("=" * 64)
    skorlar = scorer.skorla([])
    benzersiz = set(round(s, 3) for s in skorlar.values())
    print(f"  Tüm skorlar nötr mü? {benzersiz}  (beklenen: {{0.5}})")

    print("\n" + "=" * 64)
    print("TEST 2: Tatlı seven kullanıcı")
    print("=" * 64)
    # Birkaç tatlı tarifi beğenmiş bir kullanıcı simüle et
    tatlilar = df[df["category"].isin(["Tatlı", "Sütlü Tatlı", "Kek"])]["recipe_id"].head(5).tolist()
    print(f"  Beğenilen (tatlı): {tatlilar}")
    skorlar = scorer.skorla(tatlilar)
    # En yüksek skorlu 5 tarifin kategorisi
    en_yuksek = sorted(skorlar.items(), key=lambda x: -x[1])[:8]
    print("  En yüksek skorlu tarifler:")
    for rid, s in en_yuksek:
        kat = df[df["recipe_id"] == rid]["category"].iloc[0]
        print(f"    {s:.3f}  {rid[:40]:40s} [{kat}]")

    print("\n" + "=" * 64)
    print("TEST 3: Et/protein seven kullanıcı")
    print("=" * 64)
    etler = df[df["category"].isin(["Et", "Tavuk", "Köfte", "Kebap"])]["recipe_id"].head(5).tolist()
    print(f"  Beğenilen (et): {etler}")
    skorlar = scorer.skorla(etler)
    en_yuksek = sorted(skorlar.items(), key=lambda x: -x[1])[:8]
    print("  En yüksek skorlu tarifler:")
    for rid, s in en_yuksek:
        kat = df[df["recipe_id"] == rid]["category"].iloc[0]
        print(f"    {s:.3f}  {rid[:40]:40s} [{kat}]")
