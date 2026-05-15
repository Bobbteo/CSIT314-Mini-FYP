(function () {
    "use strict";

    var reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

    /* —— Scroll-mask reveals —— */
    function initReveals() {
        var reveals = document.querySelectorAll(".landing-reveal");
        if (!reveals.length) return;

        if (reduceMotion) {
            reveals.forEach(function (el) {
                el.classList.add("is-visible");
            });
            return;
        }

        var observer = new IntersectionObserver(
            function (entries) {
                entries.forEach(function (entry) {
                    if (!entry.isIntersecting) return;
                    entry.target.classList.add("is-visible");
                    observer.unobserve(entry.target);
                });
            },
            { threshold: 0.2, rootMargin: "0px 0px -8% 0px" }
        );

        reveals.forEach(function (el) {
            observer.observe(el);
        });
    }

    /* —— Stat counters —— */
    function formatCount(value, el) {
        var format = el.getAttribute("data-count-format");
        var prefix = el.getAttribute("data-count-prefix") || "";
        var suffix = el.getAttribute("data-count-suffix") || "";
        var decimals = parseInt(el.getAttribute("data-count-decimals") || "0", 10);

        if (format === "compact-plus") {
            if (value >= 1000) {
                return Math.round(value / 1000) + "k+";
            }
            return Math.round(value) + "+";
        }

        if (decimals > 0) {
            return prefix + value.toFixed(decimals) + suffix;
        }

        return prefix + Math.round(value) + suffix;
    }

    function animateCounter(el) {
        if (el.dataset.counted === "1") return;
        el.dataset.counted = "1";

        var end = parseFloat(el.getAttribute("data-count-end") || "0", 10);
        var duration = 1200;
        var startTime = null;

        function tick(now) {
            if (!startTime) startTime = now;
            var progress = Math.min((now - startTime) / duration, 1);
            var eased = 1 - Math.pow(1 - progress, 3);
            var current = end * eased;
            el.textContent = formatCount(current, el);
            if (progress < 1) {
                requestAnimationFrame(tick);
            } else {
                el.textContent = formatCount(end, el);
            }
        }

        if (reduceMotion) {
            el.textContent = formatCount(end, el);
            return;
        }

        requestAnimationFrame(tick);
    }

    function initCounters() {
        var cards = document.querySelectorAll("[data-stat-card]");
        if (!cards.length) return;

        var observer = new IntersectionObserver(
            function (entries) {
                entries.forEach(function (entry) {
                    if (!entry.isIntersecting) return;
                    var valueEl = entry.target.querySelector("[data-count-end]");
                    if (valueEl) animateCounter(valueEl);
                    observer.unobserve(entry.target);
                });
            },
            { threshold: 0.35 }
        );

        cards.forEach(function (card) {
            observer.observe(card);
        });
    }

    /* —— Floating arch parallax —— */
    function initArchParallax() {
        var mid = document.querySelector(".landing-mid");
        var arches = document.querySelectorAll(".landing-mid__arch");
        if (!mid || !arches.length || reduceMotion) return;

        function onScroll() {
            var rect = mid.getBoundingClientRect();
            var viewH = window.innerHeight;
            if (rect.bottom < 0 || rect.top > viewH) return;

            var progress = 1 - (rect.top + rect.height * 0.5) / (viewH + rect.height * 0.5);
            var scrollY = window.scrollY;

            arches.forEach(function (arch, i) {
                var factor = 0.04 + i * 0.02;
                var drift = (progress - 0.5) * 40 + scrollY * factor * (i % 2 === 0 ? 1 : -1);
                arch.style.setProperty("--arch-drift", drift + "px");
            });
        }

        window.addEventListener("scroll", onScroll, { passive: true });
        onScroll();
    }

    /* —— Flash toast: auto-dismiss after 5s —— */
    function initFlashToast() {
        var stack = document.querySelector(".landing-flash");
        if (!stack) return;

        var flashes = stack.querySelectorAll(".flash");
        flashes.forEach(function (flash) {
            flash.classList.add("landing-toast");
            flash.setAttribute("role", "alert");

            var dismiss = function () {
                flash.classList.add("landing-toast--out");
                setTimeout(function () {
                    if (flash.parentNode) flash.parentNode.removeChild(flash);
                }, 400);
            };

            var closeBtn = document.createElement("button");
            closeBtn.type = "button";
            closeBtn.className = "landing-toast__close";
            closeBtn.setAttribute("aria-label", "Dismiss");
            closeBtn.textContent = "\u00d7";
            closeBtn.addEventListener("click", dismiss);
            flash.appendChild(closeBtn);

            setTimeout(dismiss, 5000);
        });
    }

    initReveals();
    initCounters();
    initArchParallax();
    initFlashToast();
})();
