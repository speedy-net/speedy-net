"""
Monkey patch of Django's PBKDF2PasswordHasher for Speedy Core, which increases the number of password hashing iterations and limits which hashes are rehashed.
"""
from django.contrib.auth.hashers import PBKDF2PasswordHasher


def patch():
    """
    Monkey patch PBKDF2PasswordHasher to increase the number of iterations and only rehash passwords that use at most 160,000 iterations.
    """
    def must_update(self, encoded):
        """
        Determine whether the password hash should be upgraded to the current number of iterations.

        :param encoded: The encoded password hash.
        :type encoded: str
        :return: True if the hash's iteration count differs from the current setting and is at most 160,000, False otherwise.
        :rtype: bool
        """
        # Update the stored password only if the current iterations are less than or equal to 160,000.
        decoded = self.decode(encoded=encoded)
        return ((decoded["iterations"] != self.iterations) and (decoded["iterations"] <= 160000))

    PBKDF2PasswordHasher.iterations = 560000
    PBKDF2PasswordHasher.must_update = must_update


