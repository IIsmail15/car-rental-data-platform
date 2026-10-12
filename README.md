# Car Rental Data Platform

A data engineering portfolio project that simulates a UK car rental business. Python generates transactional data in Azure PostgreSQL, Azure Data Factory copies it into ADLS Gen2, Databricks validates and curates it, and dbt builds an analytical warehouse in Databricks.

ADF now orchestrates ingestion, Databricks curation, and the dbt build from a single pipeline trigger. A manually triggered end-to-end run succeeded on 2026-10-09, with all 13 dbt models and 12 data tests passing. A scheduled demonstration is planned; its result has not yet been verified.

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

The orchestration follows this dependency chain:

```mermaid
flowchart LR
    T[ADF manual or scheduled trigger] --> F[ForEach: copy 8 tables]
    F -->|Succeeded| J[Run Databricks job]
    subgraph job_carrental_curated_warehouse
        N[raw_to_curated: notebook] -->|All succeeded| B[dbt_build: dbt build]
    end
    J --> N
```

See the [Databricks job notes](databricks/README.md) for task settings and export status. Sample data generation remains a separate setup step.

ADLS stores the curated Delta files; Unity Catalog registers them and Databricks provides the compute. The warehouse now uses Databricks SQL, replacing the earlier PostgreSQL/dbt target.

## Current status

Verified during development on 2026-10-08 and the orchestrated run on 2026-10-09:

- All eight ADF table copies succeeded and their raw files were inspected.
- Raw-to-curated key, relationship, date, and row count checks passed.
- All 13 dbt models built successfully in stages on Databricks.
- The user reported successful fact model tests and manual checks: 200 source rentals, 200 fact rows, no duplicate rental keys, and no missing or invalid rental dates.
- The subsequent Databricks `dbt test` run passed all 12 data tests, including the three newly automated rental checks (saved run results: 2026-10-08 22:09 UTC).

- ADF's `ForEach1` and downstream `run_databricks_workflow` activity both succeeded.
- The Databricks job's `raw_to_curated` and `dbt_build` tasks both succeeded. The latest shared successful job run was `1083083368650268` (3 minutes 1 second).
- The job's dbt output reported `PASS=25 WARN=0 ERROR=0 SKIP=0 NO-OP=0 REUSED=0 TOTAL=25`: 13 table models and 12 data tests, completed in 14.96 seconds.

CI checks the Python source code against a temporary PostgreSQL database and parses the Databricks dbt project without connecting to Azure. Cloud execution is orchestrated by ADF and Databricks; CI does not deploy or trigger this workflow. The ADF ARM snapshot includes the job activity, managed-identity Databricks connection, and schedule. The [Databricks job YAML](databricks/job_carrental_curated_warehouse.yml) captures both tasks and their execution settings.

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

On macOS/Linux, activate with `source .venv/bin/activate`; in PowerShell use `.\.venv\Scripts\Activate.ps1`. `requirements.txt` contains Python source and test dependencies. `requirements-databricks.txt` contains the pinned dbt and Databricks adapter versions.

### 1. Populate PostgreSQL when needed

Copy [.env.example](.env.example) to `.env` and set `DATABASE_URL` to the PostgreSQL source connection string. Keep credentials out of Git. Python loads `.env`; standalone dbt uses its own connection profile.

```bash
python -m etl.setup_db
python -m data.generate_data
```

Skip generation when the source is already populated. Repeated generation adds random data; it does not reset or reproduce a fixed dataset. `etl.main` still invokes the old PostgreSQL/dbt workflow and is not the entry point for this Azure sequence.

### 2. Trigger the complete workflow in ADF

Ensure PostgreSQL is running and ready, then trigger the published `pl_all_tables_to_raw` pipeline once. Its sequential ForEach copies all eight tables; the success dependency then starts `job_carrental_curated_warehouse`. That job runs `raw_to_curated`, followed by `dbt_build` only after curation succeeds. See [ADF setup and export notes](adf/README.md).

In ADF Monitor, check the pipeline and both top-level activities. In the corresponding Databricks job run, check both tasks and the final dbt summary. A successful build currently reports 25 passes: 13 models and 12 tests. No separate notebook or local dbt run is needed after a successful pipeline run.

For a scheduled run, publish and activate the ADF trigger with the intended date, time zone, and recurrence. Keep scheduling in ADF so ingestion finishes before transformations begin. The schedule does not start a stopped PostgreSQL server; start it before the trigger fires. Capture the trigger and pipeline run details as evidence after completion. A configured schedule alone does not prove a successful scheduled run.

The 2026-10-09 export's `trg_carrental_weekly` actually runs **daily at 16:55 UK time**, with an end time of 2026-10-15 08:00. It was exported as Started; the repository snapshot records Stopped. That local change does not disable the live trigger. See the [exported schedule details](adf/README.md#exported-schedule) before reusing it.

### 3. Run curation independently during development (optional)

Run [02_all_tables_raw_to_curated.ipynb](notebooks/02_all_tables_raw_to_curated.ipynb) from top to bottom. It validates the source data, overwrites eight curated Delta tables, verifies counts, and registers the external tables. Required access connector, storage permissions, and external locations are described in [notebooks/README.md](notebooks/README.md).

The notebook refreshes tables individually, so a failed run can leave only some tables refreshed. The job's success dependency prevents the downstream dbt task from running when curation fails, but does not roll back earlier table writes. For manual development, confirm the whole notebook succeeded before running dbt. `01_cars_raw_to_curated.ipynb` is the introductory walkthrough; it is not an additional required stage.

### 4. Connect dbt locally during development (optional)

For initial setup, copy the credential-free example; preserve an existing working profile:

```bash
cp car_rental_dbt/databricks/profiles.example.yml car_rental_dbt/databricks/profiles.yml
dbt debug --project-dir car_rental_dbt --profiles-dir car_rental_dbt/databricks
dbt build --project-dir car_rental_dbt --profiles-dir car_rental_dbt/databricks
```

OAuth opens a browser for sign-in. The profile selects the development SQL warehouse, catalog `dbw_carrental_dev_7405614156846449`, and output schema `analytics`. [sources.yml](car_rental_dbt/models/staging/sources.yml) independently selects the input catalog and `curated` schema. Update both for another environment.

See the [dbt README](car_rental_dbt/README.md) for model behavior, partial runs, and automated tests for row counts, duplicate rentals, and dates. The SQL warehouse must be available; stop idle compute when finished.

### After a demonstration

Disable the ADF trigger if no further runs are intended. Stop the SQL warehouse and any unused classic Databricks compute, and stop PostgreSQL when source access is no longer needed. Set the serverless SQL warehouse's auto-stop to 5 minutes. PostgreSQL automatically starts again after seven days stopped; storage charges can continue while compute is stopped. Review Azure costs rather than assuming a stopped service has no remaining charges.

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

dbt has 12 data tests: nine model tests for required dimension references, relationships, and accepted payment modes, plus three singular SQL tests for rental row count, uniqueness, and valid dates. All 12 passed against the Databricks warehouse on 2026-10-08. Run them against existing tables with `dbt test --project-dir car_rental_dbt --profiles-dir car_rental_dbt/databricks`. See the [dbt README](car_rental_dbt/README.md) for the test definitions and equivalent manual SQL.

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

## CI and deployment

[ci.yml](.github/workflows/ci.yml) runs on pushes to `main`, pull requests targeting `main`, and manual dispatches.

It contains two independent jobs:

- `test`: runs Python tests against a disposable PostgreSQL 15 service.
- `dbt-parse`: installs the Databricks adapter and parses the dbt project using the placeholder profile in `.github/dbt/profiles.yml`.

Neither job connects to Azure. Parsing checks project configuration and references; it does not execute warehouse SQL or run the 12 data tests.

The old PostgreSQL deployment workflow has been removed. Successful CI no longer launches that deployment.

ADF now starts the Databricks job through a managed-identity linked service after ingestion succeeds, and the job runs curation followed by `dbt build`. This orchestration has passed a manually triggered end-to-end run. Automated deployment from GitHub remains pending. The ARM snapshot references an existing Databricks job; it does not create that job or its permissions. The saved job YAML captures the task definitions, but omits the Run as principal and permission assignments and is not a complete deployment bundle.

## Azure infrastructure

[infra/terraform/](infra/terraform/) defines a resource group, ADLS Gen2 account with `raw` and `curated` filesystems, PostgreSQL Flexible Server and database, Data Factory, and a Premium Databricks workspace. It requires Terraform `>= 1.6.0` and AzureRM `~> 4.0`; defaults are Sweden Central, project `carrental`, and environment `dev`.

The access connector, storage role assignments, and Unity Catalog storage credentials/external locations were configured separately and are not yet managed by Terraform. The refreshed ADF child-resource template includes orchestration, while notebook exports, the saved job YAML, and [Databricks task documentation](databricks/README.md) record the transformation flow. These snapshots have not been deployed from the repository.

## Project structure

```text
car-rental-data-platform/
|-- .env.example              # PostgreSQL source connection template
|-- .github/workflows/        # Python tests and offline dbt parsing
|-- docker-compose.yml       # Local PostgreSQL for source development/tests
|-- requirements.txt         # Python source and test dependencies
|-- requirements-databricks.txt # Verified Databricks dbt versions
|-- adf/                     # ADF export and setup notes
|-- databricks/              # Exported job YAML and task documentation
|-- notebooks/               # Databricks raw-to-curated notebooks
|-- data/                    # Sample data generator
|-- etl/                     # PostgreSQL setup and extraction utilities
|-- init/                    # Source SQL and legacy warehouse schema
|-- car_rental_dbt/
|   |-- databricks/          # Example and ignored local connection profile
|   |-- models/staging/     # Curated source declarations and 8 staging models
|   |-- models/warehouse/   # 4 dimensions, fact table, and model tests
|   `-- tests/              # Rental dates, uniqueness, and row count tests
|-- tests/                  # Python database tests
`-- infra/terraform/        # Azure infrastructure definitions
```

## Author

**I.Ismail** 

[GitHub](https://github.com/IIsmail15)
