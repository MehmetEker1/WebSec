from flask import Flask, request, jsonify
from transformers import BertTokenizer, BertForSequenceClassification
import torch

app = Flask(__name__)

device = torch.device("cpu")
MODEL_PATH = "../models/bert-turkish-finetuned"

tokenizer = BertTokenizer.from_pretrained(MODEL_PATH)
model = BertForSequenceClassification.from_pretrained(MODEL_PATH)
model.to(device)
model.eval()

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

# MODELİ LAZY LOAD'DAN KURTAR
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
    print("🚀 Flask API başlatılıyor (http://localhost:5005)")
    app.run(debug=True, port=5005)
