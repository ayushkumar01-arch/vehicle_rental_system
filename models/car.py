from models.vehicle import Vehicle


class Car(Vehicle):
    @property
    def vehicle_type(self):
        return "Car"

    def calculate_rental_cost(self, days: int) -> float:
        self._validate_days(days)
        return self.daily_rate * days
