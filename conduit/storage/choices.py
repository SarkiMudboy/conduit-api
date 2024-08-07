from django.db.models import TextChoices
from django.utils.translation import gettext as _


class DriveType(TextChoices):

    PERSONAL = "personal", _("personal")
    SHARED = "shared", _("shared")
