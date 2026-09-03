from datetime import datetime

from exceptions.rental_exceptions import PaymentFailedError, ValidationError
from payments.payment_processor import PaymentProcessor


class CardPayment(PaymentProcessor):
    def __init__(self, card_last_four: str):
        if not card_last_four.isdigit() or len(card_last_four) != 4:
            raise ValidationError("Enter exactly the last 4 digits of the card.")
        self.__card_last_four = card_last_four

    def process_payment(self, amount: float) -> dict:
        if amount <= 0:
            raise PaymentFailedError("Payment amount must be greater than zero.")
        return {
            "method": "Card",
            "status": "SUCCESS",
            "amount": amount,
            "reference": f"CARD-{datetime.now().strftime('%Y%m%d%H%M%S%f')}",
            "masked_account": f"**** **** **** {self.__card_last_four}",
        }

    def refund_payment(self, amount: float) -> dict:
        if amount <= 0:
            raise PaymentFailedError("Refund amount must be greater than zero.")
        return {
            "method": "Card Refund",
            "status": "REFUNDED",
            "amount": amount,
            "reference": f"REFUND-CARD-{datetime.now().strftime('%Y%m%d%H%M%S%f')}",
            "masked_account": f"**** **** **** {self.__card_last_four}",
        }
