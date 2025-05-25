from flask_cors import CORS
from flask import Flask, request, jsonify
from transformers import BertTokenizer, BertForSequenceClassification
import torch
import pickle
import os
import csv

app = Flask(__name__)
CORS(app)  # CORS izinleri için şart

device = torch.device("cpu")
MODEL_PATH = "../models/bert-turkish-finetuned"

# Model ve tokenizer yükleniyor
tokenizer = BertTokenizer.from_pretrained(MODEL_PATH)
model = BertForSequenceClassification.from_pretrained(MODEL_PATH)
model.to(device)
model.eval()

# known_domains.pkl yükleniyor
KNOWN_DOMAINS_PATH = "../data/known_domains.pkl"
if os.path.exists(KNOWN_DOMAINS_PATH):
    with open(KNOWN_DOMAINS_PATH, "rb") as f:
        known_domains = pickle.load(f)
    print(f"✅ {len(known_domains)} domain belleğe yüklendi.")
else:
    known_domains = set()
    print("⚠️ known_domains.pkl bulunamadı.")

# USOM kara listesi yükleniyor
USOM_LIST_PATH = "../data/url-list.txt"
def load_usom():
    domains = set()
    if os.path.exists(USOM_LIST_PATH):
        with open(USOM_LIST_PATH, "r") as f:
            for line in f:
                domain = line.strip().lower()
                domain = domain.replace("http://", "").replace("https://", "").split("/")[0]
                if domain:
                    domains.add(domain)
    print(f"🛑 USOM kara listesi yüklendi: {len(domains)} domain")
    return domains

usom_blocked = load_usom()

# Analiz edilen chunk'ları CSV'ye ekle
CSV_PATH = "../data/analyzed_chunks.csv"
def append_chunks_to_csv(chunks):
    file_exists = os.path.isfile(CSV_PATH)
    with open(CSV_PATH, "a", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        if not file_exists:
            writer.writerow(["chunk", "label"])
        for item in chunks:
            writer.writerow([
                item.get("text", ""),
                item.get("label", "")
            ])
    print(f"✅ {len(chunks)} satır eklendi → {CSV_PATH}")

# İçerik tahmini endpoint'i
@app.route("/predict", methods=["POST"])
def predict():
    data = request.get_json()
    text = data.get("text", "")

    if not text:
        return jsonify({"error": "Metin boş olamaz"}), 400

    print("🟢 API'ye gelen metin:", text)

    inputs = tokenizer(text, return_tensors="pt", truncation=True, padding=True, max_length=512)
    inputs = {k: v.to(device) for k, v in inputs.items()}

    with torch.no_grad():
        outputs = model(**inputs)
        probs = torch.softmax(outputs.logits, dim=1)
        pred = torch.argmax(probs, dim=1).item()
        confidence = round(probs[0][pred].item(), 3)

    return jsonify({
        "label": pred,
        "confidence": confidence
    })

# Chunk batch'i CSV'ye ekle endpoint'i
@app.route("/save-labels", methods=["POST"])
def save_labels():
    data = request.get_json()
    results = data.get("results", [])
    if not isinstance(results, list) or not results:
        return jsonify({"error": "Geçerli 'results' listesi gönderilmeli."}), 400
    append_chunks_to_csv(results)
    return jsonify({"message": "CSV'ye eklendi", "count": len(results)})

# URL kontrol endpoint'i (güvenli, zararlı, analiz)
@app.route("/url-check", methods=["POST"])
def check_url():
    data = request.get_json()
    domain = data.get("domain", "").lower().replace("www.", "").strip()

    if not domain:
        return jsonify({"error": "Geçersiz domain"}), 400

    if domain in known_domains:
        return jsonify({
            "domain": domain,
            "status": "safe"
        })

    if domain in usom_blocked:
        return jsonify({
            "domain": domain,
            "status": "malicious"
        })

    return jsonify({
        "domain": domain,
        "status": "analyze"
    })

def warmup_model():
    print("🔥 İlk test çağrısı yapılıyor (warmup)...")
    dummy = "Bu sadece test içindir."
    inputs = tokenizer(dummy, return_tensors="pt", truncation=True, padding=True, max_length=512)
    inputs = {k: v.to(device) for k, v in inputs.items()}
    with torch.no_grad():
        _ = model(**inputs)
    print("✅ Model hazırlandı, API istek almaya hazır.")

if __name__ == "__main__":
    warmup_model()
    print("🚀 Flask API başlatılıyor (https://localhost:5005)")
    app.run(debug=True, port=5005, ssl_context=("../cert/cert.pem", "../cert/key.pem"))
