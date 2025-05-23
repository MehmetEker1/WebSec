document.addEventListener("DOMContentLoaded", function () {
  const statusEl = document.getElementById("siteStatus");
  const buttonEl = document.getElementById("checkButton");

  buttonEl.addEventListener("click", () => {
    statusEl.textContent = "Kontrol ediliyor...";
    statusEl.className = "";

    chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
      const tab = tabs[0];
      const domain = new URL(tab.url).hostname.replace("www.", "").toLowerCase();

      // 🔍 Önce domain güvenli mi kontrol et
      fetch("https://localhost:5005/url-check", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ domain })
      })
        .then(res => res.json())
        .then(data => {
          if (data.safe) {
            statusEl.textContent = "✅ Güvenli Site";
            statusEl.className = "status-safe";
          } else {
            // content.js'i yüklüyoruz (gerekirse)
            chrome.scripting.executeScript({
              target: { tabId: tab.id },
              files: ["content.js"]
            }, () => {
              if (chrome.runtime.lastError) {
                console.error("❌ content.js yüklenemedi:", chrome.runtime.lastError.message);
                statusEl.textContent = "❌ İçerik kontrolü yüklenemedi.";
                return;
              }

              // Mesaj gönderiyoruz ama sonucu burada YAKALAMIYORUZ!
              chrome.tabs.sendMessage(tab.id, { action: "analyzeContent" }, (res) => {
                if (chrome.runtime.lastError) {
                  console.warn("🟠 İçerik analiz mesajı gönderildi ama cevap alınamadı:", chrome.runtime.lastError.message);
                  // Bu noktada hiçbir status yazmıyoruz — sonucu content.js'ten bekliyoruz.
                } else {
                  console.log("📨 analyzeContent mesajı başarıyla gönderildi.");
                }
              });
            });
          }
        })
        .catch(err => {
          console.error("❌ URL kontrol hatası:", err);
          statusEl.textContent = "❌ Hata oluştu (domain kontrol)";
        });
    });
  });

  // content.js'ten gelen analiz sonucunu al
  chrome.runtime.onMessage.addListener((message) => {
    if (message.action === "setStatus") {
      if (message.status === "malicious") {
        statusEl.textContent = "⚠️ Zararlı içerik tespit edildi!";
        statusEl.className = "status-danger";
      } else if (message.status === "safe") {
        statusEl.textContent = "✅ Güvenli içerik";
        statusEl.className = "status-safe";
      } else {
        statusEl.textContent = "❌ Hata oluştu";
        statusEl.className = "";
      }
    }
  });
});
