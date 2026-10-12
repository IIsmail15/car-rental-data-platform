# Databricks job orchestration

The live job `job_carrental_curated_warehouse` (job ID `82774375581532`) runs curation and dbt after ADF finishes copying the eight source tables. ADF invokes it through activity `run_databricks_workflow`, which depends on `ForEach1` succeeding. The refreshed [ADF ARM template](../adf/ARMTemplateForFactory.json) confirms the job ID and managed-identity linked service `AzureDatabricks1`.

## Tasks

| Setting | `raw_to_curated` | `dbt_build` |
| --- | --- | --- |
| Type | Notebook | dbt |
| Work | `02_all_tables_raw_to_curated` | `dbt build` |
| Source | Workspace notebook | Git `main`, project directory `car_rental_dbt` |
| Dependency | First task in the job | `raw_to_curated`, all succeeded |
| CLI/notebook compute | Serverless | Serverless |
| Task timeout | 600 seconds (10 minutes) | 600 seconds (10 minutes) |
| Automatic optimization | Disabled | Disabled |

The notebook path used during setup was `/Workspace/Users/israa.ismail@studio.unibo.it/02_all_tables_raw_to_curated`. The repository copy is [02_all_tables_raw_to_curated.ipynb](../notebooks/02_all_tables_raw_to_curated.ipynb). Workspace notebook changes and repository exports must be kept in sync.

The dbt project builds into `dbw_carrental_dev_7405614156846449.analytics` from the catalog's `curated` schema. The saved task selects SQL warehouse `3a42db489d006de3`. Its `dbt_build_environment` uses environment version `6`, `dbt-core==1.12.4`, and `dbt-databricks==1.12.6`, matching [requirements-databricks.txt](../requirements-databricks.txt).

The [job YAML](job_carrental_curated_warehouse.yml) preserves the configuration supplied from Databricks on 2026-10-09. The dbt task checks out `main` from `https://github.com/IIsmail15/car-rental-data-platform.git`; the notebook remains sourced from the workspace. Queueing is enabled and the performance target is `PERFORMANCE_OPTIMIZED`.

Both tasks specify a minimum retry interval of 900,000 milliseconds (15 minutes), but neither explicitly specifies `max_retries`. The interval alone does not establish the retry count. The export also omits `run_as` and an explicit maximum concurrent run count; check these in the live job if needed. The additional `Default` and `dbt-default` environment definitions are preserved as exported; `dbt_build` explicitly selects the pinned `dbt_build_environment`.

## Verified run

On 2026-10-09, the shared ADF run showed successful ingestion and Databricks activity execution. The latest shared Databricks job run, `1083083368650268`, succeeded in 3 minutes 1 second; both tasks were green. Its dbt output reported:

```text
Finished running 13 table models, 12 data tests in 0 hours 0 minutes and 14.96 seconds (14.96s).
Completed successfully
Done. PASS=25 WARN=0 ERROR=0 SKIP=0 NO-OP=0 REUSED=0 TOTAL=25
```

The end-to-end workflow was triggered manually. A scheduled demonstration is planned, with no successful scheduled-run evidence recorded yet. Schedule the complete workflow in ADF rather than independently scheduling the Databricks job.

## Saved job definition and updates

The saved [job_carrental_curated_warehouse.yml](job_carrental_curated_warehouse.yml) contains both tasks, their dependency, Git source, warehouse target, environments, and execution settings. To refresh it, open the job's menu beside **Run now**, choose **Switch to code version (YAML)**, and replace the file with the reviewed export. Do not substitute a run ID for the job ID used by ADF.

This is a job resource definition under `resources.jobs`, not a complete deployment bundle: no root `databricks.yml` or deployment target is included. Saving it does not deploy or update the live job. Its workspace notebook, SQL warehouse, catalog, Git credentials, and permissions must exist in the target environment. The ADF template references the existing job ID separately; the YAML does not bind a deployment to that existing ID. The Run as principal and permission assignments are not included in this export.

The saved tasks each have a ten-minute timeout; the ADF job activity separately retains its exported twelve-hour timeout. Before another run, verify retry settings and SQL warehouse auto-stop. After a demonstration, disable unneeded triggers and stop unused compute. PostgreSQL must be running before ADF's copy activities begin.
