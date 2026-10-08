# Car Rental Data Platform

A data engineering portfolio project that simulates a UK car rental business. Python generates transactional data in Azure PostgreSQL, Azure Data Factory copies it into ADLS Gen2, Databricks validates and curates it, and dbt builds an analytical warehouse in Databricks.

The complete data path has been exercised manually. Scheduling and automated orchestration are still pending.

## Architecture

```mermaid
flowchart LR
    A[Python + Faker] --> B[PostgreSQL: 8 staging tables]
    B --> C[ADF: ForEach + Copy]
    C --> D[ADLS raw: Parquet]
    D --> E[Databricks: validate and standardise]
    E --> F[ADLS curated: Delta / Unity Catalog]
    F --> G[dbt on Databricks SQL]
    G --> H[analytics: 8 staging models, 4 dimensions, 1 fact]
```

The [ADF export](adf/README.md) copies each table to `raw/<table>/<TABLE>.parquet`. The [Databricks notebooks](notebooks/README.md) validate keys, references, and rental dates, standardise column names, add `processed_at`, write Delta tables, and register them in Unity Catalog. dbt reads these tables from `curated` and builds all 13 models in `analytics`.

ADLS stores the curated Delta files; Unity Catalog registers them and Databricks provides the compute. The warehouse now uses Databricks SQL, replacing the earlier PostgreSQL/dbt target.

## Current status

Verified during the development session on 2026-10-08:

- All eight ADF table copies succeeded and their raw files were inspected.
- Raw-to-curated key, relationship, date, and row count checks passed.
- All 13 dbt models built successfully in stages on Databricks.
- The user reported successful fact model tests and manual checks: 200 source rentals, 200 fact rows, no duplicate rental keys, and no missing or invalid rental dates.

ADF, the notebooks, and dbt are run separately. The existing GitHub Actions workflows still configure PostgreSQL and are not compatible with the migrated dbt models. Updating CI, deployment, and orchestration is remaining work; the current Azure workflow is not an automated deployment.

## Technology

| Component | Technology |
| --- | --- |
| Sample data | Python, Faker with `en_GB` locale |
| Transactional source | Azure PostgreSQL 16; PostgreSQL 15 for local Python tests |
| Database access | SQLAlchemy, psycopg2, python-dotenv |
| Ingestion | Azure Data Factory |
| Storage | ADLS Gen2, Parquet, Delta Lake |
| Curation | Databricks, PySpark, Unity Catalog |
| Warehouse | dbt-core 1.12.4, dbt-databricks 1.12.6, Databricks SQL |
| Infrastructure | Terraform, AzureRM provider |

## Run the Azure workflow

Use Python 3.12 and run terminal commands from the repository root. For Windows Git Bash:

```bash
python -m venv .venv
source .venv/Scripts/activate
python -m pip install -r requirements.txt
python -m pip install -r requirements-databricks.txt
```

On macOS/Linux, activate with `source .venv/bin/activate`; in PowerShell use `.\.venv\Scripts\Activate.ps1`. `requirements.txt` still includes the old PostgreSQL adapter for the legacy workflow; the additional requirements file pins the dbt versions used in the successful Databricks session.

### 1. Populate PostgreSQL when needed

Copy [.env.example](.env.example) to `.env` and set `DATABASE_URL` to the PostgreSQL source connection string. Keep credentials out of Git. Python loads `.env`; standalone dbt uses its own connection profile.

```bash
python -m etl.setup_db
python -m data.generate_data
```

Skip generation when the source is already populated. Repeated generation adds random data; it does not reset or reproduce a fixed dataset. `etl.main` still invokes the old PostgreSQL/dbt workflow and is not the entry point for this Azure sequence.

### 2. Copy all eight tables with ADF

Run the published `pl_all_tables_to_raw` pipeline and check that every copy succeeds. See [ADF setup and export notes](adf/README.md). The saved generic sink dataset has an empty schema; the exported live dataset originally had cars-only columns. Clear that schema in the live dataset and publish if this correction has not yet been applied.

### 3. Validate and curate in Databricks

Run [02_all_tables_raw_to_curated.ipynb](notebooks/02_all_tables_raw_to_curated.ipynb) from top to bottom. It validates the source data, overwrites eight curated Delta tables, verifies counts, and registers the external tables. Required access connector, storage permissions, and external locations are described in [notebooks/README.md](notebooks/README.md).

The notebook refreshes tables individually, so a failed run can leave only some tables refreshed. Confirm the whole notebook succeeded before running dbt. `01_cars_raw_to_curated.ipynb` is the introductory walkthrough; it is not an additional required stage.

### 4. Connect dbt and build the warehouse

For initial setup, copy the credential-free example; preserve an existing working profile:

```bash
cp car_rental_dbt/databricks/profiles.example.yml car_rental_dbt/databricks/profiles.yml
dbt debug --project-dir car_rental_dbt --profiles-dir car_rental_dbt/databricks
dbt build --project-dir car_rental_dbt --profiles-dir car_rental_dbt/databricks --exclude rental_dates_are_valid
```

OAuth opens a browser for sign-in. The profile selects the development SQL warehouse, catalog `dbw_carrental_dev_7405614156846449`, and output schema `analytics`. [sources.yml](car_rental_dbt/models/staging/sources.yml) independently selects the input catalog and `curated` schema. Update both for another environment.

The command excludes the empty date-test placeholder; the date check is currently manual. See the [dbt README](car_rental_dbt/README.md) for model behavior, partial runs, and SQL checks for row counts, duplicate rentals, and dates. The SQL warehouse must be available; stop idle compute when finished.

## Data model

| PostgreSQL source table | Purpose |
| --- | --- |
| `rental_offices` | UK pickup and dropoff locations |
| `cars` | Vehicle identity and attributes |
| `have_optional` | Optional features associated with cars |
| `drivers` | Driver identity and licence details |
| `rentals` | Rental dates, locations, and mileage |
| `drive` | Driver assignments to rentals |
| `insurances` | Risk level and cost per rental |
| `payments` | Amount, discount, and payment mode |

| Warehouse model | Purpose |
| --- | --- |
| `stg_*` (8) | Select standardized curated columns |
| `dim_car` | Car attributes and aggregated optional features |
| `dim_driver` | Driver attributes keyed by `licensenumber` |
| `dim_office` | Office attributes keyed by `officename` |
| `dim_date` | Distinct pickup dates and calendar attributes |
| `fact_rental` | Rental measures and dimension references |

The intended fact grain is one row per `(car_plate, pickup_date)`. Insurance costs are summed before joining. For multiple drivers, the model selects the lowest `license_number` using `row_number()`; this is a repeatable selection, not a primary-driver designation. Pickup and dropoff offices share `dim_office`. `dim_date` contains pickup dates only; `dropoff_date` remains on the fact table.

Initial generator defaults are 5 offices, 50 cars, 40 drivers, 200 rentals, 200 driver assignments, 200 payments, and 1-2 insurance records per rental. Optional features and other generated values vary.

## Tests

dbt's model tests check required dimension references, relationships, and accepted payment modes. Rental row count, uniqueness, and date checks were run manually; their SQL is in the [dbt README](car_rental_dbt/README.md). The singular test file `car_rental_dbt/tests/rental_dates_are_valid.sql` is still an empty placeholder.

Python tests cover the PostgreSQL source and generator. **Their fixture deletes source rows before each test. Use a dedicated test database.** For local tests, Docker Compose provides PostgreSQL 15:

```bash
docker compose up -d
docker compose exec postgres pg_isready -U postgres -d car_rental
docker compose exec postgres createdb -U postgres car_rental_test
```

Wait for readiness, and create the test database only once. Set `.env.test` to:

```dotenv
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/car_rental_test
```

An existing shell `DATABASE_URL` takes precedence over `.env.test`; ensure it is unset or targets the test database, then run `python -m pytest -q`. These tests do not validate the live Databricks warehouse.

## CI and deployment: migration pending

[ci.yml](.github/workflows/ci.yml) currently runs Python tests and the previous PostgreSQL/dbt pipeline on pushes to `main` and pull requests. Its dbt steps need migration for the current SQL and curated sources.

[deploy.yml](.github/workflows/deploy.yml) currently runs manually or after successful CI on `main`. It uses PostgreSQL secrets and calls `etl.main`, including source data generation. It does not deploy the Databricks workflow. Update these workflows and choose unattended authentication before relying on them for this warehouse.

Remaining work includes automating the manual warehouse checks, migrating CI/deployment, and orchestrating ADF, Databricks curation, and dbt in sequence. Browser OAuth is currently used for interactive development.

## Azure infrastructure

[infra/terraform/](infra/terraform/) defines a resource group, ADLS Gen2 account with `raw` and `curated` filesystems, PostgreSQL Flexible Server and database, Data Factory, and a Premium Databricks workspace. It requires Terraform `>= 1.6.0` and AzureRM `~> 4.0`; defaults are Sweden Central, project `carrental`, and environment `dev`.

The access connector, storage role assignments, and Unity Catalog storage credentials/external locations were configured separately and are not yet managed by Terraform. ADF child resources and notebook exports are stored in this repository; Databricks job definitions are not yet included.

## Project structure

```text
car-rental-data-platform/
|-- .env.example              # PostgreSQL source connection template
|-- .github/workflows/        # Legacy PostgreSQL CI/deployment; migration pending
|-- docker-compose.yml       # Local PostgreSQL for source development/tests
|-- requirements.txt         # Python and legacy PostgreSQL dbt dependencies
|-- requirements-databricks.txt # Verified Databricks dbt versions
|-- adf/                     # ADF export and setup notes
|-- notebooks/               # Databricks raw-to-curated notebooks
|-- data/                    # Sample data generator
|-- etl/                     # PostgreSQL setup and extraction utilities
|-- init/                    # Source SQL and legacy warehouse schema
|-- car_rental_dbt/
|   |-- databricks/          # Example and ignored local connection profile
|   |-- models/staging/     # Curated source declarations and 8 staging models
|   |-- models/warehouse/   # 4 dimensions, fact table, and model tests
|   `-- tests/              # Singular SQL test placeholder
|-- tests/                  # Python database tests
`-- infra/terraform/        # Azure infrastructure definitions
```

## Author

**Israa** - MSc Data Science & Business Analytics, Bologna Business School

[GitHub](https://github.com/IIsmail15)
