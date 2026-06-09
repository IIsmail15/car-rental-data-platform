import psycopg2
import random
from faker import Faker
from dotenv import load_dotenv
from datetime import timedelta
import os


load_dotenv()

fake = Faker('en_GB')

conn = psycopg2.connect(os.environ["DATABASE_URL"])
cur = conn.cursor()

def generate_offices(): 
    offices = [('Manchester Airport', 'Manchester', 'North West', 'England', 'UK'),
        ('London Heathrow', 'London', 'West London', 'England', 'UK'),
        ('Birmingham Central', 'Birmingham', 'West Midlands', 'England', 'UK'),
        ('Edinburgh Airport', 'Edinburgh', 'Lothian', 'Scotland', 'UK'),
        ('Bristol Temple', 'Bristol', 'South West', 'England', 'UK'),
        ]
    cur.executemany("""
        INSERT INTO staging.RENTAL_OFFICES (OfficeName, City, Area, State, Country)
        VALUES (%s, %s, %s, %s, %s) ON CONFLICT DO NOTHING;
    """, offices)
    conn.commit()
    print(f"Inserted {len(offices)} offices")
    return offices

def generate_cars(n= 50):
    categories = ['Economy', 'Compact', 'Midsize', 'SUV', 'Luxury']
    brands_models = {
        'Toyota': ['Corolla', 'Yaris', 'RAV4'],
        'Ford': ['Fiesta', 'Focus', 'Escape'],
        'BMW': ['3 Series', '5 Series', 'X5'],
        'Vauxhall': ['Corsa', 'Astra', 'Mokka'],
        'Mercedes': ['A-Class', 'C-Class', 'GLE']
    }
    fuels = ['Petrol', 'Diesel', 'Electric', 'Hybrid']
    cars = []
    plate_used = set()
    for _ in range(n):
        # Generate a unique UK-style plate
        while True:
            plate = (
                fake.lexify('??', letters='ABCDEFGHIJKLMNOPQRSTUVWXYZ') +
                fake.numerify('###')
                + ' '
                + fake.lexify('???', letters='ABCDEFGHIJKLMNOPQRSTUVWXYZ')
            )
            if plate not in plate_used:
                plate_used.add(plate)
                break

        brand = random.choice(list(brands_models.keys()))
        model = random.choice(brands_models[brand])
        category = random.choice(categories)
        fuel = random.choice(fuels)
        reg_date = fake.date_between(start_date = '-8y', end_date = '-1y')
        cars.append((plate, category, model, brand, fuel, reg_date))

    cur.executemany("""
        INSERT INTO staging.CARS (Plate, Category, Model, Brand, Fuel, RegistrationDate)
        VALUES (%s, %s, %s, %s, %s, %s) 
        ON CONFLICT DO NOTHING;
        """,cars)
    print(f"Inserted {len(cars)} cars") 

def generate_have_optional():
    optionals = ['GPS', 'Child Seat', 'Roof Rack', 'Bluetooth', 'Dashcam']

    # Fetch all plates currently in the database
    cur.execute("SELECT Plate FROM staging.CARS;")
    plates = [row[0] for row in cur.fetchall()]

    rows = []
    for plate in plates:
        # Only give optionals to ~60% of cars
        if random.random() < 0.6:
            # Pick 1 to 3 random features, no duplicates per car
            chosen = random.sample(optionals, k=random.randint(1, 3))
            for feature in chosen:
                rows.append((plate, feature))

    cur.executemany("""
        INSERT INTO staging.HAVE_OPTIONAL (Plate, Optional)
        VALUES (%s, %s)
        ON CONFLICT DO NOTHING;
    """, rows)

    print(f"Inserted {len(rows)} optional features")

def generate_drivers(n=40):
    drivers = []
    licenses_used = set()

    for _ in range(n):
        # Generate a unique fake UK license number
        while True:
            license_num = (
                fake.lexify('?????', letters='ABCDEFGHIJKLMNOPQRSTUVWXYZ')
                + fake.numerify('#####')
            )
            if license_num not in licenses_used:
                licenses_used.add(license_num)
                break

        birthdate = fake.date_of_birth(minimum_age=21, maximum_age=70)
        license_expiry = fake.date_between(start_date='today', end_date='+10y')
        name = fake.name()

        drivers.append((license_num, license_expiry, name, birthdate))

    cur.executemany("""
        INSERT INTO staging.DRIVERS 
            (LicenseNumber, LicenseExpiration, DriverName, Birthdate)
        VALUES (%s, %s, %s, %s)
        ON CONFLICT DO NOTHING;
    """, drivers)

    print(f"Inserted {len(drivers)} drivers")


def generate_rentals(n=200):
    cur.execute("SELECT Plate FROM staging.CARS;")
    plates = [row[0] for row in cur.fetchall()]

    cur.execute("SELECT OfficeName FROM staging.RENTAL_OFFICES;")
    offices = [row[0] for row in cur.fetchall()]

    rentals = []
    combos_used = set()

    attempts = 0
    while len(rentals) < n and attempts < n * 10:
        attempts += 1

        plate = random.choice(plates)
        pickup_date = fake.date_between(start_date='-3y', end_date='-1d')

        combo = (plate, pickup_date)
        if combo in combos_used:
            continue
        combos_used.add(combo)

        rental_days = random.randint(1, 14)
        dropoff_date = pickup_date + timedelta(days=rental_days)

        pickup_office = random.choice(offices)
        dropoff_office = random.choice(offices)

        miles = round(random.uniform(50, 2000), 1)

        rentals.append((plate, pickup_date, dropoff_date,
                        pickup_office, dropoff_office, miles))

    cur.executemany("""
        INSERT INTO staging.RENTALS
            (Plate, PickupDate, DropoffDate, PickupPlace, DropoffPlace, Miles)
        VALUES (%s, %s, %s, %s, %s, %s)
        ON CONFLICT DO NOTHING;
    """, rentals)

    print(f"Inserted {len(rentals)} rentals") 



def generate_drive():
    cur.execute("SELECT Plate, PickupDate FROM staging.RENTALS;")
    rentals = cur.fetchall()

    cur.execute("SELECT LicenseNumber FROM staging.DRIVERS;")
    drivers = [row[0] for row in cur.fetchall()]

    rows = []
    for plate, pickup_date in rentals:
        license_num = random.choice(drivers)
        rows.append((license_num, plate, pickup_date))

    cur.executemany("""
        INSERT INTO staging.DRIVE
            (LicenseNumber, Plate, PickupDate)
        VALUES (%s, %s, %s)
        ON CONFLICT DO NOTHING;
    """, rows)

    print(f"Inserted {len(rows)} drive records")

def generate_insurances():
    cur.execute("SELECT Plate, PickupDate FROM staging.RENTALS;")
    rentals = cur.fetchall()

    risk_levels = ['Basic', 'Standard', 'Premium']
    rows = []
    combos_used = set()

    for plate, pickup_date in rentals:
        chosen_risks = random.sample(risk_levels, k=random.randint(1, 2))
        for risk in chosen_risks:
            combo = (risk, plate, pickup_date)
            if combo not in combos_used:
                combos_used.add(combo)
                cost = round(random.uniform(10, 150), 2)
                rows.append((risk, plate, pickup_date, cost))

    cur.executemany("""
        INSERT INTO staging.INSURANCES
            (Risk, Plate, PickupDate, Cost)
        VALUES (%s, %s, %s, %s)
        ON CONFLICT DO NOTHING;
    """, rows)

    print(f"Inserted {len(rows)} insurance records")

def generate_payments():
    cur.execute("SELECT Plate, PickupDate, Miles FROM staging.RENTALS;")
    rentals = cur.fetchall()

    payment_modes = ['Credit Card', 'Debit Card', 'Cash', 'Bank Transfer']
    rows = []

    for plate, pickup_date, miles in rentals:
        amount = round(miles * random.uniform(0.3, 0.8), 2)
        discount = round(random.choice([0, 0, 0, 5, 10, 15]), 2)
        mode = random.choice(payment_modes)
        rows.append((plate, pickup_date, amount, discount, mode))

    cur.executemany("""
        INSERT INTO staging.PAYMENTS
            (Plate, PickupDate, Amount, Discount, PaymentMode)
        VALUES (%s, %s, %s, %s, %s)
        ON CONFLICT DO NOTHING;
    """, rows)

    print(f"Inserted {len(rows)} payment records")


def main():
    print("Starting data generation...")
    generate_offices()
    generate_cars()
    generate_have_optional()
    generate_drivers()
    generate_rentals()
    generate_drive()
    generate_insurances()
    generate_payments()
    conn.commit()
    cur.close()
    conn.close()
    print("All done. Database populated.")

if __name__ == "__main__":
    main()