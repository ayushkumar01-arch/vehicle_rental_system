from datetime import date, datetime

from exceptions.rental_exceptions import RentalSystemError
from models.bike import Bike
from models.car import Car
from models.customer import Customer
from models.van import Van
from payments.card_payment import CardPayment
from payments.upi_payment import UPIPayment
from services.rental_service import RentalService


def print_header(title):
    print("\n" + "=" * 72)
    print(f"{title:^72}")
    print("=" * 72)


def pause():
    input("\nPress Enter to continue...")


def seed_startup_data(service):
    """Create useful starting data at program startup.

    This replaces the need for a pre-ingested test-data file.
    """
    service.add_vehicle(
        Car("V101", "DL01AB1234", "Toyota", "Camry", 2000)
    )
    service.add_vehicle(
        Bike("V102", "DL02CD5678", "Yamaha", "R15", 700)
    )
    service.add_vehicle(
        Van("V103", "DL03EF9012", "Tata", "Winger", 3000)
    )

    service.register_customer(
        Customer(
            "C001",
            "Ananya Sharma",
            "ananya@example.com",
            "LIC001",
        )
    )
    service.register_customer(
        Customer(
            "C002",
            "Rahul Verma",
            "rahul@example.com",
            "LIC002",
        )
    )


def display_vehicles(service, vehicles=None):
    vehicles = list(service.vehicles if vehicles is None else vehicles)

    print_header("AVAILABLE VEHICLES")

    if not vehicles:
        print("No vehicles found.")
        return

    print(
        f"{'ID':<7} {'TYPE':<8} {'BRAND':<12} "
        f"{'MODEL':<12} {'RATE/DAY':<14} {'STATUS'}"
    )
    print("-" * 72)

    for vehicle in vehicles:
        status = "AVAILABLE" if vehicle.is_available else "UNAVAILABLE"
        print(
            f"{vehicle.vehicle_id:<7} "
            f"{vehicle.vehicle_type:<8} "
            f"{vehicle.brand:<12} "
            f"{vehicle.model:<12} "
            f"Rs. {vehicle.daily_rate:<9,.2f} "
            f"{status}"
        )


def display_customers(service):
    print_header("CUSTOMERS")

    if not service.customers:
        print("No customers registered.")
        return

    for customer in service.customers:
        print(
            f"{customer.customer_id} | "
            f"{customer.name} | "
            f"{customer.email} | "
            f"Licence: {customer.licence_number}"
        )


def search_vehicles_menu(service):
    print_header("SEARCH VEHICLES")
    print("1. Search by vehicle ID")
    print("2. Search by vehicle type")
    print("3. Search by maximum daily price")
    print("4. Show all")

    choice = input("\nEnter your choice: ").strip()

    if choice == "1":
        vehicle_id = input("Enter vehicle ID: ").strip()
        results = service.search_vehicles(vehicle_id=vehicle_id)
    elif choice == "2":
        vehicle_type = input("Enter type (Car/Bike/Van): ").strip()
        results = service.search_vehicles(vehicle_type=vehicle_type)
    elif choice == "3":
        max_price = read_positive_float("Enter maximum daily price: ")
        results = service.search_vehicles(max_price=max_price)
    elif choice == "4":
        results = service.vehicles
    else:
        print("❌ Invalid search option.")
        return

    display_vehicles(service, results)


def register_customer_menu(service):
    print_header("REGISTER NEW CUSTOMER")

    customer_id = input("Customer ID: ").strip()
    name = input("Full name: ").strip()
    email = input("Email: ").strip()
    licence = input("Driving licence number: ").strip()

    customer = Customer(customer_id, name, email, licence)
    service.register_customer(customer)

    print(f"✅ Customer {customer_id} registered successfully.")


def choose_payment():
    print("\nPAYMENT METHOD")
    print("1. Card")
    print("2. UPI")

    choice = input("Select payment method: ").strip()

    if choice == "1":
        print("For security, do NOT enter the full card number.")
        last_four = input("Enter last 4 digits of card: ").strip()
        return CardPayment(last_four)

    if choice == "2":
        upi_id = input("Enter UPI ID (example: name@upi): ").strip()
        return UPIPayment(upi_id)

    raise ValueError("Invalid payment method selected.")


def rent_vehicle_menu(service):
    print_header("RENT A VEHICLE")

    available = [v for v in service.vehicles if v.is_available]
    display_vehicles(service, available)

    if not available:
        return

    customer_id = input("\nEnter customer ID: ").strip()
    vehicle_id = input("Enter vehicle ID: ").strip()
    days = read_positive_int("Enter rental days: ")

    vehicle = service.get_vehicle(vehicle_id)
    amount = vehicle.calculate_rental_cost(days)

    print("\nRENTAL SUMMARY")
    print(f"Customer       : {service.get_customer(customer_id).name}")
    print(f"Vehicle        : {vehicle.vehicle_id} ({vehicle.vehicle_type})")
    print(f"Rental days    : {days}")
    print(f"Rental amount  : Rs. {amount:,.2f}")

    confirm = input("\nConfirm rental and continue to payment? (y/n): ").strip().lower()
    if confirm != "y":
        print("ℹ️ Rental cancelled. No payment was processed.")
        return

    payment_processor = choose_payment()

    rental = service.rent_vehicle(
        customer_id=customer_id,
        vehicle_id=vehicle_id,
        days=days,
        payment_processor=payment_processor,
    )

    print("\n" + "=" * 72)
    print("✅ PAYMENT COMPLETED SUCCESSFULLY")
    print(f"Payment method : {rental.payment['method']}")
    print(f"Reference      : {rental.payment['reference']}")
    print(f"Amount paid    : Rs. {rental.payment['amount']:,.2f}")
    print(f"Rental ID      : {rental.rental_id}")
    print(f"Due date       : {rental.due_date}")
    print("Vehicle status : UNAVAILABLE")
    print("✅ Rental confirmed successfully.")
    print("=" * 72)


def parse_date_input(prompt):
    value = input(prompt).strip()

    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except ValueError as exc:
        raise ValueError(
            "Invalid date. Please use YYYY-MM-DD, for example 2026-08-30."
        ) from exc


def return_vehicle_menu(service):
    print_header("RETURN VEHICLE")

    active = service.active_rentals()

    if not active:
        print("No active rentals found.")
        return

    print("ACTIVE RENTALS")
    print("-" * 72)

    for rental in active:
        print(
            f"{rental.rental_id} | "
            f"{rental.customer.name} | "
            f"{rental.vehicle.vehicle_id} | "
            f"Due: {rental.due_date} | "
            f"Base: Rs. {rental.base_amount:,.2f}"
        )

    rental_id = input("\nEnter rental ID: ").strip()
    return_date = parse_date_input(
        "Enter actual return date (YYYY-MM-DD): "
    )

    invoice = service.return_vehicle(rental_id, return_date)

    print("\n✅ Vehicle returned successfully.")

    if invoice.generate()["late_fee"] > 0:
        print("⚠️ The vehicle was returned late.")
    else:
        print("✅ Vehicle was returned on time.")

    print(invoice.display())


def rental_history_menu(service):
    print_header("CUSTOMER RENTAL HISTORY")

    customer_id = input("Enter customer ID: ").strip()
    customer = service.get_customer(customer_id)

    print("\n" + customer.display_rental_history())


def show_rental_invoice_menu(service):
    print_header("VIEW RENTAL / INVOICE")

    if not service.rentals:
        print("No rentals exist yet.")
        return

    for rental in service.rentals:
        print(rental.summary())

    rental_id = input("\nEnter rental ID: ").strip()
    rental = service.get_rental(rental_id)

    print(rental.invoice.display())


def read_positive_int(prompt):
    value = input(prompt).strip()

    try:
        number = int(value)
    except ValueError as exc:
        raise ValueError("Please enter a whole number.") from exc

    if number <= 0:
        raise ValueError("Value must be greater than zero.")

    return number


def read_positive_float(prompt):
    value = input(prompt).strip()

    try:
        number = float(value)
    except ValueError as exc:
        raise ValueError("Please enter a valid number.") from exc

    if number <= 0:
        raise ValueError("Value must be greater than zero.")

    return number


def show_menu():
    print_header("VEHICLE RENTAL MANAGEMENT SYSTEM")

    print("1. 🚗 Display all vehicles")
    print("2. 🔎 Search vehicles")
    print("3. 👤 Register new customer (e.g., C001)")
    print("4. 👥 Display customers")
    print("5. 📝 Rent a vehicle")
    print("6. 🔄 Return a vehicle")
    print("7. 📜 View customer rental history")
    print("8. 🧾 View rental / invoice")
    print("9. 📊 View active rentals")
    print("0. 🚪 Exit")


def show_active_rentals(service):
    print_header("ACTIVE RENTALS")

    active = service.active_rentals()

    if not active:
        print("No active rentals.")
        return

    for rental in active:
        print(
            f"{rental.rental_id} | "
            f"{rental.customer.name} | "
            f"{rental.vehicle.vehicle_id} | "
            f"{rental.vehicle.vehicle_type} | "
            f"{rental.days} day(s) | "
            f"Due: {rental.due_date}"
        )


def run_application():
    service = RentalService()
    seed_startup_data(service)

    print_header("WELCOME TO VEHICLE RENTAL MANAGEMENT SYSTEM")
    print("Startup data loaded successfully.")
    print("You can now manage vehicles, customers, rentals and payments.")
    print("\nSample login-free data:")
    print("  Vehicles : V101, V102, V103")
    print("  Customers: C001, C002")

    while True:
        try:
            show_menu()
            choice = input("\nEnter your choice: ").strip()

            if choice == "1":
                display_vehicles(service)
                pause()

            elif choice == "2":
                search_vehicles_menu(service)
                pause()

            elif choice == "3":
                register_customer_menu(service)
                pause()

            elif choice == "4":
                display_customers(service)
                pause()

            elif choice == "5":
                rent_vehicle_menu(service)
                pause()

            elif choice == "6":
                return_vehicle_menu(service)
                pause()

            elif choice == "7":
                rental_history_menu(service)
                pause()

            elif choice == "8":
                show_rental_invoice_menu(service)
                pause()

            elif choice == "9":
                show_active_rentals(service)
                pause()

            elif choice == "0":
                print("\nThank you for using the Vehicle Rental Management System.")
                print("Program closed successfully. 👋")
                break

            else:
                print("❌ Invalid choice. Please select an option from the menu.")

        except (RentalSystemError, ValueError) as exc:
            print(f"\n❌ ERROR: {exc}")
            print("Please try again.")
            pause()
        except KeyboardInterrupt:
            print("\n\nProgram interrupted by user. Goodbye! 👋")
            break


if __name__ == "__main__":
    run_application()
