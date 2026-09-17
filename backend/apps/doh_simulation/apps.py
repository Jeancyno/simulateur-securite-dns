from django.apps import AppConfig


class DohSimulationConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.doh_simulation'
    verbose_name = 'DNS over HTTPS Simulation'
