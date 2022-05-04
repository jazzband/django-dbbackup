import re

from django.core.checks import Tags, Warning, register

from dbbackup import settings

W001 = Warning(
    "Invalid HOSTNAME parameter",
    hint="Set a non empty string to this settings.DBBACKUP_HOSTNAME",
    id="dbbackup.W001",
)
W002 = Warning(
    "Invalid STORAGE parameter",
    hint="Set a valid path to a storage in settings.DBBACKUP_STORAGE",
    id="dbbackup.W002",
)
W003 = Warning(
    "Invalid FILENAME_TEMPLATE parameter",
    hint="Include {datetime} to settings.DBBACKUP_FILENAME_TEMPLATE",
    id="dbbackup.W003",
)
W004 = Warning(
    "Invalid MEDIA_FILENAME_TEMPLATE parameter",
    hint="Include {datetime} to settings.DBBACKUP_MEDIA_FILENAME_TEMPLATE",
    id="dbbackup.W004",
)
W005 = Warning(
    "Invalid DATE_FORMAT parameter",
    hint="settings.DBBACKUP_DATE_FORMAT can contain only [A-Za-z0-9%_-]",
    id="dbbackup.W005",
)
W006 = Warning(
    "FAILURE_RECIPIENTS has been deprecated",
    hint="settings.DBBACKUP_FAILURE_RECIPIENTS is replaced by "
    "settings.DBBACKUP_ADMINS",
    id="dbbackup.W006",
)


@register(Tags.compatibility)
def check_settings(app_configs, **kwargs):
    errors = []
    if not settings.HOSTNAME:
        errors.append(W001)

    if not settings.STORAGE or not isinstance(settings.STORAGE, str):
        errors.append(W002)

    if (
        not callable(settings.FILENAME_TEMPLATE)
        and "{datetime}" not in settings.FILENAME_TEMPLATE
    ):
        errors.append(W003)

    if (
        not callable(settings.MEDIA_FILENAME_TEMPLATE)
        and "{datetime}" not in settings.MEDIA_FILENAME_TEMPLATE
    ):
        errors.append(W004)

    if re.search(r"[^A-Za-z0-9%_-]", settings.DATE_FORMAT):
        errors.append(W005)

    if getattr(settings, "FAILURE_RECIPIENTS", None) is not None:
        errors.append(W006)

    return errors
