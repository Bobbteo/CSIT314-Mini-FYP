(function () {
    const view = document.querySelector("[data-emp-view]");
    if (!view) return;

    const isEmbed = document.body.classList.contains("emp-view-embed");

    view.querySelector("[data-emp-view-close]")?.addEventListener("click", () => {
        if (isEmbed) {
            window.parent.postMessage("emp-portal-close", "*");
        }
    });

    document.querySelectorAll(".emp-view-btn--magnetic").forEach((btn) => {
        btn.addEventListener("mousemove", (e) => {
            const r = btn.getBoundingClientRect();
            btn.style.transform = `translate(${(e.clientX - r.left - r.width / 2) * 0.1}px, ${(e.clientY - r.top - r.height / 2) * 0.1}px)`;
        });
        btn.addEventListener("mouseleave", () => {
            btn.style.transform = "";
        });
    });

    const bar = view.querySelector(".emp-view__bar-fill");
    if (bar) {
        const target = bar.dataset.pct || bar.style.getPropertyValue("--pct") || "0%";
        requestAnimationFrame(() => {
            bar.style.width = target;
        });
    }
})();
