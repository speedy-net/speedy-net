import os
import re

from django.core.management.commands import makemessages

# msgmerge always rewrites the "POT-Creation-Date" header line, even when no
# other content in the .po file changed. Ignore that line when deciding
# whether a .po file actually needs to be updated, so that running this
# command again and again doesn't keep producing no-op diffs.
_POT_CREATION_DATE_LINE_RE = re.compile(rb'^"POT-Creation-Date: .*$', re.M)


class Command(makemessages.Command):
    def write_po_file(self, potfile, locale):
        po_filename = os.path.join(os.path.dirname(potfile), locale, "LC_MESSAGES", "%s.po" % self.domain)
        old_bytes = None
        old_stat = None
        if os.path.exists(po_filename):
            with open(po_filename, "rb") as fp:
                old_bytes = fp.read()
            old_stat = os.stat(po_filename)
        super().write_po_file(potfile=potfile, locale=locale)
        if (old_bytes is None) or (not os.path.exists(po_filename)):
            return
        with open(po_filename, "rb") as fp:
            new_bytes = fp.read()
        if new_bytes == old_bytes:
            # Nothing actually changed - keep the original mtime so that
            # compilemessages does not think the .po file is newer than its
            # compiled .mo file and needlessly recompile it.
            os.utime(po_filename, (old_stat.st_atime, old_stat.st_mtime))
            return
        old_without_date = _POT_CREATION_DATE_LINE_RE.sub(b'', old_bytes)
        new_without_date = _POT_CREATION_DATE_LINE_RE.sub(b'', new_bytes)
        if old_without_date == new_without_date:
            # Only the POT-Creation-Date changed - keep the old file (and
            # its mtime) as is, so that compilemessages does not think the
            # .po file is newer than its compiled .mo file and needlessly
            # recompile it.
            with open(po_filename, "wb") as fp:
                fp.write(old_bytes)
            os.utime(po_filename, (old_stat.st_atime, old_stat.st_mtime))


