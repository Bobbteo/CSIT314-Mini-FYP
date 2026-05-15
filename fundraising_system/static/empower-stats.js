(function () {
    const stats = document.querySelector("[data-emp-stats]");
    if (!stats) return;

    stats.querySelector("[data-emp-stats-close]")?.addEventListener("click", () => {
        window.parent.postMessage("emp-portal-close", "*");
    });
})();
