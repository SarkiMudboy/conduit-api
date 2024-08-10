from rest_framework.throttling import AnonRateThrottle


class PasswordThrottle(AnonRateThrottle):
    """Rate limiting for password recovery resources"""

    rate = "2/minute"