from datetime import datetime

from exceptions.rental_exceptions import PaymentFailedError, ValidationError
from payments.payment_processor import PaymentProcessor


class UPIPayment(PaymentProcessor):
    """UPI payment implementation.

    The complete UPI ID is not stored.
    """

    def __init__(self, upi_id: str):
        if not upi_id.strip() or "@" not in upi_id:
            raise ValidationError(
                "Enter a valid UPI ID, for example name@upi."
            )
        self.__upi_domain = upi_id.split("@", 1)[1]

    def process_payment(self, amount: float) -> dict:
        if amount <= 0:
            raise PaymentFailedError("Payment amount must be greater than zero.")

        return {
            "method": "UPI",
            "status": "SUCCESS",
            "amount": amount,
            "reference": f"UPI-{datetime.now().strftime('%Y%m%d%H%M%S%f')}",
            "masked_account": f"****@{self.__upi_domain}",
        }
