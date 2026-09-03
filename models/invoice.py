from datetime import date


class Invoice:
    """Final financial breakdown of a rental."""

    def __init__(
        self,
        rental_id,
        customer_name,
        vehicle,
        rental_days,
        start_date,
        due_date,
        base_amount,
        late_fee=0.0,
        fuel_charge=0.0,
        damage_charge=0.0,
        damage_items=None,
        return_date: date | None = None,
        cancellation_refund=0.0,
    ):
        self.__rental_id = rental_id
        self.__customer_name = customer_name
        self.__vehicle = vehicle
        self.__rental_days = rental_days
        self.__start_date = start_date
        self.__due_date = due_date
        self.__base_amount = base_amount
        self.__late_fee = late_fee
        self.__fuel_charge = fuel_charge
        self.__damage_charge = damage_charge
        self.__damage_items = damage_items or []
        self.__return_date = return_date
        self.__cancellation_refund = cancellation_refund

    @property
    def final_amount(self):
        return (
            self.__base_amount
            + self.__late_fee
            + self.__fuel_charge
            + self.__damage_charge
            - self.__cancellation_refund
        )

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
            "fuel_charge": self.__fuel_charge,
            "damage_charge": self.__damage_charge,
            "damage_items": self.__damage_items,
            "cancellation_refund": self.__cancellation_refund,
            "final_amount": self.final_amount,
        }

    def display(self):
        data = self.generate()
        lines = [
            "\n================ FINAL INVOICE ================",
            f"Rental ID       : {data['rental_id']}",
            f"Customer        : {data['customer']}",
            f"Vehicle         : {data['vehicle']}",
            f"Rental days     : {data['rental_days']}",
            f"Start date      : {data['start_date']}",
            f"Due date        : {data['due_date']}",
            f"Return date     : {data['return_date'] or 'Not returned'}",
            f"Base amount     : Rs. {data['base_amount']:,.2f}",
            f"Late fee        : Rs. {data['late_fee']:,.2f}",
            f"Fuel charge     : Rs. {data['fuel_charge']:,.2f}",
            f"Damage charge   : Rs. {data['damage_charge']:,.2f}",
        ]
        if data["damage_items"]:
            lines.append("Damage details:")
            for item in data["damage_items"]:
                lines.append(f"  - {item['description']} : Rs. {item['charge']:,.2f}")
        if data["cancellation_refund"]:
            lines.append(f"Cancellation refund: -Rs. {data['cancellation_refund']:,.2f}")
        lines.extend([
            f"Final amount    : Rs. {data['final_amount']:,.2f}",
            "===============================================",
        ])
        return "\n".join(lines)
