document.addEventListener("DOMContentLoaded", () => {
    // 1. Mobile navigation toggle
    const navToggle = document.getElementById("nav-toggle");
    const primaryNav = document.getElementById("primary-nav");
    if (navToggle && primaryNav) {
        navToggle.addEventListener("click", () => {
            const isOpen = primaryNav.classList.toggle("is-open");
            navToggle.setAttribute("aria-expanded", isOpen ? "true" : "false");
        });
    }

    // 2. Auto-dismiss flash alerts after 5 seconds
    const alerts = document.querySelectorAll(".flash-messages .alert");
    alerts.forEach((alert) => {
        setTimeout(() => {
            alert.style.transition = "opacity 0.3s ease";
            alert.style.opacity = "0";
            setTimeout(() => alert.remove(), 300);
        }, 5000);
    });

    // 3. Quick-fill demo credentials on Login page
    const demoButtons = document.querySelectorAll("[data-demo-email]");
    const emailInput = document.getElementById("email");
    const passwordInput = document.getElementById("password");

    demoButtons.forEach((btn) => {
        btn.addEventListener("click", () => {
            if (emailInput && passwordInput) {
                emailInput.value = btn.getAttribute("data-demo-email");
                passwordInput.value = "Password123!";
                emailInput.focus();
            }
        });
    });
});
