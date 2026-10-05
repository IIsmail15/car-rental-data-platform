# Car rental dbt project

Transforms eight PostgreSQL source tables in `staging` into eight `stg_*` models, four dimensions, and `fact_rental`. All models are materialised as tables in the schema configured by the `car_rental_dbt` profile (`warehouse` in the documented setup).

Follow the [repository setup instructions](../README.md#run-locally) to configure PostgreSQL, Python, and `~/.dbt/profiles.yml`, then populate the source tables with the Python pipeline.

From the repository root:

```bash
dbt debug --project-dir car_rental_dbt
dbt build --project-dir car_rental_dbt
```

`dbt build` runs models and their tests against existing source data. It does not generate sample data.

The warehouse uses natural keys. `fact_rental` has one row per `(car_plate, pickup_date)` and sums insurance costs per rental. `dim_date` contains pickup dates only. When a rental has multiple drivers, the fact model selects one without a deterministic ordering rule.

Model tests in [`models/warehouse/schema.yml`](models/warehouse/schema.yml) check non-null dimension references, relationships, and accepted payment modes. [`tests/rental_dates_are_valid.sql`](tests/rental_dates_are_valid.sql) is currently an empty placeholder.
