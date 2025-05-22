import pandas as pd
import pickle

# 1. CSV dosyasını yükle (indirilen dosya)
df = pd.read_csv("../data/top-1m.csv", header=None, names=["rank", "domain"])

# 2. Domain seti oluştur
top_domains = set(df["domain"].str.strip().str.lower())

# 3. .pkl olarak kaydet
with open("../data/known_domains.pkl", "wb") as f:
    pickle.dump(top_domains, f)

print(f"✅ {len(top_domains)} domain kaydedildi: known_domains.pkl")
