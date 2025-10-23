from django.apps import AppConfig

class LessonsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'tsp'
    
    def ready(self) -> None:
        import tsp.signals
        return super().ready()