import django.conf

class FakeSettings:
    """
    A minimal stand-in for django.conf.settings to avoid ImproperlyConfigured errors.

    This class is used in environments (e.g., during CrossHair symbolic analysis)
    where Django is not fully installed or configured. It provides only those
    attributes that your code references.
    """
    REST_FRAMEWORK = {
        "DEFAULT_CONTENT_NEGOTIATION_CLASS": "dataset.request.utils.negotiation.DefaultContentNegotiation",
        'UNAUTHENTICATED_USER': lambda: None,
        'UNAUTHENTICATED_TOKEN': lambda: None,
    }
    DEFAULT_CHARSET = "utf-8"

    configured = False

    def configure(self, **options) -> None:
        """
        Stub method to mimic django.conf.settings.configure().
        Setting 'configured' to True helps prevent 'ImproperlyConfigured' checks.
        Any keyword arguments are mapped to attributes on this FakeSettings object.
        """
        self.configured = True
        for key, value in options.items():
            setattr(self, key, value)

    def __getattr__(self, _: str):
        """
        Fallback for any settings attributes not explicitly defined.
        Returns None if an attribute doesn't exist, which can handle
        code that checks for 'DEBUG', etc.
        """
        return None

django.conf.settings = FakeSettings