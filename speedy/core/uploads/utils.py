import hashlib
import os


def uuid_dir(instance, filename):
    str_id = str(instance.id)
    stem = hashlib.md5('$$$-{}-$$$'.format(instance.id).encode('utf-8')).hexdigest()
    _, extension = os.path.splitext(filename)
    filename = '{}{}'.format(stem, extension.lower())
    return '/'.join([
        str_id[:1],
        str_id[:2],
        str_id[:4],
        filename,
    ])


