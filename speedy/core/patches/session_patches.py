from django.contrib.auth.hashers import PBKDF2PasswordHasher


def patch():
    PBKDF2PasswordHasher.iterations = 180000  # Django 3.0.6
