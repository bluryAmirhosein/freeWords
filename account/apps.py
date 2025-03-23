from django.apps import AppConfig


class AccountConfig(AppConfig):
    """
    Configuration class for the 'account' application.

    This class sets up the account application and ensures that signals
    are imported when the application is ready.
    """

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'account'

    def ready(self):
        """
        Import signal handlers when the application is ready.

        This ensures that all defined signals in 'account.signals' are connected
        properly and will be triggered when necessary.
        """
        import account.signals  # Importing signals to register them properly

