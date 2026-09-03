class RentalSystemError(Exception):
    """Base exception for the rental system."""


class ValidationError(RentalSystemError):
    """Raised when user input or object data is invalid."""


class VehicleUnavailableError(RentalSystemError):
    """Raised when a vehicle is unavailable for the requested period."""


class InvalidRentalDurationError(RentalSystemError):
    """Raised when rental days are zero or negative."""


class PaymentFailedError(RentalSystemError):
    """Raised when payment processing fails."""


class RentalNotFoundError(RentalSystemError):
    """Raised when a rental cannot be found."""


class InvalidReturnDateError(RentalSystemError):
    """Raised when a return/cancellation date is invalid."""


class ReservationNotFoundError(RentalSystemError):
    """Raised when a reservation cannot be found."""
