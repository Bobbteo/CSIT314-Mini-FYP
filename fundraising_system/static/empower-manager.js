(function () {
    "use strict";

    const root = document.querySelector("[data-emp-manager]");
    if (!root) return;

    const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

    const searchInput = root.querySelector(".emp-search__input");
    const clearBtn = root.querySelector("[data-search-clear]");
    const cards = () => Array.from(root.querySelectorAll("[data-emp-mgr-card]"));

    function filterCards(query) {
        const q = (query || "").toLowerCase().trim();
        let visible = 0;
        cards().forEach((card) => {
            const haystack = card.getAttribute("data-search") || "";
            const show = !q || haystack.includes(q);
            card.classList.toggle("is-hidden", !show);
            if (show) visible += 1;
        });
        const empty = root.querySelector(".emp-empty");
        if (empty) {
            empty.classList.toggle("is-dismissed", visible > 0 && cards().length > 0);
        }
        if (clearBtn) clearBtn.hidden = !q;
    }

    if (searchInput) {
        searchInput.addEventListener("input", () => filterCards(searchInput.value));
        clearBtn?.addEventListener("click", () => {
            searchInput.value = "";
            filterCards("");
            searchInput.focus();
        });
        filterCards(searchInput.value);
    }

    function formatCount(value, el) {
        const prefix = el.getAttribute("data-count-prefix") || "";
        const suffix = el.getAttribute("data-count-suffix") || "";
        const decimals = parseInt(el.getAttribute("data-count-decimals") || "0", 10);
        if (decimals > 0) return prefix + value.toFixed(decimals) + suffix;
        return prefix + Math.round(value) + suffix;
    }

    function animateCounter(el) {
        if (el.dataset.counted === "1") return;
        el.dataset.counted = "1";

        const end = parseFloat(el.getAttribute("data-count-end") || "0", 10);
        if (reduceMotion) {
            el.textContent = formatCount(end, el);
            return;
        }

        const duration = 1100;
        const start = performance.now();

        function tick(now) {
            const t = Math.min((now - start) / duration, 1);
            const eased = 1 - Math.pow(1 - t, 3);
            el.textContent = formatCount(end * eased, el);
            if (t < 1) requestAnimationFrame(tick);
            else el.textContent = formatCount(end, el);
        }

        requestAnimationFrame(tick);
    }

    const counters = root.querySelectorAll("[data-count-end]");
    if (counters.length && !reduceMotion) {
        const observer = new IntersectionObserver(
            (entries) => {
                entries.forEach((entry) => {
                    if (!entry.isIntersecting) return;
                    animateCounter(entry.target);
                    observer.unobserve(entry.target);
                });
            },
            { threshold: 0.3 }
        );
        counters.forEach((el) => observer.observe(el));
    } else {
        counters.forEach((el) => animateCounter(el));
    }
})();
