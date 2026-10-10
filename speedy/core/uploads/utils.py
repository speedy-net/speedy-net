"""
Utilities of the Speedy Core uploads app (the function which builds the upload path of a file).
"""
import hashlib
import os


def uuid_dir(instance, filename):
    """
    Build the upload path for a file instance, based on a SHA-384 hash of its id, to spread files across directories and obscure the original filename.

    :param instance: The model instance the file is being uploaded for.
    :type instance: speedy.core.uploads.models.File
    :param filename: The original filename being uploaded.
    :type filename: str
    :return: The relative upload path for the file, including the hashed filename.
    :rtype: str
    """
    if (not (instance.id) and (hasattr(instance, 'generate_id_if_needed'))):
        instance.generate_id_if_needed()

    str_id = str(instance.id)
    stem_sha384 = hashlib.sha384('$$$-{}-$$$'.format(instance.id).encode('utf-8')).hexdigest()
    assert (len(stem_sha384) == 96)
    assert (stem_sha384 == stem_sha384.lower())
    stem = stem_sha384[-32:]
    assert (len(stem) == 32)
    assert (stem == stem.lower())
    _, extension = os.path.splitext(filename)
    filename = '{}{}'.format(stem, extension.lower())
    return '/'.join([
        str_id[:1],
        str_id[:2],
        str_id[:4],
        filename,
    ])


