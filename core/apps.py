from django.apps import AppConfig


class CoreConfig(AppConfig):
    """
    Configuration class for the 'core' application.

    This class sets up the core application and ensures that signals
    are imported when the application is ready.
    """

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core'

    def ready(self):
        """
        Import signal handlers when the application is ready.

        This ensures that all defined signals in 'core.signals' are connected
        properly and will be triggered when necessary.
        """
        import core.signals  # Importing signals to register them properly
