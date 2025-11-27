// JavaScript principal
document.addEventListener('DOMContentLoaded', function() {
    // Auto-dismiss alerts después de 5 segundos
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(function(alert) {
        setTimeout(function() {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });
    
    // Confirmación para formularios de eliminación
    const deleteForms = document.querySelectorAll('form[onsubmit*="confirm"]');
    deleteForms.forEach(function(form) {
        form.addEventListener('submit', function(e) {
            if (!confirm('¿Estás seguro de que deseas realizar esta acción?')) {
                e.preventDefault();
            }
        });
    });
});

