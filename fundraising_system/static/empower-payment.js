(function () {
    "use strict";

    const pay = document.querySelector("[data-emp-pay]");
    if (!pay) return;

    document.querySelectorAll(".emp-view-btn--magnetic").forEach((btn) => {
        btn.addEventListener("mousemove", (e) => {
            const r = btn.getBoundingClientRect();
            btn.style.transform = `translate(${(e.clientX - r.left - r.width / 2) * 0.1}px, ${(e.clientY - r.top - r.height / 2) * 0.1}px)`;
        });
        btn.addEventListener("mouseleave", () => {
            btn.style.transform = "";
        });
    });
})();
