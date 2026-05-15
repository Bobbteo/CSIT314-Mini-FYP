(function () {
    const sub = document.querySelector("[data-emp-sub]");
    if (!sub) return;

    sub.querySelector("[data-emp-sub-close]")?.addEventListener("click", () => {
        window.parent.postMessage("emp-portal-close", "*");
    });
})();
