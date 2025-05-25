document.addEventListener("DOMContentLoaded", function () {
  const statusEl = document.getElementById("siteStatus");
  const buttonEl = document.getElementById("checkButton");

  buttonEl.addEventListener("click", () => {
    statusEl.textContent = "🔎 Domain kontrol ediliyor...";
    statusEl.className = "";

    chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
      const tab = tabs[0];
      const domain = new URL(tab.url).hostname.replace("www.", "").toLowerCase();

      fetch("https://localhost:5005/url-check", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ domain })
      })
        .then(res => res.json())
        .then(data => {
          if (data.status === "safe") {
            statusEl.textContent = "✅ Güvenli Site (Top 1M listesinde)";
            statusEl.className = "status-safe";
          } else if (data.status === "malicious") {
            statusEl.textContent = "⚠️ Zararlı Site (USOM kara listesinde)";
            statusEl.className = "status-danger";
          } else if (data.status === "analyze") {
            statusEl.textContent = "🧠 İçerik analizi başlatılıyor...";
            statusEl.className = "";

            chrome.scripting.executeScript({
              target: { tabId: tab.id },
              files: ["content.js"]
            }, () => {
              if (chrome.runtime.lastError) {
                console.error("❌ content.js yüklenemedi:", chrome.runtime.lastError.message);
                statusEl.textContent = "❌ İçerik analizi modülü yüklenemedi.";
                return;
              }

              chrome.tabs.sendMessage(tab.id, { action: "analyzeContent" }, (res) => {
                if (chrome.runtime.lastError) {
                  console.error("❌ analyzeContent mesajı gönderilemedi:", chrome.runtime.lastError.message);
                  statusEl.textContent = "İçerik analiz ediliyor";
                } else {
                  console.log("✅ analyzeContent mesajı başarıyla gönderildi.");
                  statusEl.textContent = "⏳ İçerik analiz ediliyor...";
                }
              });
            });
          } else {
            statusEl.textContent = "❌ Bilinmeyen bir hata oluştu";
            statusEl.className = "";
          }
        })
        .catch(err => {
          console.error("❌ URL kontrol hatası:", err);
          statusEl.textContent = "❌ Hata oluştu (domain kontrol edilemedi)";
        });
    });
  });

  chrome.runtime.onMessage.addListener((message) => {
    if (message.action === "setStatus") {
      if (message.status === "malicious") {
        statusEl.textContent = "⚠️ Zararlı içerik tespit edildi!";
        statusEl.className = "status-danger";
      } else if (message.status === "safe") {
        statusEl.textContent = "✅ İçerik güvenli";
        statusEl.className = "status-safe";
      } else {
        statusEl.textContent = "❌ İçerik analizi sırasında hata oluştu";
        statusEl.className = "";
      }
    }
  });
});
