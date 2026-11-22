# SkyPoints — Data Engineering Assessment

## 1. Project Overview

This project implements a sample data engineering pipeline for the SkyPoints airline loyalty program using Python and Snowflake.

The pipeline processes member profiles from three countries (India, USA, and Australia), standardizes member information, calculates derived fields, routes records into country-specific tables, and processes nested JSON redemption transactions.

## 2. Technologies Used

- Python 3.10
- Snowflake
- Pandas
- OpenPyXL
- Snowflake Python Connector
- Pytest
- Git

## 3. Pipeline Architecture

**Excel Files → Python Ingestion → Snowflake RAW → STAGING → Country-Specific TARGET Tables**

Redemption processing follows a separate pipeline:

**JSON → Snowflake RAW → JSON Flattening → STAGING → TARGET**

The Snowflake database is `SKYPOINTS_DB`, with three schemas: `RAW`, `STAGING`, and `TARGET`.

## 4. Project Structure

- `data/sample/` — Sample Excel files for India, Australia, and USA
- `src/` — Python ingestion, data inspection, and Snowflake connection scripts
- `sql/01_create_tables.sql` — Database schemas and table definitions
- `sql/02_member_staging.sql` — Data standardization and derived columns
- `sql/03_country_routing.sql` — Country routing and latest-change event selection
- `sql/04_redemption_processing.sql` — JSON flattening and transaction loading
- `sql/05_data_validation.sql` — Data quality checks
- `sql/06_member_country_sync.sql` — Synchronizes members to their latest country using transactional DELETE and MERGE operations.
- `tests/test_member_transformations.py` — Automated unit tests
- `docs/data_quality_findings.md` — Data quality findings
- `requirements.txt` — Python dependencies

## 5. Data Transformations

The member pipeline performs the following transformations:

- Standardizes dates from different country-specific source formats.
- Calculates `AGE` from date of birth.
- Calculates `STALE_MEMBER` when the last flight occurred more than 90 days ago.
- Selects the latest ingested member record within each country.
- Routes records to their corresponding country TARGET tables.

The redemption pipeline flattens nested transaction arrays into individual records, standardizes dates, and deduplicates transaction IDs.

## 6. Data Quality Results

The sample contains nine member records: three each from India, Australia, and USA.

Validation results:

- No missing member IDs or names.
- No missing country values.
- No duplicate `(COUNTRY, MEMBER_ID)` combinations.
- One invalid enrollment date in the Australian source data, converted to NULL.
- Two redemption transactions processed successfully.
- No invalid transaction IDs, transaction dates, or redeemed miles in the processed sample.
- No incorrect country assignments detected in the TARGET tables.

## 7. Automated Testing

The project uses Pytest to verify:

- Age calculation before, on, and after birthdays.
- Stale-member detection, including the 90-day boundary.
- Latest-country selection based on source update timestamps.

**Test result: 9 passed, 0 failed.**

These are Python unit tests of transformation rules, not full Snowflake integration tests.

Run tests using:

```powershell
python -m pytest tests/ -v
```

## 8. Local Setup

1. Create and activate a Python virtual environment.
2. Install dependencies:

```powershell
python -m pip install -r requirements.txt
```

3. Configure Snowflake connection credentials in a local `.env` file.
4. Execute `sql/01_create_tables.sql` in Snowflake.
5. Run the Python ingestion script:

```powershell
python src/load_raw_data.py
```

6. Execute the remaining SQL scripts in this order:

   - `sql/02_member_staging.sql`
   - `sql/03_country_routing.sql`
   - `sql/04_redemption_processing.sql`
   - `sql/06_member_country_sync.sql`
   - `sql/05_data_validation.sql`

7. Run automated tests:

   `python -m pytest tests/ -v`

## 9. Assumptions and Limitations

### Member Identity and Country Changes

The pipeline supports country-change synchronization for members with a stable `GLOBAL_MEMBER_ID`.

Member-change events are stored in `RAW.MEMBER_CHANGE_EVENTS`. The `STAGING.LATEST_MEMBER_CHANGES` view selects the latest event for each global member using source update timestamps.

The `sql/06_member_country_sync.sql` script uses transactional DELETE and MERGE operations to remove outdated country assignments and insert or update members in their latest country TARGET table.

**Validation results:**
- No duplicate global member IDs across country TARGET tables.
- No missing or incorrectly assigned members compared with the latest member-change events.
- Successfully tested a synthetic member moving from India to the USA.

**Limitation:** The original Excel files do not contain stable global member identifiers or authoritative source update timestamps. Therefore, automatic cross-country movement detection is supported for the separate change-event feed, but not for the original Excel records.

### Redemption-to-member joining

Redemption transactions currently contain `MEMBER_ID` without a country or global identifier. Joining on this field alone can produce ambiguous matches because member IDs repeat across countries.

A reliable join requires a global member identifier or a country-qualified member key.

### Scalability

The current implementation demonstrates transformations on small sample datasets. For production-scale workloads, improvements would include staged bulk ingestion, incremental processing, change-data capture, Snowflake `MERGE` operations, orchestration, and automated monitoring.

## 10. Conclusion

The project demonstrates Excel ingestion, Snowflake data transformations, country-specific routing, JSON flattening, data validation, and automated unit testing.

The sample-data processing and tests have been verified. Full automated cross-country member movement and production-scale incremental processing remain future enhancements.
