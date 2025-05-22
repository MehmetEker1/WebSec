from transformers import BertTokenizer, BertForSequenceClassification, Trainer, TrainingArguments
from datasets import Dataset
import pandas as pd

# 1. Yeni eklenen veri dosyasını yükle (yeni örnekler sadece!)
df_new = pd.read_csv("../data/new_training_data_augmented.csv")

# 2. Hugging Face Dataset formatına çevir
ds_new = Dataset.from_pandas(df_new)

# 3. Mevcut fine-tuned modeli ve tokenizer'ı yükle
MODEL_PATH = "../models/bert-turkish-finetuned"
tokenizer = BertTokenizer.from_pretrained(MODEL_PATH)
model = BertForSequenceClassification.from_pretrained(MODEL_PATH)

# 4. Tokenizer ile yeni veriyi encode et
def tokenize(example):
    return tokenizer(example["content"], padding="max_length", truncation=True, max_length=512)

ds_new_tok = ds_new.map(tokenize, batched=True)

# 5. Eğitim ayarları — üzerine yazılacak
training_args = TrainingArguments(
    output_dir=MODEL_PATH,  # Aynı model klasörüne tekrar yaz
    per_device_train_batch_size=8,
    num_train_epochs=3,  # Yeni veri az olduğu için 3 epoch yeterli
    logging_steps=10,
    save_strategy="no"
)

# 6. Trainer başlat ve eğit
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=ds_new_tok
)

trainer.train()

# 7. Güncellenmiş modeli kaydet
model.save_pretrained(MODEL_PATH)
tokenizer.save_pretrained(MODEL_PATH)

print("✅ Yeni verilerle yeniden eğitildi ve model güncellendi.")
