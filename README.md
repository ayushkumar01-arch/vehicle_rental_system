# Vehicle Rental Management System - Updated

## Run
```bash
python main.py
```

The system automatically creates and updates:

`data/rental_data.json`

## Main features
- Vehicle rental and return
- Future reservations
- Date-based availability checking
- Reservation cancellation and refund
- Cancellation of remaining rental days with refund
- Fuel level recorded at pickup and checked at return
- Damage inspection and extra charges
- Late-return fees
- Card and UPI payment simulation
- Persistent JSON storage after every change
- Interactive terminal menus

## Important behavior
- Use **Make future reservation** for a future pickup date.
- Use **Rent a vehicle now** for a rental starting today.
- Returning with less fuel than pickup creates a fuel charge.
- Damage can be entered as multiple items with individual charges.
- Cancelling an active rental calculates unused-day value and settles fuel/damage charges against the refund.
