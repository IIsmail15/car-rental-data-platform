# Car rental dbt project

Reads eight curated Delta tables through Unity Catalog and builds eight `stg_*` tables, four dimensions, and `fact_rental` in the Databricks `analytics` schema. The SQL now targets Databricks; the previous PostgreSQL warehouse profile is not compatible with these models.

## Connect and build

Prerequisites: the eight curated tables from the [Databricks notebooks](../notebooks/README.md), a SQL warehouse, and permission to read `curated` and create tables in `analytics` within the configured catalog.

From the repository root, with the Python environment activated:

```bash
python -m pip install -r requirements-databricks.txt
cp car_rental_dbt/databricks/profiles.example.yml car_rental_dbt/databricks/profiles.yml
dbt debug --project-dir car_rental_dbt --profiles-dir car_rental_dbt/databricks
```

Copy the example only for initial setup; preserve an existing working profile. OAuth opens a browser for interactive sign-in. The example contains the development workspace endpoint and no secrets. Local `profiles.yml` and dbt `.user.yml` files are ignored by Git. For another workspace, update the profile and the catalog in [sources.yml](models/staging/sources.yml).

The source's logical name remains `staging`, so existing `source('staging', ...)` calls resolve to the physical `curated` schema. The profile's `analytics` schema is the output location.

Build models and run their configured tests:

```bash
dbt build --project-dir car_rental_dbt --profiles-dir car_rental_dbt/databricks
```

For an individual model during development, use `dbt run`:

```bash
dbt run --project-dir car_rental_dbt --profiles-dir car_rental_dbt/databricks --select dim_date
```

`dbt run` only builds models. `dbt build` also selects tests; relationship tests can reference a fact table that has not yet been built when selecting only its dimensions. The workflow reads existing curated data and does not generate sample data. All models currently use table materialization and are rebuilt on each run.

## Model behavior

- Staging models select columns already standardized by the PySpark notebook.
- `dim_car` combines optional features using `string_agg`.
- `dim_driver` and `dim_office` retain their existing output names such as `licensenumber` and `officename`.
- `dim_date` contains distinct pickup dates only. Weekday numbering is Sunday = 0 through Saturday = 6; weekends are Saturday and Sunday.
- `fact_rental` is intended to contain one row per `(car_plate, pickup_date)`. It sums insurance costs per rental before joining.
- If a rental has multiple drivers, `row_number()` ordered by `license_number` selects the lowest license number. This is a repeatable representative selection, not a primary-driver business rule.

## Validation

The development session on 2026-10-08 successfully built all 13 models in stages. The user reported that the fact model's configured tests passed and confirmed the following manual SQL checks: 200 staging rentals, 200 fact rows, no duplicate rental keys, and no missing or invalid rental dates. These are results for that sample dataset, not assertions about future runs.

[schema.yml](models/warehouse/schema.yml) defines nine tests for required dimension references, relationships, and accepted payment modes. Three singular SQL tests automate the checks previously performed manually, for a total of 12 data tests:

| Test | Fails when |
| --- | --- |
| [rental_dates_are_valid](tests/rental_dates_are_valid.sql) | A pickup/dropoff date is missing, or dropoff is not after pickup |
| [rental_keys_are_unique](tests/rental_keys_are_unique.sql) | More than one fact row has the same car plate and pickup date |
| [rental_fact_matches_source_count](tests/rental_fact_matches_source_count.sql) | Fact row count differs from the current staging rental count |

Each test returns failing rows; zero returned rows means a pass. The count comparison adjusts to the current dataset rather than expecting 200. Matching counts alone do not prove that every rental key matches; the test also permits an empty source and empty fact table.

Run all 12 tests against the existing tables without rebuilding models:

```bash
dbt test --project-dir car_rental_dbt --profiles-dir car_rental_dbt/databricks
```

The subsequent live run of this command passed all 12 tests. Saved `run_results.json` recorded 12 passes at 2026-10-08 22:09 UTC, including zero failures in each of the three new singular tests. Local validation also checked the SQL against isolated valid, duplicate, missing-row, extra-row, null-date, equal-date, and reversed-date examples before the live run.

The equivalent manual checks remain useful in the Databricks SQL Editor after building:

```sql
USE CATALOG dbw_carrental_dev_7405614156846449;
USE SCHEMA analytics;

-- Counts must match; the verified sample had 200 in each.
SELECT 'stg_rentals' AS table_name, COUNT(*) AS row_count FROM stg_rentals
UNION ALL
SELECT 'fact_rental', COUNT(*) FROM fact_rental;

-- Expect zero rows.
SELECT car_plate, pickup_date, COUNT(*) AS row_count
FROM fact_rental
GROUP BY car_plate, pickup_date
HAVING COUNT(*) > 1;

-- Expect zero.
SELECT COUNT(*) AS invalid_dates
FROM fact_rental
WHERE pickup_date IS NULL
   OR dropoff_date IS NULL
   OR dropoff_date <= pickup_date;
```

## Pending automation

CI parses this project with the Databricks adapter without connecting to a warehouse. The 12 data tests still require a live Databricks connection.

ADF ingestion, notebook execution, and dbt remain separate manual stages. The old PostgreSQL deployment workflow has been removed. Unattended authentication and orchestration remain pending. `etl.main` is still a legacy entry point and should not run this Azure sequence.
