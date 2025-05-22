from transformers import BertTokenizer, BertForSequenceClassification

tr_model_name = "dbmdz/bert-base-turkish-uncased"
en_model_name = "bert-base-uncased"

tr_path = "../models/bert-turkish"
en_path = "../models/bert-english"

print("🔽 Türkçe model indiriliyor...")
tr_tokenizer = BertTokenizer.from_pretrained(tr_model_name)
tr_model = BertForSequenceClassification.from_pretrained(tr_model_name, num_labels=2)
tr_tokenizer.save_pretrained(tr_path)
tr_model.save_pretrained(tr_path)
print("✅ Türkçe model indirildi ve kaydedildi.")

print("🔽 İngilizce model indiriliyor...")
en_tokenizer = BertTokenizer.from_pretrained(en_model_name)
en_model = BertForSequenceClassification.from_pretrained(en_model_name, num_labels=2)
en_tokenizer.save_pretrained(en_path)
en_model.save_pretrained(en_path)
print("✅ İngilizce model indirildi ve kaydedildi.")
