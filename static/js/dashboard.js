document.addEventListener("DOMContentLoaded", function () {
    console.log("Dashboard script loaded");

    // Function to submit summary
    function submitSummary(event) {
        event.preventDefault(); // Prevent page reload
        console.log("Summarize button clicked!");

        let text = document.getElementById("text").value;
        let category = document.getElementById("category").value;
        let csrfToken = document.getElementById("csrf_token").value;

        if (!text.trim()) {
            alert("Please enter text to summarize.");
            return;
        }

        fetch("/summarize/", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": csrfToken
            },
            body: JSON.stringify({
                "text": text,
                "category": category
            })
        })
        .then(response => response.json())
        .then(data => {
            console.log("Server response:", data);
            if (data.message) {
                location.reload();
            } else {
                alert("Failed to summarize text: " + (data.error || "Unknown error"));
            }
        })
        .catch(error => console.error("Error:", error));
    }

    // Function to filter summaries
    function filterSummaries() {
        let sortOrder = document.getElementById("sort_order").value;

        fetch("/summaries/?sort=" + sortOrder, {
            method: "GET",
            headers: {
                "Content-Type": "application/json"
            }
        })
        .then(response => response.json())
        .then(data => {
            let summaryList = document.getElementById("summary_list");
            summaryList.innerHTML = "";

            if (data.length === 0) {
                summaryList.innerHTML = "<li>No summaries found.</li>";
            } else {
                data.forEach(summary => {
                    let listItem = document.createElement("div");
                    listItem.className = "p-4 border rounded-lg shadow-sm bg-gray-50";
                    listItem.innerHTML = `<p class="text-gray-800"><strong>Summary:</strong> ${summary.text}</p>
                                          <p class="text-gray-500 text-sm mt-1"><strong>Category:</strong> ${summary.category}</p>`;
                    summaryList.appendChild(listItem);
                });
            }
        })
        .catch(error => console.error("Error:", error));
    }

    // Function to search summaries
    function searchSummaries(event) {
        event.preventDefault();

        let query = document.getElementById("search_query").value;
        let resultsDiv = document.getElementById("search_results");
        let csrfToken = document.getElementById("csrf_token").value;

        resultsDiv.innerHTML = "Searching...";

        fetch("/search/", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": csrfToken
            },
            body: JSON.stringify({ "query": query })
        })
        .then(response => response.json())
        .then(data => {
            resultsDiv.innerHTML = "";

            if (data.error) {
                resultsDiv.innerHTML = `<p>Error: ${data.error}</p>`;
                return;
            }

            if (data.matches.length === 0) {
                resultsDiv.innerHTML = "<p>No relevant summaries found.</p>";
            } else {
                let ul = document.createElement("ul");
                data.matches.forEach(match => {
                    let li = document.createElement("li");
                    li.innerHTML = `<strong>Score:</strong> ${match.score.toFixed(2)}<br><strong>Summary:</strong> ${match.metadata.text}`;
                    ul.appendChild(li);
                });
                resultsDiv.appendChild(ul);
            }
        })
        .catch(error => {
            console.error("Error:", error);
            resultsDiv.innerHTML = "<p>Failed to fetch results.</p>";
        });
    }

    // Attach event listeners
    document.getElementById("summaryForm").addEventListener("submit", submitSummary);
    document.getElementById("searchForm").addEventListener("submit", searchSummaries);
    document.getElementById("sort_order").addEventListener("change", filterSummaries);
});
