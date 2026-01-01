<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Purchase Success</title>
<style>
body { font-family: Arial; padding: 20px; }
h2 { color: #1766f3; }
a { text-decoration: none; color: #fff; background-color: #1766f3; padding: 8px 16px; border-radius: 4px; }
a.disabled { background-color: #aaa; pointer-events: none; }
</style>
</head>
<body>

<h2>Thank you for your purchase!</h2>
<p id="status">Preparing your download...</p>
<p><a id="download-link" href="#" class="disabled">Download</a></p>

<script>
const params = new URLSearchParams(window.location.search);
const sessionId = params.get("session_id");
const statusEl = document.getElementById("status");
const linkEl = document.getElementById("download-link");
const lambdaUrl = "https://on.aws/";

if (!sessionId) {
  statusEl.textContent = "Session ID not found.";
} else {
  (async () => {
    try {
      // Get the current count
      const resStatus = await fetch(`${lambdaUrl}?id=${encodeURIComponent(sessionId)}&action=status`);
      const statusData = await resStatus.json();
      let count = statusData.count || 0;

      // Control button on page load
      if (count >= 4) {
        linkEl.classList.add("disabled");
        statusEl.textContent = "Download limit reached.";
        return;
      }

      linkEl.classList.remove("disabled");
      statusEl.textContent = "Click download to start.";

      // Handle button click
      linkEl.addEventListener("click", async (e) => {
        e.preventDefault();

        try {
          const res = await fetch(`${lambdaUrl}?id=${encodeURIComponent(sessionId)}&action=download`);
          const data = await res.json();

          if (!res.ok || data.error) {
            statusEl.textContent = data.error || "Download failed.";

            // Disable the button if the limit is reached
            if (data.error === "Download limit exceeded") {
              linkEl.classList.add("disabled");
            }
            return;
          }

          // Download via presigned URL
          const a = document.createElement("a");
          a.href = data.download_url;
          a.download = "Download Your Application.zip";
          document.body.appendChild(a);
          a.click();
          a.remove();

          // Update count and control button state
          count++;
          if (count >= 4) {
            linkEl.classList.add("disabled");
            statusEl.textContent = "Download limit reached.";
          }
        } catch (err) {
          statusEl.textContent = "Network error.";
          console.error(err);
        }
      });

    } catch (err) {
      statusEl.textContent = "Failed to get current count.";
      console.error(err);
    }
  })();
}
</script>

</body>
</html>
s