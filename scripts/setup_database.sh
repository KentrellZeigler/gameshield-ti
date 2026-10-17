
#!/usr/bin/env bash

set -euo pipefail

DB_NAME="${1:-gameshield_ti}"

# Accept only simple PostgreSQL database names.
if [[ ! "$DB_NAME" =~ ^[a-z][a-z0-9_]*$ ]]; then
    echo "Invalid database name."
    exit 1
fi

# Restrict this development script to our project databases.
if [[ "$DB_NAME" != "gameshield_ti" &&
      "$DB_NAME" != "gameshield_ti_test" ]]; then
    echo "Refusing to modify an unexpected database."
    exit 1
fi

cd "$(dirname "$0")/.."

echo "Setting up database: $DB_NAME"

if ! psql -d "$DB_NAME" -Atqc \
    "SELECT 1" >/dev/null 2>&1; then
    echo "Database unavailable."
    echo "Create it first with: createdb $DB_NAME"
    exit 1
fi

SQL_FILES=(
    "src/database/schema.sql"
    "src/database/migration_001_auto_cases.sql"
    "src/database/migration_002_case_evidence.sql"
    "src/database/migration_003_case_notes.sql"
    "src/database/migration_004_audit_log.sql"
)

for file in "${SQL_FILES[@]}"; do
    echo "Applying $file"

    psql \
        -v ON_ERROR_STOP=1 \
        -d "$DB_NAME" \
        -f "$file"
done

echo "Database setup completed."
