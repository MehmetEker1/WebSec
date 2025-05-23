chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
    if (message.action === "checkDomain") {
        chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
            const url = new URL(tabs[0].url);
            const domain = url.hostname.replace("www.", "");

            fetch("https://localhost:5005/url-check", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ domain })
            })
                .then(res => res.json())
                .then(data => sendResponse({ safe: data.safe }))
                .catch(() => sendResponse({ safe: false }));
        });

        // async response gelmesini beklet
        return true;
    }
});
