import json
from datetime import date, datetime, timedelta
from pathlib import Path

from exceptions.rental_exceptions import (
    InvalidRentalDurationError,
    RentalNotFoundError,
    ReservationNotFoundError,
    ValidationError,
    VehicleUnavailableError,
)
from models.bike import Bike
from models.car import Car
from models.rental import Rental
from models.reservation import Reservation
from models.van import Van


class RentalService:
    """Main business layer. Data is automatically saved to JSON."""

    DATA_FILE = Path(__file__).resolve().parent.parent / "data" / "rental_data.json"

    def __init__(self):
        self.__vehicles = {}    # all vehicles
        self.__customers = {}   # all customers
        self.__rentals = {}     # all rentals
        self.__reservations = {}
        self.load_data()

    @property
    def vehicles(self): return tuple(self.__vehicles.values())
    @property
    def customers(self): return tuple(self.__customers.values())
    @property
    def rentals(self): return tuple(self.__rentals.values())
    @property
    def reservations(self): return tuple(self.__reservations.values())

    def add_vehicle(self, vehicle):
        if vehicle.vehicle_id in self.__vehicles:
            raise ValidationError(f"Vehicle ID {vehicle.vehicle_id} already exists.")
        self.__vehicles[vehicle.vehicle_id] = vehicle
        self.save_data()

    def register_customer(self, customer):

        # check if that customer id already exists
        if customer.customer_id in self.__customers:
            raise ValidationError(f"Customer ID {customer.customer_id} already exists.")

        '''
        self.__customers[customer.customer_id] = customer
            - by using customer.customer_id fetch id and use it as key
            - other details save as value in dictionary
        '''
        self.__customers[customer.customer_id] = customer
        self.save_data()

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

    def get_reservation(self, reservation_id):
        reservation = self.__reservations.get(reservation_id)
        if reservation is None:
            raise ReservationNotFoundError(f"Reservation {reservation_id} was not found.")
        return reservation

    def search_vehicles(self, vehicle_type=None, max_price=None, vehicle_id=None):
        results = list(self.__vehicles.values())
        if vehicle_id:
            results = [v for v in results if v.vehicle_id.lower() == vehicle_id.lower()]
        if vehicle_type:
            results = [v for v in results if v.vehicle_type.lower() == vehicle_type.lower()]
        if max_price is not None:
            results = [v for v in results if v.daily_rate <= max_price]
        return results

    @staticmethod
    def _date_overlap(start1, end1, start2, end2):
        return start1 < end2 and end1 > start2

    def is_vehicle_available(self, vehicle_id, start_date, end_date):
        vehicle = self.get_vehicle(vehicle_id)
        if vehicle.status in {"MAINTENANCE", "RENTED"}:
            return False

        for reservation in self.__reservations.values():
            if reservation.vehicle.vehicle_id == vehicle_id and reservation.overlaps(start_date, end_date):
                return False

        for rental in self.__rentals.values():
            if rental.vehicle.vehicle_id != vehicle_id or rental.status not in {"ACTIVE"}:
                continue
            if self._date_overlap(start_date, end_date, rental.start_date, rental.due_date):
                return False
        return True

    def available_vehicles(self, start_date, end_date):
        return [
            v for v in self.__vehicles.values()
            if self.is_vehicle_available(v.vehicle_id, start_date, end_date)
        ]

    def rent_vehicle(self, customer_id, vehicle_id, days, payment_processor, start_date=None, pickup_fuel=None):
        if days <= 0:
            raise InvalidRentalDurationError("Rental days must be greater than zero.")
        start_date = start_date or date.today()

        # this is check weather the start date is today or not
        # for future pickup date, we should use reservation instead of direct rental
        if start_date != date.today():
            raise ValidationError("Use a reservation for a future pickup date.")
        end_date = start_date
        from datetime import timedelta
        end_date += timedelta(days=days)

        customer = self.get_customer(customer_id)
        vehicle = self.get_vehicle(vehicle_id)
        if not self.is_vehicle_available(vehicle_id, start_date, end_date):
            raise VehicleUnavailableError(
                f"Vehicle {vehicle.vehicle_id} is unavailable for {start_date} to {end_date}."
            )

        amount = vehicle.calculate_rental_cost(days)
        payment_result = payment_processor.process_payment(amount)
        if payment_result.get("status") != "SUCCESS":
            raise ValidationError("Payment was not successful.")

        vehicle.mark_as_rented()
        if pickup_fuel is not None:
            vehicle.set_fuel_level(pickup_fuel)

        rental_id = self._next_id("R", self.__rentals)
        rental = Rental(
            rental_id=rental_id,
            customer=customer,
            vehicle=vehicle,
            days=days,
            payment=payment_result,
            start_date=start_date,
            pickup_fuel=vehicle.fuel_level,
        )
        self.__rentals[rental_id] = rental
        customer.add_rental(rental)
        self.save_data()
        return rental

    def make_reservation(self, customer_id, vehicle_id, start_date, end_date, payment_processor):
        if end_date <= start_date:
            raise ValidationError("Return date must be after pickup date.")
        customer = self.get_customer(customer_id)
        vehicle = self.get_vehicle(vehicle_id)

        if not self.is_vehicle_available(vehicle_id, start_date, end_date):
            raise VehicleUnavailableError(
                f"Vehicle {vehicle_id} is already booked/unavailable for these dates."
            )

        days = (end_date - start_date).days
        amount = vehicle.calculate_rental_cost(days)
        payment_result = payment_processor.process_payment(amount)
        if payment_result.get("status") != "SUCCESS":
            raise ValidationError("Payment was not successful.")

        # It generates a new reservation ID
        reservation_id = self._next_id("RS", self.__reservations)
        reservation = Reservation(
            reservation_id, customer, vehicle, start_date, end_date, amount, payment_result
        )
        self.__reservations[reservation_id] = reservation
        self.save_data()
        return reservation

    def cancel_reservation(self, reservation_id, payment_processor):
        reservation = self.get_reservation(reservation_id)
        reservation.cancel()
        refund = payment_processor.refund_payment(reservation.amount)
        self.save_data()
        return refund

    def start_reservation(self, reservation_id, pickup_date=None, pickup_fuel=None):
        reservation = self.get_reservation(reservation_id)
        pickup_date = pickup_date or date.today()
        if reservation.status != "CONFIRMED":
            raise ValidationError("This reservation is not active.")
        if pickup_date < reservation.start_date or pickup_date >= reservation.end_date:
            raise ValidationError(
                f"Pickup must be between {reservation.start_date} and {reservation.end_date - timedelta(days=1)}."
            )

        vehicle = reservation.vehicle
        if not vehicle.is_available:
            raise VehicleUnavailableError("Vehicle is currently unavailable.")

        vehicle.mark_as_rented()
        remaining_days = (reservation.end_date - pickup_date).days
        rental_id = self._next_id("R", self.__rentals)
        rental = Rental(
            rental_id=rental_id,
            customer=reservation.customer,
            vehicle=vehicle,
            days=remaining_days,
            payment=reservation.payment,
            start_date=pickup_date,
            pickup_fuel=vehicle.fuel_level if pickup_fuel is None else pickup_fuel,
        )
        self.__rentals[rental_id] = rental
        reservation.complete()
        reservation.customer.add_rental(rental)
        self.save_data()
        return rental

    def return_vehicle(self, rental_id, return_date, return_fuel, damage_items=None):
        rental = self.get_rental(rental_id)
        invoice = rental.complete_rental(return_date, return_fuel, damage_items)
        self.save_data()
        return invoice

    def cancel_remaining_days(self, rental_id, cancel_date, return_fuel, damage_items, payment_processor):
        rental = self.get_rental(rental_id)
        used_days, remaining_days, possible_refund, extra_due = rental.cancel_remaining_days(
            cancel_date, return_fuel, damage_items
        )
        settlement = None
        if possible_refund > 0 and extra_due == 0:
            settlement = payment_processor.refund_payment(rental.cancellation_refund)
        elif extra_due > 0:
            settlement = payment_processor.process_payment(extra_due)
        self.save_data()
        return rental, used_days, remaining_days, possible_refund, extra_due, settlement

    def active_rentals(self):
        return [r for r in self.__rentals.values() if r.status == "ACTIVE"]

    def active_reservations(self):
        return [r for r in self.__reservations.values() if r.status == "CONFIRMED"]

    def _next_id(self, prefix, items):
        number = len(items) + 1
        while f"{prefix}{number:03d}" in items:
            number += 1
        return f"{prefix}{number:03d}"

    def save_data(self):
        self.DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
        data = {

            # convert the vehicles, customers, rentals, and reservations to dictionaries
            "vehicles": [self._vehicle_to_dict(v) for v in self.__vehicles.values()],
            "customers": [
                {
                    "customer_id": c.customer_id,
                    "name": c.name,
                    "email": c.email,
                    "licence_number": c.licence_number,
                }
                for c in self.__customers.values()
            ],
            "rentals": [self._rental_to_dict(r) for r in self.__rentals.values()],
            "reservations": [self._reservation_to_dict(r) for r in self.__reservations.values()],
        }
        self.DATA_FILE.write_text(json.dumps(data, indent=4), encoding="utf-8")

    def load_data(self):
        if not self.DATA_FILE.exists():
            return
        try:
            data = json.loads(self.DATA_FILE.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return

        self.__vehicles = {}
        self.__customers = {}
        self.__rentals = {}
        self.__reservations = {}

        classes = {"Car": Car, "Bike": Bike, "Van": Van}
        for item in data.get("vehicles", []):
            cls = classes[item["vehicle_type"]]
            vehicle = cls(
                item["vehicle_id"], item["registration_number"], item["brand"],
                item["model"], item["daily_rate"], item.get("fuel_level", 100)
            )
            if item.get("status") == "RENTED":
                vehicle.mark_as_rented()
            elif item.get("status") == "MAINTENANCE":
                vehicle.mark_as_maintenance()
            self.__vehicles[vehicle.vehicle_id] = vehicle

        for item in data.get("customers", []):
            from models.customer import Customer
            customer = Customer(item["customer_id"], item["name"], item["email"], item["licence_number"])
            self.__customers[customer.customer_id] = customer

        # Reservations are loaded before rentals because both refer to vehicles/customers.
        for item in data.get("reservations", []):
            customer = self.get_customer(item["customer_id"])
            vehicle = self.get_vehicle(item["vehicle_id"])
            reservation = Reservation(
                item["reservation_id"], customer, vehicle,
                date.fromisoformat(item["start_date"]), date.fromisoformat(item["end_date"]),
                item["amount"], item["payment"],
            )
            if item["status"] == "CANCELLED":
                reservation.cancel()
            elif item["status"] == "COMPLETED":
                reservation.complete()
            self.__reservations[reservation.reservation_id] = reservation

        for item in data.get("rentals", []):
            customer = self.get_customer(item["customer_id"])
            vehicle = self.get_vehicle(item["vehicle_id"])
            rental = Rental(
                item["rental_id"], customer, vehicle, item["days"], item["payment"],
                date.fromisoformat(item["start_date"]), item.get("pickup_fuel", 100),
            )
            # Restore the old state without hiding persistence details in main.py.
            if item["status"] == "RETURNED":
                rental.complete_rental(
                    date.fromisoformat(item["return_date"]),
                    item.get("return_fuel", item.get("pickup_fuel", 100)),
                    item.get("damage_items", []),
                )
            elif item["status"] == "CANCELLED":
                rental.cancel_remaining_days(
                    date.fromisoformat(item["return_date"]),
                    item.get("return_fuel", item.get("pickup_fuel", 100)),
                    item.get("damage_items", []),
                )
            self.__rentals[rental.rental_id] = rental
            customer.add_rental(rental)

    @staticmethod
    def _vehicle_to_dict(vehicle):
        return {
            "vehicle_id": vehicle.vehicle_id,
            "registration_number": vehicle.registration_number,
            "brand": vehicle.brand,
            "model": vehicle.model,
            "daily_rate": vehicle.daily_rate,
            "fuel_level": vehicle.fuel_level,
            "vehicle_type": vehicle.vehicle_type,
            "status": vehicle.status,
        }

    @staticmethod
    def _rental_to_dict(rental):
        return {
            "rental_id": rental.rental_id,
            "customer_id": rental.customer.customer_id,
            "vehicle_id": rental.vehicle.vehicle_id,
            "days": rental.days,
            "payment": rental.payment,
            "start_date": rental.start_date.isoformat(),
            "due_date": rental.due_date.isoformat(),
            "pickup_fuel": rental.pickup_fuel,
            "return_fuel": rental.return_fuel,
            "return_date": rental.return_date.isoformat() if rental.return_date else None,
            "cancellation_refund": rental.cancellation_refund,
            "status": rental.status,
            "damage_items": list(rental.damage_items),
        }

    @staticmethod
    def _reservation_to_dict(reservation):
        return {
            "reservation_id": reservation.reservation_id,
            "customer_id": reservation.customer.customer_id,
            "vehicle_id": reservation.vehicle.vehicle_id,
            "start_date": reservation.start_date.isoformat(),
            "end_date": reservation.end_date.isoformat(),
            "days": reservation.days,
            "amount": reservation.amount,
            "payment": reservation.payment,
            "status": reservation.status,
        }
