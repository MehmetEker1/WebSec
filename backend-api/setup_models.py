from transformers import BertTokenizer, BertForSequenceClassification

tr_model_name = "dbmdz/bert-base-turkish-uncased"

tr_path = "../models/bert-turkish"

print("🔽 Türkçe model indiriliyor...")
tr_tokenizer = BertTokenizer.from_pretrained(tr_model_name)
tr_model = BertForSequenceClassification.from_pretrained(tr_model_name, num_labels=2)
tr_tokenizer.save_pretrained(tr_path)
tr_model.save_pretrained(tr_path)
print("✅ Türkçe model indirildi ve kaydedildi.")


