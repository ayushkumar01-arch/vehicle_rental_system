from datetime import date

from exceptions.rental_exceptions import (
    InvalidRentalDurationError,
    RentalNotFoundError,
    ValidationError,
    VehicleUnavailableError,
)
from models.rental import Rental


class RentalService:
    """Coordinates vehicles, customers, rentals and payment processors."""

    def __init__(self):
        self.__vehicles = {}  # stores all vehicles
        self.__customers = {} # stores all customers
        self.__rentals = {}   # stores all rentals

    @property
    def vehicles(self):
        # Return a tuple of all vehicles in the system.
        return tuple(self.__vehicles.values())

    @property
    # Return a tuple of all customers in the system.
    def customers(self):
        return tuple(self.__customers.values())

    @property
    def rentals(self):
        # Return a tuple of all rentals in the system.
        return tuple(self.__rentals.values())

    def add_vehicle(self, vehicle):
        if vehicle.vehicle_id in self.__vehicles:
            raise ValidationError(f"Vehicle ID {vehicle.vehicle_id} already exists.")
        self.__vehicles[vehicle.vehicle_id] = vehicle

    def register_customer(self, customer):
        if customer.customer_id in self.__customers:
            raise ValidationError(
                f"Customer ID {customer.customer_id} already exists."
            )
        self.__customers[customer.customer_id] = customer

    def get_vehicle(self, vehicle_id):
        vehicle = self.__vehicles.get(vehicle_id)
        if vehicle is None:
            raise ValidationError(f"Vehicle {vehicle_id} was not found.")
        return vehicle

    def get_customer(self, customer_id):
        customer = self.__customers.get(customer_id)
        if customer is None:
            raise ValidationError(f"Customer {customer_id} was not found.")
        return customer

    def get_rental(self, rental_id):
        rental = self.__rentals.get(rental_id)
        if rental is None:
            raise RentalNotFoundError(f"Rental {rental_id} was not found.")
        return rental

    def search_vehicles(self, vehicle_type=None, max_price=None, vehicle_id=None):
        """Overload-style search using optional filters: ID, type, price.
        1. vehicle_id → search a specific vehicle
        2. vehicle_type → search by type like Car/Bike/Van
        3. max_price → search vehicles below a certain price
        """
        results = list(self.__vehicles.values())

        # Did the user provide a vehicle ID?
        if vehicle_id:
            results = [
                # Go through every vehicle and keep only the vehicle whose ID matches.
                v for v in results
                if v.vehicle_id.lower() == vehicle_id.lower()
            ]

        if vehicle_type:
            results = [
                v for v in results
                if v.vehicle_type.lower() == vehicle_type.lower()
            ]

        if max_price is not None:
            results = [v for v in results if v.daily_rate <= max_price]

        return results

    def rent_vehicle(
        self,
        customer_id: str,
        vehicle_id: str,
        days: int,
        payment_processor,
        start_date: date | None = None,
    ):
        if days <= 0:
            raise InvalidRentalDurationError(
                "Rental days must be greater than zero."
            )

        customer = self.get_customer(customer_id)
        vehicle = self.get_vehicle(vehicle_id)

        if not vehicle.is_available:
            raise VehicleUnavailableError(
                f"Vehicle {vehicle.vehicle_id} is currently unavailable."
            )

        # Polymorphism: this calls Car/Bike/Van implementation.
        amount = vehicle.calculate_rental_cost(days)

        # Payment MUST succeed before the vehicle is marked as rented.
        payment_result = payment_processor.process_payment(amount)

        if payment_result.get("status") != "SUCCESS":
            raise ValidationError("Payment was not successful.")

        vehicle.mark_as_rented()

        rental_id = f"R{len(self.__rentals) + 1:03d}"
        rental = Rental(
            rental_id=rental_id,
            customer=customer,
            vehicle=vehicle,
            days=days,
            payment=payment_result,
            start_date=start_date,
        )

        self.__rentals[rental_id] = rental
        customer.add_rental(rental)

        return rental

    def return_vehicle(self, rental_id: str, return_date: date):
        rental = self.get_rental(rental_id)

        if rental.status == "RETURNED":
            raise ValidationError("This vehicle has already been returned.")

        invoice = rental.complete_rental(return_date)
        return invoice

    def active_rentals(self):
        return [r for r in self.__rentals.values() if r.status == "ACTIVE"]
