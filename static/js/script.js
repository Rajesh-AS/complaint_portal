// Complaint Portal — Minimal JS

document.addEventListener('DOMContentLoaded', function () {

    // --- Mobile nav toggle ---
    const toggle = document.querySelector('.nav-toggle');
    const navLinks = document.querySelector('.navbar-links');
    if (toggle && navLinks) {
        toggle.addEventListener('click', function () {
            navLinks.classList.toggle('open');
        });
    }

    // --- Flash message dismiss ---
    document.querySelectorAll('.flash-close').forEach(function (btn) {
        btn.addEventListener('click', function () {
            const msg = btn.closest('.flash-msg');
            if (msg) {
                msg.style.opacity = '0';
                msg.style.transform = 'translateY(-10px)';
                setTimeout(function () { msg.remove(); }, 300);
            }
        });
    });

    // Auto-dismiss flash messages after 5 seconds
    document.querySelectorAll('.flash-msg').forEach(function (msg) {
        setTimeout(function () {
            msg.style.opacity = '0';
            msg.style.transform = 'translateY(-10px)';
            setTimeout(function () { msg.remove(); }, 300);
        }, 5000);
    });

});
