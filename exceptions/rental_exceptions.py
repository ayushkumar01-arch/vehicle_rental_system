class RentalSystemError(Exception):
    """Base exception for the rental system."""


class ValidationError(RentalSystemError):
    """Raised when user input or object data is invalid."""


class VehicleUnavailableError(RentalSystemError):
    """Raised when a vehicle is already rented or unavailable."""


class InvalidRentalDurationError(RentalSystemError):
    """Raised when rental days are zero or negative."""


class PaymentFailedError(RentalSystemError):
    """Raised when payment processing fails."""


class RentalNotFoundError(RentalSystemError):
    """Raised when a rental cannot be found."""


class InvalidReturnDateError(RentalSystemError):
    """Raised when a return date is invalid."""
