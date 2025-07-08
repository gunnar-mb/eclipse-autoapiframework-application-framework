"""
vaf.exceptions
~~~~~~~~~~~~~~~~~~~

This module contains the set of vaf' exceptions.
"""


class VafProjectTemplateError(Exception):
    """Exception class for specific error handling regarding project template errors"""

    def __init__(self, message: str, error_code: int = 0) -> None:
        """
        Initialize VafProjectTemplateError with a message and optional error code.

        :param message: The error message.
        :param error_code: An optional error code.
        """
        super().__init__(message)
        self.error_code = error_code


class VafProjectGenerationError(Exception):
    """Exception class for specific error handling regarding project generation errors"""

    def __init__(self, message: str, error_code: int = 0) -> None:
        """
        Initialize VafProjectGenerationError with a message and optional error code.

        :param message: The error message.
        :param error_code: An optional error code.
        """
        super().__init__(message)
        self.error_code = error_code
