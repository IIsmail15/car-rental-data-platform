# 🚗 Car Rental Data Platform

An end-to-end data engineering portfolio project that simulates a UK car rental business — from raw transactional data through to an analytics-ready data warehouse.

Built with Python, PostgreSQL, and dbt. Runs with a single command.

---

## 🧱 Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                          SOURCE LAYER                               │
│                                                                     │
│   Python + Faker → Generates realistic UK car rental data           │
└────────────────────────────────┬────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────┐
│                         STAGING SCHEMA (OLTP)                       │
│                                                                     │
│   RENTAL_OFFICES   CARS   HAVE_OPTIONAL   DRIVERS                   │
│   RENTALS   DRIVE   INSURANCES   PAYMENTS                           │
│                                                                     │
│   PostgreSQL — normalised relational tables                         │
└────────────────────────────────┬────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      TRANSFORMATION LAYER (dbt)                     │
│                                                                     │
│   dim_car ──────────────────────────────────────┐                   │
│   dim_driver ────────────────────────────────── ▼                   │
│   dim_office ──────────────────────────────► fact_rental            │
│   dim_date ─────────────────────────────────────┘                   │
│                                                                     │
│   dbt manages dependencies, materialisation, and lineage            │
└────────────────────────────────┬────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────┐
│                       WAREHOUSE SCHEMA (Star Schema)                │
│                                                                     │
│   dim_car   dim_driver   dim_office   dim_date   fact_rental        │
│                                                                     │
│   PostgreSQL — analytics-ready, query-optimised                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## ⭐ Star Schema

```
                        ┌─────────────┐
                        │  dim_date   │
                        │─────────────│
                        │ date_value  │
                        │ year        │
                        │ month       │
                        │ quarter     │
                        │ is_weekend  │
                        └──────┬──────┘
                               │
  ┌─────────────┐    ┌─────────┴──────────┐    ┌─────────────┐
  │   dim_car   │    │    fact_rental      │    │ dim_driver  │
  │─────────────│    │────────────────────│    │─────────────│
  │ plate       │◄───│ car_plate          │    │ licensenumber│
  │ category    │    │ driver_license     │───►│ drivername  │
  │ model       │    │ pickup_office      │    │ birthdate   │
  │ brand       │    │ dropoff_office     │    └─────────────┘
  │ fuel        │    │ pickup_date        │
  │ optional    │    │ dropoff_date       │    ┌─────────────┐
  └─────────────┘    │ miles             │    │ dim_office  │
                     │ amount            │───►│─────────────│
                     │ discount          │    │ officename  │
                     │ payment_mode      │    │ city        │
                     │ insurance_cost    │    │ area        │
                     └────────────────────┘    │ country     │
                                               └─────────────┘
```

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| Data generation | Python, Faker |
| Database | PostgreSQL 15 |
| DB connection | SQLAlchemy, psycopg2 |
| Transformation | dbt (dbt-postgres) |
| Environment | python-dotenv |
| Version control | Git, GitHub |

---

## 📁 Project Structure

```
car-rental-data-platform/
├── .env                        # DB credentials (not committed)
├── .env.example                # Template for DB credentials
├── .gitignore
├── docker-compose.yml          # Postgres 15 container
├── requirements.txt
├── etl/
│   ├── connect.py              # SQLAlchemy engine
│   ├── setup_db.py             # Creates staging schema + tables
│   ├── extract.py              # Reads staging tables into DataFrames
│   └── main.py                 # Pipeline orchestrator
├── data/
│   ├── generate_data.py        # Faker data generation
│   └── sample_data.sql         # Manual seed for rental offices
├── init/
│   ├── 01_staging_schema.sql   # Docker init: staging schema + tables
│   └── 02_warehouse_schema.sql # Docker init: warehouse schema (dbt-managed)
├── car_rental_dbt/
│   ├── models/
│   │   ├── staging/
│   │   │   └── sources.yml     # Declares staging tables as dbt sources
│   │   └── warehouse/
│   │       ├── dim_car.sql
│   │       ├── dim_driver.sql
│   │       ├── dim_office.sql
│   │       ├── dim_date.sql
│   │       └── fact_rental.sql
│   └── dbt_project.yml
└── README.md
```

---

## ⚙️ How to Run

### Prerequisites
- Python 3.9+
- PostgreSQL 15 (or Docker)
- dbt-postgres installed

### Setup

```bash
# Clone the repo
git clone https://github.com/IIsmail15/car-rental-data-platform.git
cd car-rental-data-platform

# Install dependencies
pip install -r requirements.txt

# Start Postgres via Docker (optional — skip if using a local instance)
docker-compose up -d

# Create your .env file from the template and fill in your credentials
cp .env.example .env
```

> **dbt profile**: dbt reads its connection config from `~/.dbt/profiles.yml`. Make sure a profile named `car_rental_dbt` exists there pointing to your database. The `.env` file is used by the Python pipeline only.

### Run the full pipeline

```bash
python -m etl.main
```

This single command:
1. Creates the staging schema and all OLTP tables
2. Generates realistic UK car rental data using Faker
3. Runs all dbt models to build the warehouse

### Run dbt only

```bash
cd car_rental_dbt
dbt run
```

---

## 🗃️ Staging Schema (OLTP)

Eight normalised tables modelling a real car rental business:

| Table | Description |
|-------|-------------|
| `RENTAL_OFFICES` | UK pickup and dropoff locations |
| `CARS` | Fleet of vehicles with plate, brand, fuel type |
| `HAVE_OPTIONAL` | Optional features per car (GPS, child seat etc.) |
| `DRIVERS` | Licensed drivers with expiry dates |
| `RENTALS` | Core rental records — car, dates, offices, miles |
| `DRIVE` | Links drivers to rentals |
| `INSURANCES` | Risk level and cost per rental |
| `PAYMENTS` | Amount, discount, and payment mode per rental |

---

## 🔄 dbt Models

| Model | Type | Description |
|-------|------|-------------|
| `dim_car` | table | Cars with optionals aggregated via `string_agg` |
| `dim_driver` | table | Driver dimension from staging |
| `dim_office` | table | Office locations dimension |
| `dim_date` | table | Date attributes extracted from pickup dates |
| `fact_rental` | table | Central fact table — joins all dims via surrogate keys |

dbt resolves model dependencies automatically via `{{ ref() }}` — dimensions are always built before the fact table.

---

## 🧠 Design Decisions

**Why dbt for transformation?**
The staging → warehouse transformation is exactly dbt's core use case. Rather than writing Pandas joins and loading back to PostgreSQL manually, dbt reads from staging and materialises warehouse tables directly — with automatic dependency resolution, lineage tracking, and documentation built in.

**Why a star schema?**
The warehouse is optimised for analytical queries — e.g. total revenue by office, average miles by car category, rental frequency by month. A star schema with one central fact table and four dimension tables makes these queries simple and fast.

**Why separate staging and warehouse schemas?**
Staging mirrors the source OLTP system. Warehouse is analytics-ready. Keeping them separate means the raw data is always preserved and the transformation logic lives entirely in dbt, not scattered across SQL scripts.

**Why Faker with UK locale?**
The project simulates a UK car rental business. Using `Faker('en_GB')` generates realistic British names, and UK-style number plates add authenticity to the dataset.

---

## 📊 Sample Data Generated

| Entity | Count |
|--------|-------|
| Rental offices | 5 |
| Cars | 50 |
| Drivers | 40 |
| Rentals | 200 |
| Insurance records | ~400 |
| Payments | 200 |

---

## 👩‍💻 Author

**Israa** — MSc Data Science & Business Analytics, Bologna Business School  
[GitHub](https://github.com/IIsmail15)