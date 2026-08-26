import unittest
from datetime import date, timedelta

from exceptions.rental_exceptions import VehicleUnavailableError, PaymentFailedError
from models.bike import Bike
from models.car import Car
from models.customer import Customer
from models.van import Van
from payments.card_payment import CardPayment
from payments.upi_payment import UPIPayment
from payments.payment_processor import PaymentProcessor
from services.rental_service import RentalService


class FailingPayment(PaymentProcessor):
    def process_payment(self, amount):
        raise PaymentFailedError("Simulated payment failure.")


class TestVehicleRentalSystem(unittest.TestCase):

    def setUp(self):
        self.service = RentalService()

        self.car = Car("V101", "DL01AB1234", "Toyota", "Camry", 2000)
        self.bike = Bike("V102", "DL02CD5678", "Yamaha", "R15", 700)
        self.van = Van("V103", "DL03EF9012", "Tata", "Winger", 3000)

        self.customer_a = Customer(
            "C001", "Ananya Sharma", "ananya@example.com", "LIC001"
        )
        self.customer_b = Customer(
            "C002", "Rahul Verma", "rahul@example.com", "LIC002"
        )

        self.service.add_vehicle(self.car)
        self.service.add_vehicle(self.bike)
        self.service.add_vehicle(self.van)
        self.service.register_customer(self.customer_a)
        self.service.register_customer(self.customer_b)

    def test_car_cost(self):
        self.assertEqual(self.car.calculate_rental_cost(3), 6000)

    def test_bike_discount_after_five_days(self):
        self.assertEqual(self.bike.calculate_rental_cost(6), 3990)

    def test_van_service_charge(self):
        self.assertEqual(self.van.calculate_rental_cost(2), 6600)

    def test_successful_rental(self):
        rental = self.service.rent_vehicle(
            "C001", "V101", 3, CardPayment("1234")
        )
        self.assertEqual(rental.base_amount, 6000)
        self.assertFalse(self.car.is_available)

    def test_unavailable_vehicle(self):
        self.service.rent_vehicle("C001", "V101", 3, CardPayment("1234"))

        with self.assertRaises(VehicleUnavailableError):
            self.service.rent_vehicle("C002", "V101", 2, UPIPayment("rahul@upi"))

    def test_late_return(self):
        rental = self.service.rent_vehicle(
            "C001", "V101", 3, CardPayment("1234"),
            start_date=date(2026, 8, 26),
        )

        invoice = self.service.return_vehicle(
            rental.rental_id, date(2026, 8, 30)
        )

        self.assertEqual(invoice.generate()["late_fee"], 400)
        self.assertEqual(invoice.generate()["final_amount"], 6400)
        self.assertTrue(self.car.is_available)

    def test_failed_payment_does_not_rent_vehicle(self):
        with self.assertRaises(PaymentFailedError):
            self.service.rent_vehicle("C001", "V101", 3, FailingPayment())

        self.assertTrue(self.car.is_available)
        self.assertEqual(len(self.service.rentals), 0)

    def test_customer_history(self):
        self.service.rent_vehicle("C001", "V101", 3, CardPayment("1234"))
        self.assertEqual(len(self.customer_a.rental_history), 1)


if __name__ == "__main__":
    unittest.main(verbosity=2)
