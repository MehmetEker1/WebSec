from transformers import BertTokenizer, BertForSequenceClassification, Trainer, TrainingArguments
from datasets import Dataset
import pandas as pd
import os

# 1. Veriyi Yükle ve Tekrarlıları Sil
CSV_PATH = "../data/analyzed_chunks.csv"
assert os.path.exists(CSV_PATH), f"CSV bulunamadı: {CSV_PATH}"

df = pd.read_csv(CSV_PATH)

# Eğer confidence kolonu varsa onu atabilirsin (model eğitimi için gerekmiyor)
if "confidence" in df.columns:
    df = df.drop(columns=["confidence"])

# Chunk bazında tekrarları sil (son label'ı koru)
df = df.drop_duplicates(subset=["chunk"], keep="last")

# DataFrame'i HuggingFace formatına çevir
# Kolon adları "chunk" → "content" olarak değiştiriliyor
df = df.rename(columns={"chunk": "content"})

# Eğer label kolonun string olarak geldiyse int'e çevir
df["label"] = df["label"].astype(int)

ds = Dataset.from_pandas(df)

# 2. Model ve Tokenizer Yükle
MODEL_PATH = "../models/bert-turkish-finetuned"
tokenizer = BertTokenizer.from_pretrained(MODEL_PATH)
model = BertForSequenceClassification.from_pretrained(MODEL_PATH)

# 3. Tokenizer ile encode et
def tokenize(example):
    return tokenizer(example["content"], padding="max_length", truncation=True, max_length=512)

ds_tok = ds.map(tokenize, batched=True)

# 4. Eğitim ayarları
training_args = TrainingArguments(
    output_dir=MODEL_PATH,  # Aynı model klasörüne tekrar yaz
    per_device_train_batch_size=8,
    num_train_epochs=3,
    logging_steps=10,
    save_strategy="no"
)

# 5. Trainer başlat ve eğit
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=ds_tok
)

trainer.train()

# 6. Güncellenmiş modeli kaydet
model.save_pretrained(MODEL_PATH)
tokenizer.save_pretrained(MODEL_PATH)

print(f"✅ Model, tekrarsız {len(df)} veriyle yeniden eğitildi ve güncellendi!")
