from datetime import date

from exceptions.rental_exceptions import ValidationError


class Reservation:
    """A future booking that blocks a vehicle for a date range."""

    def __init__(
        self,
        reservation_id,
        customer,
        vehicle,
        start_date: date,
        end_date: date,
        amount: float,
        payment: dict,
    ):
        if end_date <= start_date:
            raise ValidationError("Return date must be after pickup date.")

        self.__reservation_id = reservation_id
        self.__customer = customer
        self.__vehicle = vehicle
        self.__start_date = start_date
        self.__end_date = end_date
        self.__days = (end_date - start_date).days
        self.__amount = amount
        self.__payment = payment
        self.__status = "CONFIRMED"

    @property
    def reservation_id(self):
        return self.__reservation_id

    @property
    def customer(self):
        return self.__customer

    @property
    def vehicle(self):
        return self.__vehicle

    @property
    def start_date(self):
        return self.__start_date

    @property
    def end_date(self):
        return self.__end_date

    @property
    def days(self):
        return self.__days

    @property
    def amount(self):
        return self.__amount

    @property
    def payment(self):
        return self.__payment

    @property
    def status(self):
        return self.__status

    def cancel(self):
        if self.__status != "CONFIRMED":
            raise ValidationError("Only confirmed reservations can be cancelled.")
        self.__status = "CANCELLED"

    def complete(self):
        self.__status = "COMPLETED"

    def overlaps(self, start_date, end_date):
        if self.status != "CONFIRMED":
            return False
        return start_date < self.end_date and end_date > self.start_date

    def summary(self):
        return (
            f"{self.reservation_id} | {self.vehicle.vehicle_id} | "
            f"{self.customer.name} | {self.start_date} -> {self.end_date} | "
            f"Rs. {self.amount:,.2f} | {self.status}"
        )
