# Azure Data Factory ingestion and orchestration

## Live automation and export status

The live `pl_all_tables_to_raw` pipeline now runs `run_databricks_workflow` after `ForEach1` succeeds. That activity invokes `job_carrental_curated_warehouse`, whose `raw_to_curated` task is followed by `dbt_build`. The manually triggered end-to-end workflow passed on 2026-10-09; dbt reported 13 successful models and 12 passing tests. See the [Databricks task notes](../databricks/README.md).

The ARM files were refreshed from `arm_template (1).zip`, exported on 2026-10-09. They include the Databricks linked service, job activity, and published schedule trigger. Successful scheduled execution has not yet been verified.

## Saved snapshot

The ARM template contains ten child resources for `adf-carrental-dev`: three linked services, four datasets, two pipelines, and one trigger.

| Pipeline | Behaviour |
| --- | --- |
| `pl_cars_to_raw` | Copies `staging.cars` to `raw/cars/CARS.parquet`. |
| `pl_all_tables_to_raw` | Sequentially copies eight tables to `raw/<table>/<TABLE>.parquet`, then invokes the Databricks job after the ForEach succeeds. |

The table list is `rental_offices`, `cars`, `have_optional`, `drivers`, `rentals`, `drive`, `insurances`, and `payments`. Both pipelines write Parquet with Snappy compression. The reusable datasets pass `table_name` from the ForEach `@item()` expression.

## Databricks activity

`run_databricks_workflow` is a `DatabricksJob` activity with a `Succeeded` dependency on `ForEach1`. Its `AzureDatabricks1` linked service uses managed identity (`authentication: MSI`) against `dbw-carrental-dev`. The workspace URL and Azure resource ID are ARM parameters. The `databricksJobId` parameter defaults to the exported job ID `82774375581532`; this is distinct from individual run IDs.

The job must already exist in Databricks, and the ADF identity must retain the access used by the working pipeline. This ARM template does not create the job, assign identity permissions, or configure its Run as principal. The exported activity has zero retries and a 12-hour timeout; those values are preserved rather than represented as the shorter limits discussed during setup. Review the live timeout before further unattended runs.

## Exported schedule

Despite its name, `trg_carrental_weekly` has a **daily** recurrence (`Day`, interval `1`) at **16:55**, using `GMT Standard Time`, which observes UK daylight saving. The exported window is 2026-10-09 00:00 through 2026-10-15 08:00 in that time zone. It targets `pl_all_tables_to_raw`.

The live export recorded `runtimeState: Started`. The repository template records `Stopped` so the snapshot does not describe an active demonstration schedule. This local change does not stop the live trigger; stop it in ADF when further runs are not intended. Review the dates and recurrence before reusing this historical schedule, and explicitly manage trigger state during deployment.

## Files and credentials

- `ARMTemplateForFactory.json`: pipeline, dataset, and linked-service definitions.
- `ARMTemplateParametersForFactory.example.json`: environment values with blank secret parameters.
- `arm_template (1).zip`: updated local export, ignored by Git; `arm_template.zip` is the older ingestion-only export.

The PostgreSQL linked service uses Basic authentication. The ADLS linked service uses an account key. Both secrets are referenced through ARM `secureString` parameters; neither value is stored in the committed files. Supply those values securely at deployment time. The Databricks linked service uses managed identity and has no embedded token. A local `ARMTemplateParametersForFactory.json` is ignored by Git.

Terraform under `infra/terraform/` manages the factory resource itself. This template manages its child resources; the ZIP's separate factory template and duplicate linked templates are intentionally not included in the committed export. These files are a deployment snapshot, not an ADF Git-integration source folder. No deployment is performed by adding them to this repository.

## Export correction

The new export still contains a fixed cars schema in `ds_raw_table`, even though it is reused for all eight tables. Its `schema` array remains cleared in the repository template so the reusable dataset has no fixed column list. Apply the same change in ADF Studio's dataset Schema tab (or JSON editor: `"schema": []`) and publish before the next export. This local correction has not been deployed to the live factory.

Other deliberate differences from the export are the stopped trigger snapshot and parameters for the Databricks workspace URL, workspace resource ID, and job ID. Resource order is retained where possible to keep diffs readable.

To refresh these files, publish ADF changes, export the ARM template, and review the full template and parameter file. Keep the secret values blank in the example file.
