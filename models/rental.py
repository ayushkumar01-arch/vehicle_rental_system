from datetime import date, timedelta

from exceptions.rental_exceptions import (
    InvalidReturnDateError,
    ValidationError,
)
from models.invoice import Invoice


class Rental:
    """Composition: a Rental contains a Customer, Vehicle and payment result."""

    LATE_FEE_RATE = 0.20

    def __init__(
        self,
        rental_id: str,
        customer,
        vehicle,
        days: int,
        payment,
        start_date: date | None = None,
    ):
        if days <= 0:
            raise ValidationError("Rental days must be greater than zero.")

        self.__rental_id = rental_id
        self.__customer = customer
        self.__vehicle = vehicle
        self.__days = days
        self.__payment = payment
        self.__start_date = start_date or date.today()
        self.__due_date = self.__start_date + timedelta(days=days)
        self.__base_amount = vehicle.calculate_rental_cost(days)
        self.__late_fee = 0.0
        self.__return_date = None
        self.__status = "ACTIVE"

        self.__invoice = Invoice(
            rental_id=self.__rental_id,
            customer_name=self.__customer.name,
            vehicle=self.__vehicle,
            rental_days=self.__days,
            start_date=self.__start_date,
            due_date=self.__due_date,
            base_amount=self.__base_amount,
        )

    @property
    def rental_id(self):
        return self.__rental_id

    @property
    def customer(self):
        return self.__customer

    @property
    def vehicle(self):
        return self.__vehicle

    @property
    def days(self):
        return self.__days

    @property
    def start_date(self):
        return self.__start_date

    @property
    def due_date(self):
        return self.__due_date

    @property
    def base_amount(self):
        return self.__base_amount

    @property
    def late_fee(self):
        return self.__late_fee

    @property
    def final_amount(self):
        return self.__base_amount + self.__late_fee

    @property
    def status(self):
        return self.__status

    @property
    def return_date(self):
        return self.__return_date

    @property
    def invoice(self):
        return self.__invoice

    @property
    def payment(self):
        return self.__payment

    def complete_rental(self, return_date: date):
        if self.__status == "RETURNED":
            raise ValidationError("This rental has already been returned.")

        if return_date < self.__start_date:
            raise InvalidReturnDateError(
                "Return date cannot be before the rental start date."
            )

        self.__return_date = return_date
        late_days = max(0, (return_date - self.__due_date).days)
        self.__late_fee = (
            late_days * self.__vehicle.daily_rate * self.LATE_FEE_RATE
        )
        self.__status = "RETURNED"

        self.__invoice = Invoice(
            rental_id=self.__rental_id,
            customer_name=self.__customer.name,
            vehicle=self.__vehicle,
            rental_days=self.__days,
            start_date=self.__start_date,
            due_date=self.__due_date,
            base_amount=self.__base_amount,
            late_fee=self.__late_fee,
            return_date=self.__return_date,
        )

        self.__vehicle.mark_as_available()
        return self.__invoice

    def summary(self):
        return (
            f"{self.rental_id} | {self.vehicle.vehicle_type} "
            f"{self.vehicle.vehicle_id} | {self.days} day(s) | "
            f"Rs. {self.final_amount:,.2f} | {self.status}"
        )

    def __str__(self):
        return self.summary()
