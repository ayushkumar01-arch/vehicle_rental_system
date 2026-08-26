from abc import ABC, abstractmethod


class PaymentProcessor(ABC):
    """Payment contract used by the rental workflow."""

    @abstractmethod
    def process_payment(self, amount: float) -> dict:
        """Process payment and return a safe payment result."""
        raise NotImplementedError
