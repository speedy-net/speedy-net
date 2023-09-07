from django.contrib.auth.hashers import PBKDF2PasswordHasher


def patch():
    def must_update(self, encoded):
        # Update the stored password only if the iterations diff is at least 250,000.
        algorithm, iterations, salt, hash = encoded.split('$', 3)
        iterations_diff = abs(self.iterations - int(iterations))
        return ((int(iterations) != self.iterations) and (iterations_diff >= 250000))

    PBKDF2PasswordHasher.iterations = 390000  # Django 4.1.x
    PBKDF2PasswordHasher.must_update = must_update


