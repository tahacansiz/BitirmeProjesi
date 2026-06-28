# Haftalık Yemek Planlama Sistemi

MILP tabanlı, sağlık ve tercih kısıtlarına duyarlı haftalık yemek planlayıcı.

## Bileşenler
- `nutrition_targets.py` — Kullanıcı profilinden günlük besin hedefleri
- `personalization.py` — İçerik-tabanlı + LinUCB tercih skorlama
- `meal_planner.py` — MILP modeli ve çözücü (varsayılan: Gurobi)
- `validate_plan.py` — Üretilen planı bağımsız doğrulama

## Kurulum
```bash
pip install -r requirements.txt
```

## Çalıştırma
```bash
python validate_plan.py
```

## Çözücü Notu
Varsayılan çözücü Gurobi'dir (akademik lisans gerektirir).
Lisansın yoksa `cozucu="HiGHS"` parametresi geçirin.

## Veri
`recipes_normalized.parquet` — 6990 Türkçe tarif, normalize edilmiş besin/sağlık/mevsim/maliyet kolonlarıyla.
`1780649928977_Tarifler.csv` — Ham veri kaynağı.
