"""
Exceptions related to the handling of identity proofs.
"""


class FileValidationError(Exception):
    """
    Exception to use when the system rejects a user-supplied source image or pdf.
    """
    @property
    def user_message(self):
        """
        Translate the developer-facing exception message for API clients.
        """
        return self.message
