/**
 * Script mínimo para o portal OPA.
 * Uso: auto-dismiss de alertas flash (complementar ao Bootstrap).
 */
(function () {
  'use strict';
  var alerts = document.querySelectorAll('.alert-dismissible');
  if (alerts.length) {
    alerts.forEach(function (alert) {
      setTimeout(function () {
        var bsAlert = bootstrap.Alert.getOrCreateInstance(alert);
        if (bsAlert) bsAlert.close();
      }, 5000);
    });
  }
})();
