from models.vehicle import Vehicle


class Van(Vehicle):
    SERVICE_CHARGE_RATE = 0.10

    @property
    def vehicle_type(self):
        return "Van"

    def calculate_rental_cost(self, days: int) -> float:
        self._validate_days(days)
        normal_amount = self.daily_rate * days
        service_charge = normal_amount * self.SERVICE_CHARGE_RATE
        return normal_amount + service_charge
