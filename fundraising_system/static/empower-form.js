(function () {
    const root = document.querySelector("[data-emp-form]");
    if (!root) return;

    const formEl = root.querySelector("form");
    const panels = Array.from(root.querySelectorAll("[data-emp-step]"));
    const btnNext = root.querySelector("[data-emp-next]");
    const btnBack = root.querySelector("[data-emp-back]");
    const btnSubmit = root.querySelector("[data-emp-submit]");
    const isEmbed = document.body.classList.contains("emp-form-embed");
    let step = 1;

    function notifyParentSuccess() {
        window.parent.postMessage("emp-form-success", "*");
    }

    root.querySelectorAll(".emp-field input, .emp-field textarea, .emp-field select").forEach((el) => {
        const field = el.closest(".emp-field");
        const sync = () => field?.classList.toggle("is-filled", !!el.value);
        el.addEventListener("input", sync);
        el.addEventListener("change", sync);
        sync();
    });

    function updateActionButtons() {
        const onLastStep = step === panels.length;
        btnNext.classList.toggle("is-hidden", onLastStep);
        btnSubmit.classList.toggle("is-hidden", !onLastStep);

        if (btnBack) {
            if (isEmbed) {
                btnBack.hidden = false;
                btnBack.textContent = step === 1 ? "Cancel" : "Back";
            } else {
                btnBack.hidden = step === 1;
            }
        }
    }

    function showStep(next) {
        const current = root.querySelector(`[data-emp-step="${step}"]`);
        const target = root.querySelector(`[data-emp-step="${next}"]`);
        if (!target || next === step) return;

        current?.classList.add("is-exiting");
        setTimeout(() => {
            current?.classList.remove("is-active", "is-exiting");
            step = next;
            root.setAttribute("data-step", String(step));
            target.classList.add("is-active");
            updateActionButtons();
        }, step < next ? 280 : 0);
    }

    updateActionButtons();

    btnNext?.addEventListener("click", () => {
        const panel = root.querySelector(`[data-emp-step="${step}"]`);
        const fields = panel?.querySelectorAll("input, textarea, select") || [];
        for (const field of fields) {
            if (!field.checkValidity()) {
                field.reportValidity();
                return;
            }
        }
        showStep(step + 1);
    });

    btnBack?.addEventListener("click", () => {
        if (step === 1 && isEmbed) {
            window.parent.postMessage("emp-portal-close", "*");
            return;
        }
        showStep(step - 1);
    });

    if (btnBack && isEmbed) {
        btnBack.hidden = false;
        btnBack.textContent = "Cancel";
    }

    document.querySelectorAll(".emp-form-btn--magnetic").forEach((btn) => {
        btn.addEventListener("mousemove", (e) => {
            const r = btn.getBoundingClientRect();
            btn.style.transform = `translate(${(e.clientX - r.left - r.width / 2) * 0.1}px, ${(e.clientY - r.top - r.height / 2) * 0.1}px)`;
        });
        btn.addEventListener("mouseleave", () => {
            btn.style.transform = "";
        });
    });

    formEl?.addEventListener("submit", async (e) => {
        if (!isEmbed) return;

        e.preventDefault();
        if (!formEl.reportValidity()) return;

        const submitBtn = btnSubmit;
        submitBtn.disabled = true;
        submitBtn.classList.add("is-loading");

        const action = formEl.getAttribute("action") || window.location.pathname;
        const url = action.includes("embed=1") ? action : action + (action.includes("?") ? "&" : "?") + "embed=1";

        try {
            const res = await fetch(url, {
                method: "POST",
                body: new FormData(formEl),
                headers: {
                    "X-Emp-Form": "1",
                    Accept: "application/json",
                },
                credentials: "same-origin",
                redirect: "manual",
            });

            if (res.type === "opaqueredirect" || res.status === 302 || res.status === 303) {
                notifyParentSuccess();
                return;
            }

            const contentType = res.headers.get("content-type") || "";
            if (contentType.includes("application/json")) {
                const data = await res.json();
                if (data.success) {
                    submitBtn.classList.remove("is-loading");
                    submitBtn.classList.add("is-success");
                    setTimeout(notifyParentSuccess, 400);
                } else {
                    submitBtn.classList.remove("is-loading");
                    submitBtn.disabled = false;
                    alert(data.message || "Could not save. Please try again.");
                }
                return;
            }

            if (res.ok) {
                notifyParentSuccess();
                return;
            }

            throw new Error("Unexpected response");
        } catch (err) {
            submitBtn.classList.remove("is-loading");
            submitBtn.disabled = false;
            alert("Something went wrong. Please try again.");
        }
    });
})();
