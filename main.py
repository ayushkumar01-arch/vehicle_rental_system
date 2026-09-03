from datetime import date, datetime, timedelta

from exceptions.rental_exceptions import RentalSystemError, ValidationError
from models.bike import Bike
from models.car import Car
from models.customer import Customer
from models.van import Van
from payments.card_payment import CardPayment
from payments.upi_payment import UPIPayment
from services.rental_service import RentalService


def clear_screen():
    print("\n" * 2)

# This prints a nice heading
def print_header(title):
    print("\n" + "=" * 78)
    print(f"{title:^78}")
    print("=" * 78)


def pause():
    input("\nPress Enter to continue...")


# make sure user only select from the given choices
def read_choice(prompt, choices):
    while True:
        value = input(prompt).strip()
        if value in choices:
            return value
        print(f"❌ Please choose one of: {', '.join(choices)}")


# read a positive integer from user input
def read_positive_int(prompt):
    value = input(prompt).strip()
    try:
        number = int(value)
    except ValueError as exc:
        raise ValidationError("Please enter a whole number.") from exc
    if number <= 0:
        raise ValidationError("Value must be greater than zero.")
    return number


# read a positive float from user input
def read_positive_float(prompt):
    value = input(prompt).strip()
    try:
        number = float(value)
    except ValueError as exc:
        raise ValidationError("Please enter a valid number.") from exc
    if number <= 0:
        raise ValidationError("Value must be greater than zero.")
    return number

# valid percentage input between 0 and 100
def read_percentage(prompt):
    value = input(prompt).strip()
    try:
        number = float(value)
    except ValueError as exc:
        raise ValidationError("Please enter a valid percentage.") from exc
    if not 0 <= number <= 100:
        raise ValidationError("Percentage must be between 0 and 100.")
    return number

# check if date in date format or not
def parse_date_input(prompt):
    value = input(prompt).strip()
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except ValueError as exc:
        raise ValidationError("Use date format YYYY-MM-DD, for example 2026-09-10.") from exc


#This function creates demo/default data when the system is empty.
def seed_startup_data(service):
    if service.vehicles or service.customers:
        return

    vehicles = [
        Car("V101", "DL01AB1234", "Toyota", "Camry", 2000),
        Bike("V102", "DL02CD5678", "Yamaha", "R15", 700),
        Van("V103", "DL03EF9012", "Tata", "Winger", 3000),
        Car("V104", "DL04GH1122", "BMW", "5 Series", 5000),
        Car("V105", "DL05IJ3344", "Mercedes-Benz", "C-Class", 5500),
        Car("V106", "DL06KL5566", "Audi", "A4", 4500),
        Car("V107", "DL07MN7788", "Bugatti", "Chiron", 25000),
        Car("V108", "DL08OP9900", "Mahindra", "Thar", 3000),
        Car("V109", "DL09QR1234", "Hyundai", "Creta", 2500),
        Bike("V110", "DL10ST2345", "Royal Enfield", "Classic 350", 800),
        Bike("V111", "DL11UV6789", "Kawasaki", "Ninja 650", 1500),
        Bike("V112", "DL12WX3456", "Harley-Davidson", "Iron 883", 1800),
        Bike("V113", "DL13YZ7890", "KTM", "Duke 390", 900),
        Bike("V114", "DL14AA4567", "Royal Enfield", "Himalayan 450", 1000),
        Van("V115", "DL15BB8901", "Toyota", "HiAce", 4000),
        Van("V116", "DL16CC2345", "Force", "Traveller", 3500),
    ]

    # adds every vehicle to the rental service
    for vehicle in vehicles:
        service.add_vehicle(vehicle)

    customers = [
        Customer("C001", "Ananya Sharma", "ananya@example.com", "LIC001"),
        Customer("C002", "Rahul Verma", "rahul@example.com", "LIC002"),
        Customer("C003", "Priya Singh", "priya@example.com", "LIC003"),
        Customer("C004", "Arjun Mehta", "arjun@example.com", "LIC004"),
        Customer("C005", "Sneha Kapoor", "sneha@example.com", "LIC005"),
    ]

    for customer in customers:
        service.register_customer(customer)


def display_vehicles(service, vehicles=None):
    vehicles = list(service.vehicles if vehicles is None else vehicles)
    print_header("VEHICLE FLEET")
    if not vehicles:
        print("No vehicles found.")
        return

    print(f"{'ID':<7} {'TYPE':<7} {'VEHICLE':<28} {'RATE/DAY':<14} {'FUEL':<9} STATUS")
    print("-" * 78)
    for vehicle in vehicles:
        print(
            f"{vehicle.vehicle_id:<7} {vehicle.vehicle_type:<7} "
            f"{vehicle.brand + ' ' + vehicle.model:<28} "
            f"Rs. {vehicle.daily_rate:<9,.0f} {vehicle.fuel_level:>5.1f}%   {vehicle.status}"
        )


def display_customers(service):
    print_header("CUSTOMERS")
    if not service.customers:
        print("No customers registered.")
        return
    for customer in service.customers:
        print(
            f"{customer.customer_id} | {customer.name} | "
            f"{customer.email} | Licence: {customer.licence_number}"
        )


def choose_payment():
    print("\nPAYMENT METHOD")
    print("1. Card")
    print("2. UPI")
    choice = read_choice("Choose payment method: ", {"1", "2"})

    if choice == "1":
        last_four = input("Enter last 4 digits of card: ").strip()
        return CardPayment(last_four)

    upi_id = input("Enter UPI ID (example: name@upi): ").strip()
    return UPIPayment(upi_id)

# This is used when money needs to be refunded
def choose_refund_processor(payment):
    """Use the original payment method for a simulated refund."""
    if payment.get("method") == "Card":

        # from the payment dictionary, get the last 4 digits of the card number
        last_four = payment.get("masked_account", "")[-4:]
        return CardPayment(last_four)

    domain = payment.get("masked_account", "upi").split("@")[-1]
    return UPIPayment(f"refund@{domain}")


def search_vehicles_menu(service):
    print_header("SEARCH VEHICLES")
    print("1. Search by vehicle ID")
    print("2. Search by vehicle type")
    print("3. Search by maximum daily price")
    print("4. Show all")
    print("0. Back")

    choice = read_choice("Choose option: ", {"1", "2", "3", "4", "0"})
    if choice == "0":
        return
    if choice == "1":
        results = service.search_vehicles(vehicle_id=input("Vehicle ID: ").strip())
    elif choice == "2":
        results = service.search_vehicles(vehicle_type=input("Type (Car/Bike/Van): ").strip())
    elif choice == "3":
        results = service.search_vehicles(max_price=read_positive_float("Maximum daily price: "))
    else:
        results = service.vehicles
    display_vehicles(service, results)


def register_customer_menu(service):
    print_header("REGISTER CUSTOMER")
    customer_id = input("Customer ID: ").strip()
    name = input("Full name: ").strip()
    email = input("Email: ").strip()
    licence = input("Driving licence number: ").strip()
    service.register_customer(Customer(customer_id, name, email, licence))
    print(f"\n✅ Customer {customer_id} registered successfully.")

# This checks which vehicles are available between two dates
def show_date_availability(service):
    print_header("CHECK DATE AVAILABILITY")
    start_date = parse_date_input("Pickup date (YYYY-MM-DD): ")
    end_date = parse_date_input("Return date (YYYY-MM-DD): ")
    if end_date <= start_date:
        raise ValidationError("Return date must be after pickup date.")

    available = service.available_vehicles(start_date, end_date)
    print(f"\nRequested period: {start_date} → {end_date}")
    print(f"Available vehicles: {len(available)}")
    display_vehicles(service, available)


def rent_vehicle_menu(service):
    print_header("RENT VEHICLE")
    customer_id = input("Customer ID: ").strip()
    customer = service.get_customer(customer_id)

    vehicle_id = input("Vehicle ID: ").strip()
    vehicle = service.get_vehicle(vehicle_id)
    days = read_positive_int("Rental days: ")
    start_date = parse_date_input("Pickup date (YYYY-MM-DD): ")
    end_date = start_date + timedelta(days=days)

    if not service.is_vehicle_available(vehicle_id, start_date, end_date):
        raise ValidationError("This vehicle is not available for the selected dates.")

    print("\nRENTAL SUMMARY")
    print("-" * 50)
    print(f"Customer       : {customer.name}")
    print(f"Vehicle        : {vehicle.brand} {vehicle.model}")
    print(f"Pickup         : {start_date}")
    print(f"Return         : {end_date}")
    print(f"Rental days    : {days}")
    print(f"Pickup fuel    : {vehicle.fuel_level:.1f}%")
    print(f"Rental amount  : Rs. {vehicle.calculate_rental_cost(days):,.2f}")
    print("-" * 50)

    if read_choice("Confirm? (y/n): ", {"y", "n"}) == "n":
        print("Rental cancelled before payment.")
        return

    payment_processor = choose_payment()
    rental = service.rent_vehicle(
        customer_id, vehicle_id, days, payment_processor, start_date=start_date
    )
    print("\n✅ RENTAL CONFIRMED")
    print(f"Rental ID      : {rental.rental_id}")
    print(f"Payment ref    : {rental.payment['reference']}")
    print(f"Amount paid    : Rs. {rental.payment['amount']:,.2f}")
    print(f"Due date       : {rental.due_date}")
    print(f"Pickup fuel    : {rental.pickup_fuel:.1f}%")


def make_reservation_menu(service):
    print_header("MAKE RESERVATION")
    customer_id = input("Customer ID: ").strip()
    vehicle_id = input("Vehicle ID: ").strip()
    start_date = parse_date_input("Pickup date (YYYY-MM-DD): ")
    end_date = parse_date_input("Return date (YYYY-MM-DD): ")

    vehicle = service.get_vehicle(vehicle_id)
    days = (end_date - start_date).days
    if days <= 0:
        raise ValidationError("Return date must be after pickup date.")
    if not service.is_vehicle_available(vehicle_id, start_date, end_date):
        raise ValidationError("Vehicle is already booked/unavailable for these dates.")

    amount = vehicle.calculate_rental_cost(days)
    print(f"\n{vehicle.brand} {vehicle.model}")
    print(f"{days} day(s) | Total: Rs. {amount:,.2f}")
    print(f"Pickup: {start_date} | Return: {end_date}")

    if read_choice("Confirm reservation? (y/n): ", {"y", "n"}) == "n":
        print("Reservation cancelled before payment.")
        return

    reservation = service.make_reservation(
        customer_id, vehicle_id, start_date, end_date, choose_payment()
    )
    print("\n✅ RESERVATION CONFIRMED")
    print(reservation.summary())
    print(f"Payment ref: {reservation.payment['reference']}")


def show_reservations(service):
    print_header("RESERVATIONS")
    reservations = service.reservations
    if not reservations:
        print("No reservations found.")
        return
    for reservation in reservations:
        print(reservation.summary())

# This cancels a future reservation
def cancel_reservation_menu(service):
    print_header("CANCEL RESERVATION")
    active = service.active_reservations()
    if not active:
        print("No active reservations.")
        return
    for reservation in active:
        print(reservation.summary())

    reservation_id = input("Reservation ID: ").strip()
    reservation = service.get_reservation(reservation_id)

    # Because the customer already paid
    # the function also creates a refund processor
    refund = service.cancel_reservation(
        reservation_id, choose_refund_processor(reservation.payment)
    )
    print("\n✅ RESERVATION CANCELLED")
    print(f"Refund amount : Rs. {refund['amount']:,.2f}")
    print(f"Refund ref    : {refund['reference']}")

'''
Customer reserved vehicle for Sept 10.
Now Sept 10 arrives.
This function starts the reservation
It asks:
    Reservation ID
    Actual pickup date
    Fuel at pickup
'''
def start_reservation_menu(service):
    print_header("START RESERVED VEHICLE")
    active = service.active_reservations()
    if not active:
        print("No active reservations.")
        return
    for reservation in active:
        print(reservation.summary())

    reservation_id = input("Reservation ID: ").strip()
    pickup_date = parse_date_input("Actual pickup date (YYYY-MM-DD): ")
    reservation = service.get_reservation(reservation_id)
    fuel = read_percentage("Fuel at pickup (0-100): ")

    # this converts the reservation into a actual rental
    rental = service.start_reservation(reservation_id, pickup_date, fuel)
    print("\n✅ RESERVED VEHICLE PICKED UP")
    print(f"New Rental ID : {rental.rental_id}")
    print(f"Vehicle       : {rental.vehicle.brand} {rental.vehicle.model}")
    print(f"Due date      : {rental.due_date}")
    print(f"Pickup fuel   : {rental.pickup_fuel:.1f}%")

DAMAGE_OPTIONS = {
    "1": ("Small scratch / paint mark", 500.0),
    "2": ("Deep / large scratch", 1200.0),
    "3": ("Small dent", 1000.0),
    "4": ("Large dent / body damage", 2500.0),
    "5": ("Broken mirror", 1500.0),
    "6": ("Headlight / tail light damage", 3000.0),
    "7": ("Indicator damage", 800.0),
    "8": ("Brake damage", 5000.0),
    "9": ("Tyre damage / puncture", 1200.0),
    "10": ("Handlebar / steering damage", 2000.0),
}


def collect_damage_items():
    """Let the user select predefined damages; the system decides the fine."""
    print("\n" + "=" * 70)
    print("DAMAGE INSPECTION".center(70))
    print("=" * 70)
    print("1. No damage")
    print("2. Vehicle has damage")
    print("=" * 70)

    choice = read_choice("Choose option: ", {"1", "2"})

    if choice == "1":
        print("\n✓ No damage reported. No damage fine added.")
        return []

    damage_items = []
    selected_numbers = set()

    while True:
        print("\nSELECT DAMAGE")
        print("-" * 70)

        for number, (description, charge) in DAMAGE_OPTIONS.items():
            print(
                f"{number:>2}. {description:<38} "
                f"Fine: Rs. {charge:>8,.2f}"
            )

        print(" 0. Finish")
        print("-" * 70)

        damage_choice = input("Select damage option: ").strip()

        if damage_choice == "0":
            if not damage_items:
                print("❌ Please select at least one damage.")
                continue
            break

        if damage_choice not in DAMAGE_OPTIONS:
            print("❌ Invalid option. Please choose from the list.")
            continue

        if damage_choice in selected_numbers:
            print("⚠️ This damage is already selected.")
            continue

        description, charge = DAMAGE_OPTIONS[damage_choice]

        damage_items.append({
            "description": description,
            "charge": charge,
        })

        selected_numbers.add(damage_choice)

        print(f"\n✓ Damage selected: {description}")
        print(f"✓ Automatically added fine: Rs. {charge:,.2f}")

        print("\n1. Add another damage")
        print("2. Finish inspection")

        next_choice = read_choice(
            "Choose: ",
            {"1", "2"}
        )

        if next_choice == "2":
            break

    total = sum(item["charge"] for item in damage_items)

    print("\nSELECTED DAMAGES")
    print("-" * 70)

    for item in damage_items:
        print(
            f"✓ {item['description']:<45} "
            f"Rs. {item['charge']:>8,.2f}"
        )

    print("-" * 70)
    print(
        f"TOTAL DAMAGE FINE{'':<32} "
        f"Rs. {total:>8,.2f}"
    )
    print("-" * 70)

    return damage_items


# Customer returning a rented vehicle
def return_vehicle_menu(service):
    print_header("RETURN VEHICLE + INSPECTION")
    active = service.active_rentals()
    if not active:
        print("No active rentals.")
        return

    for rental in active:
        print(
            f"{rental.rental_id} | {rental.customer.name} | "
            f"{rental.vehicle.vehicle_id} | Due: {rental.due_date} | "
            f"Pickup fuel: {rental.pickup_fuel:.1f}%"
        )

    rental_id = input("\nRental ID: ").strip()
    rental = service.get_rental(rental_id)
    return_date = parse_date_input("Actual return date (YYYY-MM-DD): ")
    return_fuel = read_positive_float("Fuel at return (0-100): ")
    if return_fuel > 100:
        raise ValidationError("Fuel must be between 0 and 100.")

    damage_items = collect_damage_items()
    invoice = service.return_vehicle(rental_id, return_date, return_fuel, damage_items)

    print(invoice.display())
    if invoice.final_amount > rental.payment["amount"]:
        extra = invoice.final_amount - rental.payment["amount"]
        print(f"\n💳 EXTRA PAYMENT REQUIRED: Rs. {extra:,.2f}")
        processor = choose_payment()
        result = processor.process_payment(extra)
        print(f"✅ Extra payment successful: {result['reference']}")
    else:
        print("\n✅ Return completed successfully.")


def cancel_remaining_days_menu(service):
    print_header("CANCEL REMAINING RENTAL DAYS")
    active = service.active_rentals()
    if not active:
        print("No active rentals.")
        return

    for rental in active:
        print(
            f"{rental.rental_id} | {rental.customer.name} | "
            f"{rental.vehicle.vehicle_id} | {rental.start_date} -> {rental.due_date} | "
            f"Paid: Rs. {rental.base_amount:,.2f}"
        )

    rental_id = input("Rental ID: ").strip()
    rental = service.get_rental(rental_id)
    cancel_date = parse_date_input("Cancellation/return date (YYYY-MM-DD): ")
    return_fuel = read_percentage("Fuel at cancellation (0-100): ")
    damage_items = collect_damage_items()

    refund_processor = choose_refund_processor(rental.payment)
    result = service.cancel_remaining_days(
        rental_id, cancel_date, return_fuel, damage_items, refund_processor
    )
    rental_result, used_days, remaining_days, possible_refund, extra_due, settlement = result

    print("\n================ CANCELLATION SUMMARY ================")
    print(f"Used days          : {used_days}")
    print(f"Remaining days     : {remaining_days}")
    print(f"Unused value       : Rs. {possible_refund:,.2f}")
    print(f"Fuel charge        : Rs. {rental_result.fuel_charge:,.2f}")
    print(f"Damage charge      : Rs. {rental_result.damage_charge:,.2f}")

    if settlement and settlement["status"] == "REFUNDED":
        print(f"Refund             : Rs. {settlement['amount']:,.2f}")
        print(f"Refund reference   : {settlement['reference']}")
    elif settlement and settlement["status"] == "SUCCESS":
        print(f"Extra payment      : Rs. {settlement['amount']:,.2f}")
        print(f"Payment reference  : {settlement['reference']}")
    else:
        print("Settlement         : Rs. 0.00")

    print("=======================================================")
    print(f"Vehicle status     : {rental_result.vehicle.status}")
    print("\n✅ Remaining rental days cancelled and vehicle returned.")


def rental_history_menu(service):
    print_header("CUSTOMER RENTAL HISTORY")
    customer_id = input("Customer ID: ").strip()
    print(service.get_customer(customer_id).display_rental_history())


def show_rental_invoice_menu(service):
    print_header("RENTAL / INVOICE")
    if not service.rentals:
        print("No rentals exist yet.")
        return
    for rental in service.rentals:
        print(rental.summary())
    rental_id = input("Rental ID: ").strip()
    print(service.get_rental(rental_id).invoice.display())


def show_active_rentals(service):
    print_header("ACTIVE RENTALS")
    active = service.active_rentals()
    if not active:
        print("No active rentals.")
        return
    for rental in active:
        print(
            f"{rental.rental_id} | {rental.customer.name} | {rental.vehicle.vehicle_id} | "
            f"{rental.vehicle.vehicle_type} | {rental.days} day(s) | Due: {rental.due_date} | "
            f"Fuel: {rental.pickup_fuel:.1f}%"
        )


def show_menu():
    print_header("🚗 VEHICLE RENTAL MANAGEMENT SYSTEM")
    print("1.  Display vehicle fleet")
    print("2.  Search vehicles")
    print("3.  Check availability by date")
    print("4.  Register customer")
    print("5.  Display customers")
    print("6.  Rent a vehicle now")
    print("7.  Make future reservation")
    print("8.  View reservations")
    print("9.  Start reserved vehicle")
    print("10. Cancel reservation")
    print("11. Return vehicle + inspection")
    print("12. Cancel remaining rental days")
    print("13. View active rentals")
    print("14. View customer rental history")
    print("15. View rental / invoice")
    print("0.  Exit")
    print("-" * 78)
    print("Data is automatically saved in data/rental_data.json")


def run_application():
    service = RentalService()
    seed_startup_data(service)

    print_header("WELCOME TO VEHICLE RENTAL MANAGEMENT SYSTEM")
    print("✅ Persistent storage enabled")
    print("✅ Reservations + date availability enabled")
    print("✅ Fuel tracking + damage inspection enabled")
    print("✅ Cancellation + refund enabled")

    while True:
        try:
            show_menu()
            choice = input("\nEnter your choice: ").strip()

            if choice == "1":
                display_vehicles(service)
            elif choice == "2":
                search_vehicles_menu(service)
            elif choice == "3":
                show_date_availability(service)
            elif choice == "4":
                register_customer_menu(service)
            elif choice == "5":
                display_customers(service)
            elif choice == "6":
                rent_vehicle_menu(service)
            elif choice == "7":
                make_reservation_menu(service)
            elif choice == "8":
                show_reservations(service)
            elif choice == "9":
                start_reservation_menu(service)
            elif choice == "10":
                cancel_reservation_menu(service)
            elif choice == "11":
                return_vehicle_menu(service)
            elif choice == "12":
                cancel_remaining_days_menu(service)
            elif choice == "13":
                show_active_rentals(service)
            elif choice == "14":
                rental_history_menu(service)
            elif choice == "15":
                show_rental_invoice_menu(service)
            elif choice == "0":
                print("\n💾 All data saved.")
                print("Thank you for using the Vehicle Rental Management System. 👋")
                break
            else:
                print("❌ Invalid option. Please choose from the menu.")

            if choice != "0":
                pause()

        except (RentalSystemError, ValueError) as exc:
            print(f"\n❌ ERROR: {exc}")
            pause()
        except KeyboardInterrupt:
            print("\n\nProgram interrupted. Goodbye! 👋")
            break


if __name__ == "__main__":
    run_application()
