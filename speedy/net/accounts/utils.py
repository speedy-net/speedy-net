import random
import string


def generate_id():
    chars = string.digits + string.ascii_lowercase
    chars_without_zero = chars[1:]
    return ''.join(random.choice(chars if i > 0 else chars_without_zero) for i in range(15))
