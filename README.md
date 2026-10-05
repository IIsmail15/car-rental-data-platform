# Car Rental Data Platform

A data engineering portfolio project that simulates a UK car rental business, generates transactional data in PostgreSQL, and builds an analytical warehouse with dbt.

The implemented pipeline uses Python, Faker, PostgreSQL, and dbt. GitHub Actions validates it against an isolated database and includes a deployment workflow for a configured PostgreSQL target. The repository also contains Terraform definitions for an Azure data platform.

## Architecture

```mermaid
flowchart TD
    A[Python + Faker: UK rental data] --> B[PostgreSQL staging schema: 8 source tables]
    B --> C[dbt: 8 stg_ models]
    C --> D[dbt: 4 dimensions + fact_rental]
    D --> E[PostgreSQL warehouse schema]
```

`python -m etl.main` creates the `staging` and `warehouse` schemas, generates sample data, and runs `dbt run`. dbt manages transformation dependencies through `source()` and `ref()`.

With the profile shown below, all 13 dbt models are materialised as tables in `warehouse`. The models under `models/staging/` standardise source column names; the raw source tables remain in the separate `staging` schema.

## Technology

| Component | Technology |
| --- | --- |
| Sample data | Python, Faker with `en_GB` locale |
| Database access | SQLAlchemy, psycopg2, python-dotenv |
| Local and CI database | PostgreSQL 15 |
| Transformations | dbt-postgres |
| Data extraction utility | pandas |
| Validation and automation | pytest, dbt tests, GitHub Actions |
| Azure infrastructure definitions | Terraform, AzureRM provider, ADLS Gen2, PostgreSQL 16, Data Factory, Databricks |

## Run locally

Use Python 3.12, matching CI, and Docker Compose for the local PostgreSQL database. Run commands from the repository root unless stated otherwise.

### 1. Install dependencies

```bash
git clone https://github.com/IIsmail15/car-rental-data-platform.git
cd car-rental-data-platform
python -m venv .venv
```

Activate the environment:

```powershell
# Windows PowerShell
.\.venv\Scripts\Activate.ps1
```

```bash
# macOS / Linux
source .venv/bin/activate
```

Then install the Python dependencies, including dbt and pytest:

```bash
python -m pip install -r requirements.txt
```

### 2. Start PostgreSQL and configure Python

```bash
docker compose up -d
docker compose exec postgres pg_isready -U postgres -d car_rental
```

Wait until PostgreSQL reports that it is accepting connections. Compose exposes port `5432`, creates the `car_rental` database, and persists data in the `postgres_data` volume.

Copy [`.env.example`](.env.example) to `.env`:

```powershell
# Windows PowerShell
Copy-Item .env.example .env
```

```bash
# macOS / Linux
cp .env.example .env
```

The template matches the local Compose database:

```dotenv
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/car_rental
```

To use an existing PostgreSQL database, skip Docker and set `DATABASE_URL` to its connection string. For Neon, use your Neon connection string with `sslmode=require`. Configure dbt to use the same database in the next step.

### 3. Configure dbt

Create `~/.dbt/profiles.yml` (`$HOME\.dbt\profiles.yml` on Windows), creating the `.dbt` directory if needed. Add this profile for the local Compose database:

```yaml
car_rental_dbt:
  target: dev
  outputs:
    dev:
      type: postgres
      host: localhost
      user: postgres
      password: postgres
      port: 5432
      dbname: car_rental
      schema: warehouse
      threads: 1
```

For a remote database, replace the connection fields and set `sslmode: require` when required by the host. Keep credentials out of version control. Python loads `.env`; a standalone dbt command reads its profile and does not load `.env` automatically.

### 4. Build and validate the warehouse

```bash
dbt debug --project-dir car_rental_dbt
python -m etl.main
dbt test --project-dir car_rental_dbt
```

The pipeline command runs these steps:

1. Creates missing schemas and the eight source tables.
2. Generates offices, cars, optional features, drivers, rentals, driver assignments, insurance records, and payments.
3. Runs all dbt models to rebuild the transformed tables.

Tests are a separate step; `etl.main` does not run them. Repeated pipeline runs add random source data and can add assignments or features to existing records. They do not reset the database or reproduce a fixed dataset.

To rebuild and test the models using existing source data:

```bash
dbt build --project-dir car_rental_dbt
```

## Data model

### Source tables

| Table in `staging` | Purpose |
| --- | --- |
| `rental_offices` | UK pickup and dropoff locations |
| `cars` | Vehicle plate, category, model, brand, fuel, and registration date |
| `have_optional` | Optional features associated with each car |
| `drivers` | Driver identity and licence details |
| `rentals` | Rental dates, locations, and mileage; keyed by `(plate, pickupdate)` |
| `drive` | Driver assignments to rentals |
| `insurances` | Risk level and cost per rental |
| `payments` | Amount, discount, and payment mode per rental |

### Warehouse models

| Model | Purpose |
| --- | --- |
| `stg_*` (8 models) | Select source fields and standardise column names |
| `dim_car` | Vehicle attributes with optional features combined using `string_agg` |
| `dim_driver` | Driver attributes keyed by `licensenumber` |
| `dim_office` | Office attributes keyed by `officename` |
| `dim_date` | Distinct pickup dates with calendar attributes |
| `fact_rental` | Rental measures joined to cars, drivers, offices, dates, payments, and aggregated insurance costs |

The fact table has one row per rental, identified by `(car_plate, pickup_date)`, and uses natural keys: car plate, driver licence, office name, and date. Pickup and dropoff offices both reference `dim_office`. `dim_date` covers pickup dates only; `dropoff_date` remains a date column on the fact table.

Insurance costs are summed per rental before joining. If a rental has multiple driver assignments, the current model selects one with `DISTINCT ON`; without an ordering rule, the selected driver is not deterministic.

### Sample data

Defaults for a first run against an empty database:

| Entity | Count |
| --- | --- |
| Rental offices | 5 |
| Cars | 50 |
| Drivers | 40 |
| Rentals | 200 |
| Driver assignments | 200 |
| Insurance records | 200-400 (1-2 per rental) |
| Payments | 200 |

Optional features are assigned randomly to approximately 60% of cars. Generated values and totals on subsequent runs vary.

## Tests

Python tests cover database connectivity, data generation, and source data checks. **Their fixture deletes all rows from the eight staging tables before each test. Use a dedicated test database.**

For the local Compose service, create it once:

```bash
docker compose exec postgres createdb -U postgres car_rental_test
```

Create `.env.test` in the repository root:

```dotenv
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/car_rental_test
```

An existing shell `DATABASE_URL` takes precedence over `.env.test`; ensure it is unset or points to the test database before running:

```bash
python -m pytest -q
```

The configured dbt tests check non-null dimension references, relationships to car/driver/office dimensions, and accepted payment modes. The file `car_rental_dbt/tests/rental_dates_are_valid.sql` is currently empty, so it does not implement a dbt date check.

## CI and deployment

[`ci.yml`](.github/workflows/ci.yml) runs on pushes to `main` and pull requests targeting `main`. It uses Python 3.12 and an isolated PostgreSQL 15 service to run pytest, validate the dbt profile, execute the full pipeline, and run dbt tests.

[`deploy.yml`](.github/workflows/deploy.yml) runs manually or after a successful `CI` workflow run on `main`. It uses the GitHub `production` environment and requires these secrets:

| Secret | Used by |
| --- | --- |
| `DATABASE_URL` | Python setup and data generation |
| `DB_HOST`, `DB_PORT`, `DB_NAME` | dbt connection |
| `PGUSER`, `PGPASSWORD` | dbt authentication |

Both connection configurations must identify the same database. Deployment requires SSL for dbt, runs the full pipeline (including sample data generation), and then runs dbt tests. Environment protection rules may require approval before the job starts.

## Azure infrastructure

[`infra/terraform/`](infra/terraform/) defines:

- An Azure resource group.
- An ADLS Gen2 storage account with `raw` and `curated` filesystems.
- A PostgreSQL 16 Flexible Server and `car_rental` database.
- An Azure Data Factory instance.
- A Premium Azure Databricks workspace.

The configuration requires Terraform `>= 1.6.0` and AzureRM `~> 4.0`. Defaults are `Sweden Central`, project name `carrental`, and environment `dev`; required PostgreSQL administrator values are shown in [`terraform.tfvars.example`](infra/terraform/terraform.tfvars.example).

These files define infrastructure; the repository does not yet define Data Factory pipelines, Databricks jobs, or a data flow through ADLS. The Python/dbt pipeline connects directly to PostgreSQL. Deployment status of the cloud resources is not established by these configuration files.

## Project structure

```text
car-rental-data-platform/
|-- .env.example              # Python connection template
|-- .github/workflows/        # CI and deployment
|-- docker-compose.yml       # Local PostgreSQL 15
|-- requirements.txt         # Python, dbt, and test dependencies
|-- data/
|   |-- generate_data.py     # UK rental sample data
|   `-- sample_data.sql      # Manual office seed
|-- etl/
|   |-- connect.py           # SQLAlchemy engine
|   |-- setup_db.py          # Schemas and source tables
|   |-- extract.py           # Standalone pandas extraction utility
|   `-- main.py              # Setup, generation, and dbt orchestration
|-- init/                    # Docker init SQL and legacy schema comments
|-- car_rental_dbt/
|   |-- dbt_project.yml
|   |-- models/staging/      # Source declarations and 8 staging models
|   |-- models/warehouse/    # 4 dimensions, fact table, and model tests
|   `-- tests/               # Singular SQL tests
|-- tests/                   # Python database tests
`-- infra/terraform/         # Azure infrastructure definitions
```

## Author

**Israa** — MSc Data Science & Business Analytics, Bologna Business School  
[GitHub](https://github.com/IIsmail15)
