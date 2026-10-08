# Databricks transformations

These notebooks were exported from the working Azure Databricks workspace. Saved outputs and execution metadata are removed for version control; code cells, including SQL cells, are retained.

| Notebook | Purpose |
| --- | --- |
| `01_cars_raw_to_curated.ipynb` | Learning walkthrough: inspect cars, check keys, rename the registration date, write Delta, and register the external table. |
| `02_all_tables_raw_to_curated.ipynb` | Validate and process all eight source tables, verify saved row counts, and register them in Unity Catalog. |

## Run in Databricks

1. Run ADF's `pl_all_tables_to_raw` pipeline and wait for all eight copies to finish.
2. Import the notebook into a Unity Catalog-enabled Databricks workspace and attach notebook compute.
3. Confirm access to the `raw` and `curated` external locations in `stcarrentaldev` and permission to create tables in the target catalog.
4. For the complete workflow, run `02_all_tables_raw_to_curated.ipynb` from top to bottom. Running the cars walkthrough first is optional.

The notebooks use Databricks-provided `spark` and `display`; the project's local Python environment is not a replacement for Databricks compute. The storage account and catalog `dbw_carrental_dev_7405614156846449` are currently hardcoded in the cells. Update them when using another environment.

The all-table notebook reads `raw/<table>/<TABLE>.parquet`, checks keys, eight foreign-key relationships, and rental dates, then standardises column names and adds `processed_at`. It writes Delta data to `curated/<table>` and registers external tables under the catalog's `curated` schema.

Each run overwrites the current contents of each curated table. Writes are committed separately per table; a failure partway through can leave earlier tables refreshed. Source ingestion and notebook execution are currently separate manual steps. The notebooks do not build dbt dimensions or facts.

The cars walkthrough prints key-check results for learning. The all-table notebook raises errors for failed key and business checks before reaching its write loop.

## Updating the exports

Export notebooks as IPython notebooks with **Include outputs** disabled. Keep passwords, storage keys, and execution outputs out of committed notebook files. Review the diff before committing a new export.
