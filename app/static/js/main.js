document.addEventListener("DOMContentLoaded", () => {
    // 1. Mobile navigation toggle
    const navToggle = document.getElementById("nav-toggle");
    const primaryNav = document.getElementById("primary-nav");
    if (navToggle && primaryNav) {
        navToggle.addEventListener("click", () => {
            const isOpen = primaryNav.classList.toggle("is-open");
            navToggle.setAttribute("aria-expanded", isOpen ? "true" : "false");
        });

        primaryNav.addEventListener("click", (event) => {
            if (event.target.closest("a") && window.matchMedia("(max-width: 767px)").matches) {
                primaryNav.classList.remove("is-open");
                navToggle.setAttribute("aria-expanded", "false");
            }
        });
    }

    // 2. Animate capacity indicators from empty to their current value.
    const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    if (!reduceMotion) {
        document.querySelectorAll(".capacity-progress").forEach((progress) => {
            const targetValue = Number(progress.value);
            if (targetValue > 0) {
                progress.value = 0;
                requestAnimationFrame(() => {
                    requestAnimationFrame(() => { progress.value = targetValue; });
                });
            }
        });
    }

    // 3. Auto-dismiss flash alerts after 5 seconds with a brief fade.
    const alerts = document.querySelectorAll(".flash-messages .alert");
    alerts.forEach((alert) => {
        setTimeout(() => {
            alert.classList.add("is-dismissing");
            setTimeout(() => alert.remove(), reduceMotion ? 0 : 250);
        }, 5000);
    });

    // 4. Prevent accidental duplicate submissions on ticket booking.
    const bookingForm = document.querySelector("form[action*='/book/']");
    if (bookingForm) {
        bookingForm.addEventListener("submit", () => {
            const submitButton = bookingForm.querySelector("button[type='submit']");
            if (submitButton) {
                submitButton.disabled = true;
                submitButton.setAttribute("aria-busy", "true");
                submitButton.textContent = "Booking…";
            }
        });
    }

});
