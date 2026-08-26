from abc import ABC, abstractmethod

from exceptions.rental_exceptions import (
    InvalidRentalDurationError,
    ValidationError,
)


class Vehicle(ABC):
    """Abstract base class for every rentable vehicle."""

    def __init__(
        self,
        vehicle_id: str,
        registration_number: str,
        brand: str,
        model: str,
        daily_rate: float,
    ):
        self.__validate_text(vehicle_id, "Vehicle ID")
        self.__validate_text(registration_number, "Registration number")
        self.__validate_text(brand, "Brand")
        self.__validate_text(model, "Model")

        if daily_rate <= 0:
            raise ValidationError("Daily rental rate must be greater than zero.")

        self.__vehicle_id = vehicle_id.strip()
        self.__registration_number = registration_number.strip()
        self.__brand = brand.strip()
        self.__model = model.strip()
        self.__daily_rate = float(daily_rate)
        self.__available = True

    @staticmethod
    def __validate_text(value, field_name):
        if not str(value).strip():
            raise ValidationError(f"{field_name} cannot be empty.")

    @property
    def vehicle_id(self):
        return self.__vehicle_id

    @property
    def registration_number(self):
        return self.__registration_number

    @property
    def brand(self):
        return self.__brand

    @property
    def model(self):
        return self.__model

    @property
    def daily_rate(self):
        return self.__daily_rate

    @property
    def is_available(self):
        return self.__available

    @property
    @abstractmethod
    def vehicle_type(self):
        """Return the vehicle type."""

    @abstractmethod
    def calculate_rental_cost(self, days: int) -> float:
        """Calculate rental cost using vehicle-specific rules."""

    def _validate_days(self, days: int):
        if not isinstance(days, int) or days <= 0:
            raise InvalidRentalDurationError(
                "Rental days must be greater than zero."
            )

    def mark_as_rented(self):
        if not self.__available:
            raise ValidationError(
                f"Vehicle {self.vehicle_id} is already unavailable."
            )
        self.__available = False

    def mark_as_available(self):
        self.__available = True

    def display_details(self) -> str:
        status = "Available" if self.is_available else "Rented/Unavailable"
        return (
            f"{self.vehicle_id} | {self.vehicle_type} | "
            f"{self.brand} {self.model} | "
            f"Rs. {self.daily_rate:,.2f}/day | {status}"
        )

    def __str__(self):
        return self.display_details()
