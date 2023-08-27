document.addEventListener("DOMContentLoaded", function () {
    const versionsButtons = document.querySelectorAll(".versions-button");
    const searchButton = document.getElementById("search-button");
    const appSearchInput = document.getElementById("app-search");

    versionsButtons.forEach(function (button) {
        button.addEventListener("click", function () {
            const appCard = button.closest(".app-card");
            const versionsContainer = appCard.querySelector(".versions-container");

            if (versionsContainer.classList.contains("visible")) {
                versionsContainer.innerHTML = "";
                versionsContainer.classList.remove("visible");
            } else {
                const appVersions = app_versions[appCard.querySelector("h4").textContent];

                appVersions.forEach(function (versionData) {
                    const versionDiv = document.createElement("div");
                    versionDiv.classList.add("version");
                    versionDiv.innerHTML = `
                        <p>Version: ${versionData.version}</p>
                        <p>Size: ${versionData.size}</p>
                        <a class="download-button" href="${versionData.download_url}" target="_blank">Download</a>
                        <a class="install-button" href="apple-magnifier://install?url=${versionData.download_url}" target="_blank">Install</a>
                    `;
                    versionsContainer.appendChild(versionDiv);
                });

                versionsContainer.classList.add("visible");
            }
        });
    });
    searchButton.addEventListener("click", function () {
        const searchQuery = appSearchInput.value.trim().toLowerCase();
        const appCards = document.querySelectorAll(".app-card");

        appCards.forEach(function (appCard) {
            const appName = appCard.querySelector("h4").textContent.toLowerCase();

            if (appName.includes(searchQuery)) {
                appCard.style.display = "block";
            } else {
                appCard.style.display = "none";
            }
        });
    });
});



