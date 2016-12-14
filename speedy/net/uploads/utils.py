

def uuid_dir(instance, filename):
    str_id = str(instance.id)
    return '/'.join([
        str_id[:1],
        str_id[:2],
        str_id[:4],
        filename,
    ])


