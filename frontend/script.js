document.querySelector(".scan-btn").addEventListener("click", async () => {

    let url = document.querySelector("#urlInput").value;

    if (!url) {
        alert("Enter a URL");
        return;
    }

    if (!url.startsWith("http")) {
        url = "http://" + url;
    }

    try {
    const response = await fetch("https://phishing-detector-s0nb.onrender.com/predict", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ url: url })
    });

    const data = await response.json();
    console.log(data);

    } catch (error) {
    console.error("API error:", error);
    }

    const data = await response.json();

    console.log("API RESPONSE:", data);

    const verdictElement = document.querySelector("#verdict");
    const confidenceElement = document.querySelector("#confidence");
    const rawScoreElement = document.querySelector("#rawScore");
    const domainElement = document.querySelector("#domain");

    const probability = (data.probability * 100).toFixed(2);

    verdictElement.innerText = data.prediction.toUpperCase();
    confidenceElement.innerText = probability + "%";
    rawScoreElement.innerText = data.probability.toFixed(6);
    let cleanUrl = url.trim();

    if (!cleanUrl.startsWith("http://") && !cleanUrl.startsWith("https://")) {
    cleanUrl = "http://" + cleanUrl;
    }

    try {
        const parsedUrl = new URL(cleanUrl);
        domainElement.innerText = parsedUrl.hostname;
    } catch (error) {
        console.error("Invalid URL:", cleanUrl);
        domainElement.innerText = cleanUrl;
    }
});