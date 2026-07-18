document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('.alert').forEach((alert) => {
        setTimeout(() => {
            alert.classList.remove('show');
            alert.classList.add('fade');
        }, 4000);
    });
});
