from datetime import date, timedelta

from exceptions.rental_exceptions import InvalidReturnDateError, ValidationError
from models.invoice import Invoice


class Rental:
    """A rental containing a customer, vehicle, payment and return inspection."""

    LATE_FEE_RATE = 1.2
    FUEL_PRICE_PER_PERCENT = 25.0

    def __init__(
        self,
        rental_id,
        customer,
        vehicle,
        days,
        payment,
        start_date=None,
        pickup_fuel=None,
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
        self.__pickup_fuel = vehicle.fuel_level if pickup_fuel is None else pickup_fuel
        self.__return_fuel = None
        self.__late_fee = 0.0
        self.__fuel_charge = 0.0
        self.__damage_charge = 0.0
        self.__damage_items = []
        self.__return_date = None
        self.__status = "ACTIVE"
        self.__cancellation_refund = 0.0
        self.__invoice = self._build_invoice()

    @property
    def rental_id(self): return self.__rental_id
    @property
    def customer(self): return self.__customer
    @property
    def vehicle(self): return self.__vehicle
    @property
    def days(self): return self.__days
    @property
    def start_date(self): return self.__start_date
    @property
    def due_date(self): return self.__due_date
    @property
    def base_amount(self): return self.__base_amount
    @property
    def late_fee(self): return self.__late_fee
    @property
    def fuel_charge(self): return self.__fuel_charge
    @property
    def damage_charge(self): return self.__damage_charge
    @property
    def damage_items(self): return tuple(self.__damage_items)
    @property
    def pickup_fuel(self): return self.__pickup_fuel
    @property
    def return_fuel(self): return self.__return_fuel
    @property
    def status(self): return self.__status
    @property
    def return_date(self): return self.__return_date
    @property
    def invoice(self): return self.__invoice
    @property
    def payment(self): return self.__payment
    @property
    def cancellation_refund(self): return self.__cancellation_refund

    @property
    def final_amount(self):
        return self.__invoice.final_amount

    def _build_invoice(self):
        return Invoice(
            rental_id=self.__rental_id,
            customer_name=self.__customer.name,
            vehicle=self.__vehicle,
            rental_days=self.__days,
            start_date=self.__start_date,
            due_date=self.__due_date,
            base_amount=self.__base_amount,
            late_fee=self.__late_fee,
            fuel_charge=self.__fuel_charge,
            damage_charge=self.__damage_charge,
            damage_items=self.__damage_items,
            return_date=self.__return_date,
            cancellation_refund=self.__cancellation_refund,
        )

    def complete_rental(self, return_date, return_fuel, damage_items=None):
        if self.__status != "ACTIVE":
            raise ValidationError("This rental is not active.")
        if return_date < self.__start_date:
            raise InvalidReturnDateError("Return date cannot be before the rental start date.")
        if not 0 <= return_fuel <= 100:
            raise ValidationError("Return fuel must be between 0 and 100.")

        self.__return_date = return_date
        self.__return_fuel = float(return_fuel)
        late_days = max(0, (return_date - self.__due_date).days)
        self.__late_fee = late_days * self.__vehicle.daily_rate * self.LATE_FEE_RATE

        missing_fuel = max(0, self.__pickup_fuel - self.__return_fuel)
        self.__fuel_charge = missing_fuel * self.FUEL_PRICE_PER_PERCENT

        self.__damage_items = damage_items or []
        self.__damage_charge = sum(item["charge"] for item in self.__damage_items)
        self.__status = "RETURNED"
        self.__vehicle.set_fuel_level(self.__return_fuel)
        self.__invoice = self._build_invoice()
        self.__vehicle.mark_as_available()
        return self.__invoice

    def cancel_remaining_days(self, cancel_date, return_fuel, damage_items=None):
        if self.__status != "ACTIVE":
            raise ValidationError("Only active rentals can be cancelled.")
        if cancel_date < self.__start_date:
            raise InvalidReturnDateError("Cancellation date cannot be before the rental start date.")
        if cancel_date >= self.__due_date:
            raise ValidationError("There are no remaining rental days to cancel.")
        if not 0 <= return_fuel <= 100:
            raise ValidationError("Return fuel must be between 0 and 100.")

        used_days = (cancel_date - self.__start_date).days
        remaining_days = self.__days - used_days
        daily_paid_amount = self.__base_amount / self.__days
        possible_refund = daily_paid_amount * remaining_days

        self.__return_date = cancel_date
        self.__return_fuel = float(return_fuel)
        missing_fuel = max(0, self.__pickup_fuel - self.__return_fuel)
        self.__fuel_charge = missing_fuel * self.FUEL_PRICE_PER_PERCENT
        self.__damage_items = damage_items or []
        self.__damage_charge = sum(item["charge"] for item in self.__damage_items)

        # Remaining rental value is refunded after inspection charges.
        self.__cancellation_refund = max(0.0, possible_refund - self.__fuel_charge - self.__damage_charge)
        extra_due = max(0.0, self.__fuel_charge + self.__damage_charge - possible_refund)
        self.__status = "CANCELLED"
        self.__vehicle.set_fuel_level(self.__return_fuel)
        self.__invoice = self._build_invoice()
        self.__vehicle.mark_as_available()

        return used_days, remaining_days, possible_refund, extra_due

    def summary(self):
        return (
            f"{self.rental_id} | {self.vehicle.vehicle_type} {self.vehicle.vehicle_id} | "
            f"{self.days} day(s) | Rs. {self.final_amount:,.2f} | {self.status}"
        )

    def __str__(self):
        return self.summary()
