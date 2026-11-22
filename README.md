# SkyPoints — Data Engineering Assessment

## 1. Project Overview

This project implements a data engineering pipeline for the SkyPoints airline loyalty program using Python and Snowflake.

The pipeline processes member profiles from Excel files and a pipe-delimited flat file, performs data cleaning and transformations, calculates derived fields, and routes members into country-specific tables.

It also processes nested JSON redemption transactions and supports latest-record-wins synchronization when a globally identified member moves between countries.

The project is developed as part of the Incubyte Data Engineer Technical Assessment.

## 2. Technologies Used

- Python 3.10
- Snowflake
- Pandas
- OpenPyXL
- Snowflake Python Connector
- Pytest
- Git and GitHub

## 3. Pipeline Architecture

**Member processing:**

Excel Files / Pipe-Delimited Flat File → Python Validation and Ingestion → Snowflake RAW → STAGING → Country-Specific TARGET Tables

**Redemption processing:**

Partner JSON Feed → Snowflake RAW → JSON Flattening → STAGING → TARGET

**Country movement:**

Member Change Events → Latest Event Selection → Transactional Country Synchronization

The Snowflake database is `SKYPOINTS_DB`, containing three schemas:

- `RAW` — Source data ingestion
- `STAGING` — Cleaned and transformed data
- `TARGET` — Country-specific member records and redemption transactions

## 4. Project Structure

```text
skypoints-data-engineering/
├── data/
│   └── sample/
│       ├── IND.xlsx
│       ├── USA.xlsx
│       ├── AUS.xlsx
│       ├── members_sample.txt
│       └── partner_redemptions.json
├── src/
│   ├── inspect_data.py
│   ├── ingestion.py
│   ├── load_raw_data.py
│   ├── parse_flat_file.py
│   ├── load_flat_file.py
│   └── snowflake_connection.py
├── sql/
│   ├── 01_create_tables.sql
│   ├── 02_member_staging.sql
│   ├── 03_country_routing.sql
│   ├── 04_redemption_processing.sql
│   ├── 05_data_validation.sql
│   ├── 06_member_country_sync.sql
│   ├── 07_flat_file_staging.sql
│   └── 08_load_redemption_json.sql
├── tests/
│   └── test_member_transformations.py
├── docs/
│   └── data_quality_findings.md
├── requirements.txt
└── README.md
```

## 5. Source Data

### Excel Member Profiles

Three Excel files contain nine original member records:

- India — 3 members
- USA — 3 members
- Australia — 3 members

### Assessment Flat File

The pipe-delimited file `members_sample.txt` contains five member records.

| Member | Member ID | Country |
|---|---|---|
| Elena | 223457 | USA |
| Ravi | 223458 | IND |
| Mateo | 223459 | PHIL |
| Nora | 22345 | CAN |
| Jacob | 2256 | AU |

The Python parser identifies header (`H`) and data (`D`) records, validates field counts, checks mandatory values, and validates date formats before ingestion.

The combined RAW and STAGING member dataset contains **14 records**.

### Partner Redemption JSON

The assessment JSON contains two redemption transactions for Elena (`MEMBER_ID = 223457`):

| Transaction | Partner | Miles | Status |
|---|---|---:|---|
| RX10091 | AeroLink | 12000 | COMPLETED |
| RX10092 | SkyPoints | 5000 | PENDING |

## 6. Member Transformations

The member transformation pipeline:

- Standardizes dates from Excel and flat-file formats.
- Calculates `AGE` from date of birth.
- Calculates `STALE_MEMBER` when the last flight occurred more than 90 days ago.
- Handles missing or invalid dates using Snowflake `TRY_TO_DATE`.
- Routes members into country-specific TARGET tables.
- Uses deduplication and `MERGE` logic for repeatable country routing.

The assessment's five members have a date of birth of March 5, 1985, giving an age of 41 as of November 22, 2026.

Their last flight was October 13, 2012, so all five have `STALE_MEMBER = TRUE`.

## 7. Country-Specific Routing

The pipeline supports five country tables:

| Country | Snowflake Target |
|---|---|
| India | `TARGET.TABLE_INDIA` |
| USA | `TARGET.TABLE_USA` |
| Australia | `TARGET.TABLE_AUSTRALIA` |
| Philippines | `TARGET.TABLE_PHILIPPINES` |
| Canada | `TARGET.TABLE_CANADA` |

Both `AU` and `AUS` are accepted as Australian country codes.

The country-routing process uses `MERGE` statements to insert or update member records without replacing entire country tables.

### Latest Record Wins

Country-change events are stored in `RAW.MEMBER_CHANGE_EVENTS`.

The view `STAGING.LATEST_MEMBER_CHANGES` selects the latest event for each `GLOBAL_MEMBER_ID` using source update timestamps.

The `06_member_country_sync.sql` script:

1. Identifies each globally identified member's latest country.
2. Removes outdated country assignments.
3. Inserts or updates the member in the latest country table.
4. Validates that the global member appears in only one country table.

**Verified example:**

`GLOBAL_1001`, representing Test Member (`MEMBER_ID = 101`), exists only in the USA target table after synchronization.

This demonstration record is separate from the 14 original source members.

## 8. JSON Redemption Processing

The partner airline provides nested JSON redemption transactions.

Snowflake `LATERAL FLATTEN` converts the nested `redemptions` array into individual transaction records.

The transformation:

- Extracts member and transaction identifiers.
- Converts feed and transaction dates.
- Extracts partner, redeemed miles, and status.
- Deduplicates transaction IDs.
- Loads the processed transactions into the TARGET table.

The assessment JSON was verified to produce two transactions, both successfully linked to Elena through `MEMBER_ID`.

## 9. Data Quality Validation

The SQL validation script checks:

- Missing mandatory member fields
- Duplicate member IDs within each country
- Missing or invalid dates
- Invalid AGE and STALE_MEMBER values
- Incorrect country assignments
- Members missing from country targets
- Missing redemption transaction identifiers
- Duplicate transaction IDs
- Invalid redeemed miles
- Redemption transactions without matching members

The assessment member records and both redemption transactions were verified successfully.

The original Excel data includes an invalid Australian enrollment date, which is converted to NULL and retained as a documented data-quality finding.

## 10. Automated Testing

The project uses Pytest to verify:

- Age calculation around birthday boundaries
- Stale-member detection, including the 90-day threshold
- Latest-country selection based on source update timestamps

The previously verified test result was:

**9 passed, 0 failed**

Run tests using:

```powershell
python -m pytest tests/ -v
```

These tests validate Python transformation rules. They do not replace full Snowflake integration testing.

## 11. Local Setup and Execution

### Install dependencies

Create and activate a Python virtual environment, then run:

```powershell
python -m pip install -r requirements.txt
```

### Configure Snowflake

Create a local `.env` file containing the Snowflake connection settings expected by `src/snowflake_connection.py`.

Do not commit `.env` or credentials to GitHub.

### Execute the pipeline

1. Run `sql/01_create_tables.sql` to create the database objects.
2. Run `python src/load_raw_data.py` to load the Excel sample records.
3. Run `python src/load_flat_file.py` to validate and load the assessment flat file.
4. Run `sql/08_load_redemption_json.sql` to load the assessment JSON sample.
5. Run `sql/02_member_staging.sql` to transform all RAW member records.
6. Run `sql/03_country_routing.sql` to route members to the five country tables and create the latest-change view.
7. Run `sql/04_redemption_processing.sql` to flatten and load redemption transactions.
8. Run `sql/06_member_country_sync.sql` to synchronize global member country changes.
9. Run `sql/05_data_validation.sql` to validate the results.
10. Run `python -m pytest tests/ -v` to execute unit tests.

`07_flat_file_staging.sql` is an optional flat-file-only staging reload script and is not required after a full execution of `02_member_staging.sql`.

## 12. Scalability Design for Billions of Daily Records

The current implementation demonstrates the required functionality using small sample datasets.

For a production environment processing billions of records daily, the architecture would require the following improvements.

### Bulk ingestion

Use Snowflake external or internal stages and `COPY INTO` for large-scale file ingestion instead of Python row-by-row inserts.

### Incremental processing

Use Snowflake Streams and Tasks, or an equivalent orchestration framework, to process only newly arrived or changed records.

### Efficient deduplication

Apply window functions and `MERGE` operations to incremental datasets rather than repeatedly scanning and rebuilding all records.

### Country routing

Maintain a globally unique member identifier and authoritative source update timestamp to support deterministic latest-record-wins processing across countries.

### Storage and query optimization

Use Snowflake's columnar storage, warehouse sizing, workload separation, and selective clustering where query patterns justify the cost.

### Monitoring and reliability

Implement automated data-quality checks, failed-record quarantine, pipeline monitoring, retry mechanisms, and audit logging.

### Idempotency

Track file identifiers, ingestion batches, and transaction IDs to prevent duplicate processing during retries.

These are proposed production improvements; they are not all implemented in the sample pipeline.

## 13. Assumptions and Limitations

### Member identity

The Excel sample files reuse member IDs across countries.

Therefore, `MEMBER_ID` alone cannot reliably identify every member globally.

The country-change demonstration uses `GLOBAL_MEMBER_ID` as the stable identity.

### Country movement

Latest-country synchronization is implemented for members represented in the member-change event feed.

The original Excel and assessment flat-file records do not all contain authoritative global identifiers or source update timestamps.

### Redemption joins

The sample redemption transactions are joined to member profiles using `MEMBER_ID`.

For production use, a globally unique identifier or a reliable country-qualified member key is required.

### Full-refresh transformations

The member staging and redemption transformations use full-refresh operations for demonstration purposes.

Production-scale processing should use incremental ingestion and change tracking.

### Data quality

Invalid or missing source dates may produce NULL transformed dates.

These cases are reported by validation queries rather than automatically corrected.

## 14. Conclusion

The SkyPoints project demonstrates an end-to-end data engineering pipeline using Python and Snowflake.

It includes structured and semi-structured data ingestion, member transformations, country-specific routing, latest-record-wins synchronization, JSON flattening, data-quality validation, and automated unit testing.

The assessment sample has been processed and verified using 14 member records and two JSON redemption transactions.

The implementation provides a functional demonstration of the required data engineering concepts, with a documented approach for scaling to production workloads.