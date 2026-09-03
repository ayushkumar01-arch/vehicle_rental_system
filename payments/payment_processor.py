from abc import ABC, abstractmethod


class PaymentProcessor(ABC):
    @abstractmethod
    def process_payment(self, amount: float) -> dict:
        raise NotImplementedError

    @abstractmethod
    def refund_payment(self, amount: float) -> dict:
        raise NotImplementedError
