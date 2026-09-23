"""
Users app configuration
"""

from django.apps import AppConfig


class UsersConfig(AppConfig):
    """
    Configuration for users app
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'users'
    verbose_name = 'User Management'
    
    def ready(self):
        """
        Initialize app when Django starts
        This is called once when Django loads the app
        """
        # Import and initialize Firebase Admin SDK
        try:
            from .utils import initialize_firebase
            initialize_firebase()
        except Exception as e:
            print(f"Warning: Failed to initialize Firebase: {str(e)}")
            print("Firebase authentication will not be available.")
        
        # Auto-optimize uploaded videos for mobile streaming
        from .video_processing import connect_signals
        connect_signals()

        # Import signals if you have any
        # import users.signals