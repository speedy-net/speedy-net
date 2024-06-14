from django.contrib.auth.hashers import PBKDF2PasswordHasher


def patch():
    def must_update(self, encoded):
        # Update the stored password only if the current iterations are less than or equal to 140,000.
        decoded = self.decode(encoded=encoded)
        return ((decoded["iterations"] != self.iterations) and (decoded["iterations"] <= 140000))

    PBKDF2PasswordHasher.iterations = 480000
    PBKDF2PasswordHasher.must_update = must_update


