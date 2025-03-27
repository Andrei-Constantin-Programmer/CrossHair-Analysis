class FakeSettings:
    """
    A minimal stand-in for django.conf.settings to avoid ImproperlyConfigured errors.

    This class is used in environments (e.g., during CrossHair symbolic analysis)
    where Django is not fully installed or configured. It provides only those
    attributes that your code references. If additional settings keys are needed,
    add them here or remove references to them in your code.
    """
    REST_FRAMEWORK = {}
    DEFAULT_CHARSET = "utf-8"
