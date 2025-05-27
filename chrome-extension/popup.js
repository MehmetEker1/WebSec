document.addEventListener("DOMContentLoaded", function () {
  const statusEl = document.getElementById("mainStatus");
  const buttonEl = document.getElementById("checkButton");
  const spinner = document.getElementById("spinner");
  const resultIcon = document.getElementById("resultIcon");

  // Sonucu ikonla göster
  function setResultIcon(status) {
    if (status === "safe") {
      resultIcon.innerHTML = `<svg width="58" height="58" viewBox="0 0 24 24" fill="none">
        <circle cx="12" cy="12" r="11" fill="#1d2a23" stroke="#57d087" stroke-width="2.5"/>
        <path d="M8 13.5l2.5 2.5 5-5" stroke="#57d087" stroke-width="2.3" stroke-linecap="round" stroke-linejoin="round"/>
      </svg>`;
      resultIcon.className = "big-icon safe";
    } else if (status === "danger") {
      resultIcon.innerHTML = `<svg width="58" height="58" viewBox="0 0 24 24" fill="none">
        <circle cx="12" cy="12" r="11" fill="#27181b" stroke="#ff6371" stroke-width="2.5"/>
        <path d="M9.3 9.3l5.4 5.4M14.7 9.3l-5.4 5.4" stroke="#ff6371" stroke-width="2.3" stroke-linecap="round"/>
      </svg>`;
      resultIcon.className = "big-icon danger";
    } else {
      resultIcon.innerHTML = ""; // Yüklenirken veya hata olunca ikon yok
      resultIcon.className = "big-icon loading";
    }
  }

  function showLoading() {
    setResultIcon(null);
    spinner.style.display = "flex";
    statusEl.textContent = "İçerik analiz ediliyor...";
    statusEl.className = "loading";
  }

  function hideLoading() {
    spinner.style.display = "none";
  }

  buttonEl.addEventListener("click", () => {
    showLoading();

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
            hideLoading();
            setResultIcon("safe");
            statusEl.textContent = "Güvenli Site (Top 1M listesinde)";
            statusEl.className = "safe";
          } else if (data.status === "malicious") {
            hideLoading();
            setResultIcon("danger");
            statusEl.textContent = "Zararlı Site (USOM kara listesinde)";
            statusEl.className = "danger";
          } else if (data.status === "analyze") {
            showLoading();
            chrome.scripting.executeScript({
              target: { tabId: tab.id },
              files: ["content.js"]
            }, () => {
              if (chrome.runtime.lastError) {
                hideLoading();
                statusEl.textContent = "İçerik analizi modülü yüklenemedi.";
                setResultIcon("danger");
                statusEl.className = "danger";
                return;
              }
              chrome.tabs.sendMessage(tab.id, { action: "analyzeContent" }, (res) => {
                showLoading();
              });
            });
          } else {
            hideLoading();
            setResultIcon("danger");
            statusEl.textContent = "Bilinmeyen bir hata oluştu";
            statusEl.className = "danger";
          }
        })
        .catch(err => {
          hideLoading();
          setResultIcon("danger");
          statusEl.textContent = "Hata oluştu (domain kontrol edilemedi)";
          statusEl.className = "danger";
        });
    });
  });

  // İçerik analiz sonucu mesajı
  chrome.runtime.onMessage.addListener((message) => {
    hideLoading();
    if (message.action === "setStatus") {
      if (message.status === "malicious") {
        setResultIcon("danger");
        statusEl.textContent = "Zararlı içerik tespit edildi!";
        statusEl.className = "danger";
      } else if (message.status === "safe") {
        setResultIcon("safe");
        statusEl.textContent = "İçerik güvenli";
        statusEl.className = "safe";
      } else {
        setResultIcon("danger");
        statusEl.textContent = "İçerik analizi sırasında hata oluştu";
        statusEl.className = "danger";
      }
    }
  });
});
