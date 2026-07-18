class BookingError(Exception):
    """Base exception for booking errors."""
    pass


class FlightNotFoundError(BookingError):
    """Raised when a flight is not found."""
    pass


class InsufficientSeatsError(BookingError):
    """Raised when there are not enough seats available."""
    pass


class InvalidSeatClassError(BookingError):
    """Raised when an invalid seat class is provided."""
    pass


class MissingStatusError(BookingError):
    """Raised when required status data is missing from database."""
    pass