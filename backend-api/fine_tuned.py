from transformers import BertTokenizer, BertForSequenceClassification, Trainer, TrainingArguments
from datasets import Dataset
import pandas as pd

# 1. CSV dosyasını yükle (Türkçe zararlı ve güvenli içerikler)
df_tr = pd.read_csv("../data/balanced_turkish_dataset_v2.csv")

# 2. Hugging Face Dataset formatına çevir
ds_tr = Dataset.from_pandas(df_tr)

# 3. Tokenizer yükle (önceden indirilmiş Türkçe model)
tokenizer = BertTokenizer.from_pretrained("../models/bert-turkish")

# 4. Tokenizer uygulama
def tokenize(example):
    return tokenizer(example["content"], padding="max_length", truncation=True, max_length=512)

ds_tr_tok = ds_tr.map(tokenize, batched=True)

# 5. Modeli yükle
model = BertForSequenceClassification.from_pretrained("../models/bert-turkish", num_labels=2)

# 6. Eğitim ayarlarını tanımla
training_args = TrainingArguments(
    output_dir="../models/bert-turkish-finetuned",
    per_device_train_batch_size=8,
    num_train_epochs=5,
    logging_steps=10,
    save_strategy="no"
)

# 7. Trainer oluştur ve eğit
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=ds_tr_tok
)
trainer.train()

# 8. Eğitilen modeli ve tokenizer'ı kaydet
model.save_pretrained("../models/bert-turkish-finetuned")
tokenizer.save_pretrained("../models/bert-turkish-finetuned")
