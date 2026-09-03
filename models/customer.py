from exceptions.rental_exceptions import ValidationError


class Customer:
    """Customer with private data and rental history."""

    def __init__(self, customer_id, name, email, licence_number):
        values = {
            "Customer ID": customer_id,
            "Name": name,
            "Email": email,
            "Driving licence number": licence_number,
        }
        for field_name, value in values.items():
            if not str(value).strip():
                raise ValidationError(f"{field_name} cannot be empty.")

        self.__customer_id = customer_id.strip()
        self.__name = name.strip()
        self.__email = email.strip()
        self.__licence_number = licence_number.strip()
        self.__rental_history = []

    @property
    def customer_id(self):
        return self.__customer_id

    @property
    def name(self):
        return self.__name

    @property
    def email(self):
        return self.__email

    @property
    def licence_number(self):
        return self.__licence_number

    @property
    def rental_history(self):
        return tuple(self.__rental_history)

    def add_rental(self, rental):
        if rental not in self.__rental_history:
            self.__rental_history.append(rental)

    def display_rental_history(self):
        if not self.__rental_history:
            return f"No rental history found for {self.name}."
        lines = [f"Rental History - {self.name}", "-" * 70]
        for rental in self.__rental_history:
            lines.append(rental.summary())
        return "\n".join(lines)

    def __str__(self):
        return f"{self.customer_id} | {self.name} | {self.email}"
