from django.contrib.auth.hashers import PBKDF2PasswordHasher


def patch():
    def must_update(self, encoded):
        algorithm, iterations, salt, hash = encoded.split('$', 3)
        if int(iterations) == 180000:  # Django 3.0.6
            extra_iterations = self.iterations - int(iterations)
            return extra_iterations < 0  # Can harden_runtime
        return int(iterations) != self.iterations

    PBKDF2PasswordHasher.must_update = must_update
