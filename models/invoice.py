from datetime import date


class Invoice:
    """Represents the final financial breakdown of a rental."""

    def __init__(
        self,
        rental_id: str,
        customer_name: str,
        vehicle,
        rental_days: int,
        start_date: date,
        due_date: date,
        base_amount: float,
        late_fee: float = 0.0,
        return_date: date | None = None,
    ):
        self.__rental_id = rental_id
        self.__customer_name = customer_name
        self.__vehicle = vehicle
        self.__rental_days = rental_days
        self.__start_date = start_date
        self.__due_date = due_date
        self.__base_amount = base_amount
        self.__late_fee = late_fee
        self.__return_date = return_date

    @property
    def final_amount(self):
        return self.__base_amount + self.__late_fee

    def generate(self):
        return {
            "rental_id": self.__rental_id,
            "customer": self.__customer_name,
            "vehicle": f"{self.__vehicle.vehicle_id} - {self.__vehicle.vehicle_type}",
            "rental_days": self.__rental_days,
            "start_date": self.__start_date,
            "due_date": self.__due_date,
            "return_date": self.__return_date,
            "base_amount": self.__base_amount,
            "late_fee": self.__late_fee,
            "final_amount": self.final_amount,
        }

    def display(self):
        data = self.generate()
        return (
            "\n"
            "================ FINAL INVOICE ================\n"
            f"Rental ID       : {data['rental_id']}\n"
            f"Customer        : {data['customer']}\n"
            f"Vehicle         : {data['vehicle']}\n"
            f"Rental days     : {data['rental_days']}\n"
            f"Start date      : {data['start_date']}\n"
            f"Due date        : {data['due_date']}\n"
            f"Return date     : {data['return_date'] or 'Not returned'}\n"
            f"Base amount     : Rs. {data['base_amount']:,.2f}\n"
            f"Late fee        : Rs. {data['late_fee']:,.2f}\n"
            f"Final amount    : Rs. {data['final_amount']:,.2f}\n"
            "===============================================\n"
        )
