(function () {
    const root = document.querySelector("[data-fra-dashboard]");
    if (!root) return;

    const searchInput = root.querySelector("#fra-search");
    const rows = () => Array.from(root.querySelectorAll("[data-fra-row]"));
    const emptyState = root.querySelector(".fra-dash-empty");
    const listEl = root.querySelector(".fra-dash-list-wrap .fra-dash-list");
    const demoBanner = root.querySelector(".fra-dash-demo-banner");

    const DEMO_ROWS = [
        { id: 101, title: "Community Garden Revival", category: "Community", target: 5000, current: 3240, status: "active", start: "2026-01-15", end: "2026-06-30" },
        { id: 102, title: "STEM Kits for Rural Schools", category: "Education", target: 12000, current: 8750, status: "active", start: "2026-02-01", end: "2026-08-15" },
        { id: 103, title: "Emergency Flood Relief Fund", category: "Emergency", target: 25000, current: 25000, status: "goal_achieved", start: "2025-11-01", end: "2026-03-01" },
    ];

    function normalize(text) {
        return (text || "").toLowerCase().trim();
    }

    function filterRows(query) {
        const q = normalize(query);
        let visible = 0;

        rows().forEach((row) => {
            const haystack = row.getAttribute("data-search") || "";
            const show = !q || haystack.includes(q);
            row.classList.toggle("is-hidden", !show);
            if (show) visible += 1;
        });

        if (emptyState) {
            const hasReal = rows().some((r) => !r.classList.contains("fra-dash-row--demo"));
            emptyState.classList.toggle("is-dismissed", visible > 0 || (hasReal && rows().length > 0));
        }
    }

    if (searchInput) {
        searchInput.addEventListener("input", () => filterRows(searchInput.value));
        filterRows(searchInput.value);
    }

    function cell(className, html) {
        const el = document.createElement("div");
        el.className = className;
        el.innerHTML = html;
        return el;
    }

    function buildDemoRow(data) {
        const pct = Math.min(100, Math.round((data.current / data.target) * 100));
        const statusLabel = data.status.replace(/_/g, " ");
        const row = document.createElement("article");
        row.className = "fra-dash-row fra-dash-row--demo";
        row.setAttribute("data-fra-row", "");
        row.setAttribute(
            "data-search",
            [data.id, data.title, data.category, data.status, statusLabel].join(" ").toLowerCase()
        );

        const progress = document.createElement("div");
        progress.className = "fra-dash-row__progress";
        const amounts = document.createElement("div");
        amounts.className = "fra-dash-row__amounts";
        amounts.textContent =
            "$" + data.current.toLocaleString() + " / $" + data.target.toLocaleString();

        const bar = document.createElement("div");
        bar.className = "fra-dash-row__bar";
        const fill = document.createElement("div");
        fill.className = "fra-dash-row__bar-fill";
        fill.style.width = pct + "%";
        bar.appendChild(fill);
        progress.appendChild(amounts);
        progress.appendChild(bar);

        const progressWrap = document.createElement("div");
        progressWrap.className = "fra-dash-row__cell";
        progressWrap.appendChild(progress);

        row.appendChild(cell("fra-dash-row__cell fra-dash-row__cell--id", "#" + data.id));
        row.appendChild(cell("fra-dash-row__cell fra-dash-row__cell--title", data.title));
        row.appendChild(cell("fra-dash-row__cell", data.category));
        row.appendChild(progressWrap);
        row.appendChild(cell("fra-dash-row__cell", "—"));
        row.appendChild(
            cell(
                "fra-dash-row__cell",
                '<span class="fra-dash-badge fra-dash-badge--' + data.status + '">' + statusLabel + "</span>"
            )
        );
        row.appendChild(cell("fra-dash-row__cell", data.start));
        row.appendChild(cell("fra-dash-row__cell", data.end));
        row.appendChild(
            cell(
                "fra-dash-row__cell fra-dash-row__actions",
                '<span class="fra-dash-row__btn fra-dash-row__btn--edit">Preview</span>'
            )
        );

        return row;
    }

    const previewBtn = root.querySelector("[data-preview-demo]");
    if (previewBtn && listEl) {
        previewBtn.addEventListener("click", () => {
            if (root.querySelector(".fra-dash-row--demo")) return;
            DEMO_ROWS.forEach((d) => listEl.appendChild(buildDemoRow(d)));
            if (demoBanner) demoBanner.classList.add("is-visible");
            if (emptyState) emptyState.classList.add("is-dismissed");
            filterRows(searchInput ? searchInput.value : "");
        });
    }

    function openPanel(panel, url) {
        const frame = panel.querySelector("iframe");
        if (frame) frame.src = url;
        panel.classList.add("is-open");
        panel.setAttribute("aria-hidden", "false");
        document.body.style.overflow = "hidden";
    }

    function closePanel(panel) {
        panel.classList.remove("is-open");
        panel.setAttribute("aria-hidden", "true");
        const frame = panel.querySelector("iframe");
        if (frame) frame.src = "about:blank";
        if (!document.querySelector(".fra-dash-panel.is-open")) {
            document.body.style.overflow = "";
        }
    }

    root.querySelectorAll("[data-panel-open]").forEach((trigger) => {
        trigger.addEventListener("click", (e) => {
            e.preventDefault();
            const panelId = trigger.getAttribute("data-panel-open");
            const panel = document.getElementById(panelId);
            const url = trigger.getAttribute("href") || trigger.dataset.panelUrl;
            if (panel && url) openPanel(panel, url.includes("?") ? url + "&embed=1" : url + "?embed=1");
        });
    });

    document.querySelectorAll("[data-panel-close]").forEach((btn) => {
        btn.addEventListener("click", () => {
            const panel = btn.closest(".fra-dash-panel");
            if (panel) closePanel(panel);
        });
    });

    const more = root.querySelector(".fra-dash-more");
    if (more) {
        const toggle = more.querySelector("[data-more-toggle]");
        toggle?.addEventListener("click", () => {
            const open = more.classList.toggle("is-open");
            toggle.setAttribute("aria-expanded", open ? "true" : "false");
        });
        document.addEventListener("click", (e) => {
            if (!more.contains(e.target)) {
                more.classList.remove("is-open");
                toggle?.setAttribute("aria-expanded", "false");
            }
        });
    }

    const palette = document.getElementById("fra-cmd-palette");
    const paletteInput = palette?.querySelector(".fra-dash-palette__input");

    function togglePalette(open) {
        if (!palette) return;
        palette.classList.toggle("is-open", open);
        palette.setAttribute("aria-hidden", open ? "false" : "true");
        if (open) {
            paletteInput?.focus();
            if (paletteInput && searchInput) paletteInput.value = searchInput.value;
        }
    }

    document.addEventListener("keydown", (e) => {
        if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === "k") {
            e.preventDefault();
            togglePalette(true);
        }
        if (e.key === "Escape") {
            togglePalette(false);
            document.querySelectorAll(".fra-dash-panel.is-open").forEach(closePanel);
            more?.classList.remove("is-open");
        }
    });

    paletteInput?.addEventListener("input", () => {
        if (searchInput) {
            searchInput.value = paletteInput.value;
            filterRows(paletteInput.value);
        }
    });

    palette?.querySelector("[data-palette-close]")?.addEventListener("click", () => togglePalette(false));
    palette?.querySelector(".fra-dash-palette__backdrop")?.addEventListener("click", () => togglePalette(false));
})();
