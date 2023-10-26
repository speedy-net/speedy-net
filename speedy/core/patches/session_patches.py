from django.contrib.auth.hashers import PBKDF2PasswordHasher


def patch():
    def must_update(self, encoded):
        # Update the stored password only if the iterations diff is at least 250,000.
        decoded = self.decode(encoded)
        iterations_diff = abs(self.iterations - decoded["iterations"])
        return ((decoded["iterations"] != self.iterations) and (iterations_diff >= 250000))

    PBKDF2PasswordHasher.iterations = 390000  # Django 4.1.x
    PBKDF2PasswordHasher.must_update = must_update


