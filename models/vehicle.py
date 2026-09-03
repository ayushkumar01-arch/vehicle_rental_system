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
        fuel_level: float = 100.0,
    ):
        for value, field in [
            (vehicle_id, "Vehicle ID"),
            (registration_number, "Registration number"),
            (brand, "Brand"),
            (model, "Model"),
        ]:
            if not str(value).strip():
                raise ValidationError(f"{field} cannot be empty.")

        if daily_rate <= 0:
            raise ValidationError("Daily rental rate must be greater than zero.")
        if not 0 <= fuel_level <= 100:
            raise ValidationError("Fuel level must be between 0 and 100.")

        self.__vehicle_id = vehicle_id.strip()
        self.__registration_number = registration_number.strip()
        self.__brand = brand.strip()
        self.__model = model.strip()
        self.__daily_rate = float(daily_rate)
        self.__fuel_level = float(fuel_level)
        self.__status = "AVAILABLE"

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
    def fuel_level(self):
        return self.__fuel_level

    @property
    def status(self):
        return self.__status

    @property
    def is_available(self):
        return self.__status == "AVAILABLE"

    @property
    @abstractmethod
    def vehicle_type(self):
        pass

    @abstractmethod
    def calculate_rental_cost(self, days: int) -> float:
        pass

    def _validate_days(self, days: int):
        if not isinstance(days, int) or days <= 0:
            raise InvalidRentalDurationError(
                "Rental days must be greater than zero."
            )

    def set_fuel_level(self, fuel_level: float):
        if not 0 <= fuel_level <= 100:
            raise ValidationError("Fuel level must be between 0 and 100.")
        self.__fuel_level = float(fuel_level)

    def mark_as_rented(self):
        if not self.is_available:
            raise ValidationError(
                f"Vehicle {self.vehicle_id} is already unavailable."
            )
        self.__status = "RENTED"

    def mark_as_available(self):
        self.__status = "AVAILABLE"

    def mark_as_maintenance(self):
        self.__status = "MAINTENANCE"

    def display_details(self) -> str:
        return (
            f"{self.vehicle_id} | {self.vehicle_type:<5} | "
            f"{self.brand} {self.model:<14} | "
            f"Rs. {self.daily_rate:>8,.2f}/day | "
            f"Fuel: {self.fuel_level:>5.1f}% | {self.status}"
        )

    def __str__(self):
        return self.display_details()
