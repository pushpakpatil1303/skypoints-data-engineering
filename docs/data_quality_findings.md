
# SkyPoints - Data Quality Findings

# Source Files
- AUS.xlsx: 3 records
- IND.xlsx: 3 records
- USA.xlsx: 3 records

# Identified Issues

### 1. Inconsistent Column Names
The three source files use different column names for the same business attributes.
Solution: Standardize columns during ingestion.

### 2. Invalid Dates
AUS.xlsx contains an invalid enrollment date: 2021-13-13.
Solution: Validate dates and quarantine invalid records.

### 3. Missing Values
AUS.xlsx contains a missing date of birth.
USA.xlsx does not provide a DOB column.
Solution: Preserve missing optional values as NULL. Do not calculate AGE when DOB is unavailable.

### 4. Different Date Formats
AUS and IND contain ISO-style dates.USA contains dates in variable-length MMDDYYYY format.
Solution: Apply source-specific date parsing rules.

### 5. Duplicate Member IDs
Member IDs 1, 2 and 3 occur in all three country files.
Solution: Do not assume these are global identifiers. Use a country-qualified source key until an authoritative global member identifier is available.

### 6. Country Movement
The assessment requires latest-record-wins processing.
Solution: Use an authoritative global member ID and a reliable source update timestamp to identify the latest country assignment.

The sample files do not provide enough information
to reliably demonstrate actual member movement.

## Design Decision
Preserve original source records in the RAW layer. Perform standardization and validation before loading records into STAGING and TARGET tables.