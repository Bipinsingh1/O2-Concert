from django.apps import AppConfig


class QrScannerConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'backend.qr_scanner'
    label = 'qr_scanner'
    verbose_name = 'QR Scanner'
