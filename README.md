# Vehicle Rental Management System

A console-based Python OOP project for the Vehicle Rental Management System case study.

## Features

- Car, Bike and Van inheritance from an abstract `Vehicle`
- Vehicle-specific rental cost through polymorphism
- Customer registration and rental history
- Vehicle search by ID, type and maximum daily price
- Payment abstraction using Card and UPI
- Payment before rental confirmation
- Vehicle availability management
- Return-date and late-fee calculation
- Final invoice generation
- Meaningful exception handling
- Interactive terminal menu
- Unit tests for success and failure cases

## Project Structure

```text
OOP-Case-Study/
│
├── exceptions/
│   ├── __init__.py
│   └── rental_exceptions.py
│
├── models/
│   ├── __init__.py
│   ├── vehicle.py
│   ├── car.py
│   ├── bike.py
│   ├── van.py
│   ├── customer.py
│   ├── rental.py
│   └── invoice.py
│
├── payments/
│   ├── __init__.py
│   ├── payment_processor.py
│   ├── card_payment.py
│   └── upi_payment.py
│
├── services/
│   ├── __init__.py
│   └── rental_service.py
│
├── tests/
│   ├── __init__.py
│   └── test_rental_system.py
│
├── class_diagram.md
├── README.md
└── main.py
```

## Run

Open the terminal in the project root and run:

```powershell
python main.py
```

The program creates a few initial vehicles and customers when it starts. This is startup sample data, not a pre-ingested test file.

The entire normal workflow is interactive through the terminal.

## Run Tests

```powershell
python -m unittest discover -s tests -v
```

## OOP Concepts Demonstrated

### Encapsulation
Vehicle and Customer state is private (`__field`) and exposed through controlled properties and methods.

### Abstraction
`Vehicle` is abstract and `PaymentProcessor` defines the payment contract.

### Inheritance
`Car`, `Bike` and `Van` inherit from `Vehicle`.

### Polymorphism
`calculate_rental_cost()` is overridden by each vehicle type. `RentalService` does not need a large vehicle-type `if/else` block.

### Composition
A `Rental` contains a Customer, Vehicle, payment result and Invoice.

### Interface / Dependency Inversion
`RentalService.rent_vehicle()` receives a `PaymentProcessor`, so it works with Card or UPI without depending on a concrete payment class.

## Business Rules

- Rental days must be greater than zero.
- An unavailable vehicle cannot be rented.
- A vehicle cannot be rented by two customers at the same time.
- Registration number is required.
- Payment must succeed before rental confirmation.
- Sensitive card/UPI information is not stored as plain text.
- Returned vehicles become available.
- Late fee = late days x 20% x vehicle daily rate.
- Bike gets 5% discount when rental exceeds five days.
- Van adds a 10% service charge to the normal rental amount.

## Mandatory Scenario

The seeded startup data contains:

- V101: Toyota Car, Rs. 2,000/day
- V102: Yamaha Bike, Rs. 700/day
- V103: Tata Van, Rs. 3,000/day
- C001: Ananya Sharma
- C002: Rahul Verma

To demonstrate the assignment:

1. Display vehicles.
2. Rent V101 for C001 for 3 days.
3. Pay successfully.
4. Try to rent V101 for C002 and see the unavailable message.
5. Return rental R001 one day late.
6. View the final invoice.
7. View C001 rental history.

For a 3-day car rental starting on 2026-08-26 and returned on 2026-08-30:
- Base = Rs. 6,000
- Late fee = Rs. 400
- Final = Rs. 6,400

## Important Design Choice

There is no pre-ingested runtime test file. Sample data is created in `main.py` at startup so the application immediately has usable vehicles and customers. The `tests/` folder is kept only for the required automated test cases.
