import os

from django.conf import settings as djsettings
from forum.settings.base import Setting, SettingSet
from django.utils.translation import ugettext_lazy as _

EXPORTER_SET = SettingSet('exporter', _('Exporter settings'), _("Data export settings"), 800)

EXPORTER_BACKUP_STORAGE = Setting('EXPORTER_BACKUP_STORAGE', os.path.join(os.path.dirname(__file__), 'backups'), EXPORTER_SET, dict(
label = _("Backups storage"),
help_text = _("A folder to keep your backups organized.")))

MERGE_MAPPINGS = Setting('MERGE_MAPPINGS', {})