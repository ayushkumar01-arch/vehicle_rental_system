from models.vehicle import Vehicle


class Bike(Vehicle):
    DISCOUNT_RATE = 0.05

    @property
    def vehicle_type(self):
        return "Bike"

    def calculate_rental_cost(self, days: int) -> float:
        self._validate_days(days)
        amount = self.daily_rate * days

        if days > 5:
            amount *= 1 - self.DISCOUNT_RATE

        return amount
