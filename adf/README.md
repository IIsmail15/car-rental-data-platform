# Azure Data Factory ingestion

The ARM template contains the exported child resources for `adf-carrental-dev`: two linked services, four datasets, and two pipelines.

| Pipeline | Behaviour |
| --- | --- |
| `pl_cars_to_raw` | Copies `staging.cars` to `raw/cars/CARS.parquet`. |
| `pl_all_tables_to_raw` | Sequentially loops through eight tables and copies each to `raw/<table>/<TABLE>.parquet`. |

The table list is `rental_offices`, `cars`, `have_optional`, `drivers`, `rentals`, `drive`, `insurances`, and `payments`. Both pipelines write Parquet with Snappy compression. The reusable datasets pass `table_name` from the ForEach `@item()` expression. No scheduled triggers or Databricks activities are included in this export.

## Files and credentials

- `ARMTemplateForFactory.json`: pipeline, dataset, and linked-service definitions.
- `ARMTemplateParametersForFactory.example.json`: environment values with blank secret parameters.
- `arm_template.zip`: original local export, ignored by Git.

The exported PostgreSQL linked service uses Basic authentication. The ADLS linked service uses an account key, not ADF's managed identity. Both secrets are referenced through ARM `secureString` parameters; neither value is stored in the committed files. Supply those values securely at deployment time. A local `ARMTemplateParametersForFactory.json` is ignored by Git.

Terraform under `infra/terraform/` manages the factory resource itself. This template manages its child resources; the ZIP's separate factory template and duplicate linked templates are intentionally not included in the committed export. These files are a deployment snapshot, not an ADF Git-integration source folder. No deployment is performed by adding them to this repository.

## Export correction

The exported `ds_raw_table` contained a fixed cars schema even though it is reused for all eight tables. Its `schema` array is cleared in the committed template so the reusable dataset has no fixed column list. Apply the same change in ADF Studio's dataset Schema tab (or JSON editor: `"schema": []`) and publish it before the next export. This local correction has not been deployed to the live factory.

To refresh these files, publish ADF changes, export the ARM template, and review the full template and parameter file. Keep the secret values blank in the example file.
