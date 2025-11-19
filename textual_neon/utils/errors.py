class Errors:
    """A container class for all exceptions unique to textual-neon."""

    class NeonError(Exception):
        """Base class for all exceptions unique to textual-neon."""

    class ProcessingError(NeonError):
        """
        Raised when an error occurs during data processing.
        Used in the LoadingScreen to shut processing down.
        """

    class DuplicateError(NeonError):
        """
        Raised when a duplicate item is found during data processing.
        Used in the LoadingScreen, where it writes a special log instead of breaking
        the loop like ProcessingError does.
        """

    class BadInput(NeonError):
        """Raised when an input validation fails with improper handling."""