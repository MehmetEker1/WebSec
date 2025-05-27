function analyzeContent() {
    const rawText = document.body.innerText || "";

    if (!rawText.trim()) {
        console.warn("⛔ Sayfa metni boş, analiz iptal edildi.");
        chrome.runtime.sendMessage({
            action: "setStatus",
            status: "error"
        });
        return;
    }

    function chunkText(text, size = 5) {
        const words = text.split(/\s+/);
        const chunks = [];
        for (let i = 0; i < words.length; i += size) {
            chunks.push(words.slice(i, i + size).join(" "));
        }
        return chunks;
    }

    const chunks = chunkText(rawText, 5).slice(0, 100);
    const promises = chunks.map(chunk =>
        fetch("https://localhost:5005/predict", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ text: chunk })
        })
            .then(res => res.json())
            .then(result => ({ text: chunk, ...result }))
    );

    Promise.all(promises)
        .then(results => {
            // === CSV'ye KAYIT ===
            fetch("https://localhost:5005/save-labels", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ results })
            });

            const maliciousChunks = results.filter(r => r.label === 1);
            const ratio = maliciousChunks.length / results.length;
            const isMalicious = ratio > 0.3;

            if (maliciousChunks.length > 0) {
                console.warn(`🚨 ${maliciousChunks.length} zararlı içerik bulundu:`);
                maliciousChunks.forEach((chunk, index) => {
                    console.warn(`⚠️ ${index + 1}. [${chunk.confidence}] → ${chunk.text}`);
                });
            }

            chrome.runtime.sendMessage({
                action: "setStatus",
                status: isMalicious ? "malicious" : "safe"
            });

            console.log(`📊 ${maliciousChunks.length}/${results.length} blok zararlı (${Math.round(ratio * 100)}%)`);
            console.log("✅ İçerik sonucu gönderildi:", isMalicious ? "malicious" : "safe");
        })
        .catch(err => {
            console.error("❌ İçerik analizi hatası:", err);
            chrome.runtime.sendMessage({
                action: "setStatus",
                status: "error"
            });
        });
}

// 🧪 Debug için gelen mesajı konsola yaz
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    console.log("📨 Gelen mesaj:", request);
    if (request.action === "analyzeContent") {
        console.log("🚀 İçerik analizi tetiklendi.");
        analyzeContent();
    }
});
