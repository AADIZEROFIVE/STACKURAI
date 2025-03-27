document.getElementById("newsForm").addEventListener("submit", async function(event) {
    event.preventDefault();
    
    const topic = document.getElementById("topic").value;
    const newsSummaryDiv = document.getElementById("newsSummary");

    newsSummaryDiv.innerHTML = "Fetching news...";

    try {
        const response = await fetch("/get_news/?topic=" + encodeURIComponent(topic));
        const data = await response.json();

        if (response.ok) {
            newsSummaryDiv.innerHTML = `<h3>Summary:</h3><p>${data.news_summary}</p>`;
        } else {
            newsSummaryDiv.innerHTML = `<p>Error: ${data.detail}</p>`;
        }
    } catch (error) {
        newsSummaryDiv.innerHTML = `<p>Error fetching news.</p>`;
    }
});
