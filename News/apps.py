from django.apps import AppConfig


class NewsConfig(AppConfig):
    '''Load and register signal handlers when Django is started up.'''
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'News'

    def ready(self):
        import News.signals
