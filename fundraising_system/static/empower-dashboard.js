(function () {
    const dashboard = document.querySelector("[data-emp-dashboard]");
    if (!dashboard) return;

    const searchInput = dashboard.querySelector(".emp-search__input");
    const clearBtn = dashboard.querySelector("[data-search-clear]");
    const cards = () => Array.from(dashboard.querySelectorAll("[data-emp-card]"));

    function normalize(text) {
        return (text || "").toLowerCase().trim();
    }

    function filterCards(query) {
        const q = normalize(query);
        let visible = 0;
        cards().forEach((card) => {
            const haystack = card.getAttribute("data-search") || "";
            const show = !q || haystack.includes(q);
            card.classList.toggle("is-hidden", !show);
            if (show) visible += 1;
        });
        const empty = dashboard.querySelector(".emp-empty");
        if (empty) {
            empty.classList.toggle("is-dismissed", visible > 0 && cards().length > 0);
        }
        if (clearBtn) {
            clearBtn.hidden = !q;
        }
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

    function openPortal(portal, url, title) {
        const frame = portal.querySelector(".emp-portal__frame");
        const titleEl = portal.querySelector("[data-portal-title]");
        const embedUrl = url.includes("?") ? url + "&embed=1" : url + "?embed=1";

        if (frame) {
            const isFormPortal = portal.classList.contains("emp-portal--form");
            frame.onload = function onFrameLoad() {
                if (!isFormPortal) return;
                try {
                    const path = frame.contentWindow?.location?.pathname || "";
                    const isForm =
                        path.includes("/fra/create") || /\/fra\/\d+\/edit/.test(path);
                    if (!isForm && portal.classList.contains("is-open")) {
                        frame.onload = null;
                        finishFormSuccess();
                    }
                } catch (err) {
                    /* ignore cross-origin */
                }
            };
            frame.src = embedUrl;
        }

        if (titleEl && title) titleEl.textContent = title;
        portal.classList.add("is-open");
        portal.setAttribute("aria-hidden", "false");
        document.body.style.overflow = "hidden";
    }

    function finishFormSuccess() {
        document.querySelectorAll(".emp-portal.is-open").forEach((p) => closePortal(p, true));
        window.location.reload();
    }

    function closePortal(portal, animate) {
        const finish = () => {
            portal.classList.remove("is-open", "is-closing");
            portal.setAttribute("aria-hidden", "true");
            const frame = portal.querySelector(".emp-portal__frame");
            if (frame) frame.src = "about:blank";
            if (!document.querySelector(".emp-portal.is-open")) {
                document.body.style.overflow = "";
            }
        };

        if (animate) {
            portal.classList.add("is-closing");
            setTimeout(finish, 420);
        } else {
            finish();
        }
    }

    document.querySelectorAll("[data-portal-open]").forEach((trigger) => {
        trigger.addEventListener("click", (e) => {
            e.preventDefault();
            const id = trigger.getAttribute("data-portal-open");
            const portal = document.getElementById(id);
            const url = trigger.getAttribute("href");
            const title = trigger.getAttribute("data-portal-title") || trigger.textContent.trim();
            if (portal && url) openPortal(portal, url, title);
        });
    });

    document.querySelectorAll("[data-portal-close]").forEach((btn) => {
        btn.addEventListener("click", () => {
            const portal = btn.closest(".emp-portal");
            if (portal) closePortal(portal, true);
        });
    });

    document.addEventListener("keydown", (e) => {
        if (e.key === "Escape") {
            document.querySelectorAll(".emp-portal.is-open").forEach((p) => closePortal(p, true));
            dashboard.querySelector(".emp-more")?.classList.remove("is-open");
        }
    });

    window.addEventListener("message", (e) => {
        if (e.data === "emp-form-success") {
            finishFormSuccess();
        }
        if (e.data === "emp-portal-close") {
            document.querySelectorAll(".emp-portal.is-open").forEach((p) => closePortal(p, true));
        }
    });

    const more = dashboard.querySelector(".emp-more");
    if (more) {
        const toggle = more.querySelector("[data-more-toggle]");
        toggle?.addEventListener("click", (e) => {
            e.stopPropagation();
            more.classList.toggle("is-open");
        });
        document.addEventListener("click", () => more.classList.remove("is-open"));
    }

    document.querySelectorAll(".emp-btn--magnetic").forEach((btn) => {
        btn.addEventListener("mousemove", (e) => {
            const rect = btn.getBoundingClientRect();
            const x = e.clientX - rect.left - rect.width / 2;
            const y = e.clientY - rect.top - rect.height / 2;
            btn.style.transform = `translate(${x * 0.12}px, ${y * 0.12}px)`;
        });
        btn.addEventListener("mouseleave", () => {
            btn.style.transform = "";
        });
    });

    const progressObserver = new IntersectionObserver(
        (entries) => {
            entries.forEach((entry) => {
                if (entry.isIntersecting) {
                    entry.target.closest(".emp-card")?.classList.add("is-progress-visible");
                    progressObserver.unobserve(entry.target);
                }
            });
        },
        { threshold: 0.25, rootMargin: "0px 0px -40px 0px" }
    );

    dashboard.querySelectorAll("[data-progress-bar]").forEach((bar) => progressObserver.observe(bar));
})();
