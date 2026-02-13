#!/bin/bash
# Initialize and seed the visa interview database
set -e

echo "=== VisaWire Local: Database Seeder ==="

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOCAL_DIR="$(dirname "$SCRIPT_DIR")"

cd "$LOCAL_DIR"

# Option 1: SQLite (default for local dev)
echo "--- Initializing SQLite database ---"
python3 -c "
import sys
sys.path.insert(0, '.')
from services.visa_db.retrieval import init_db, seed_db, get_destinations, get_questions_by_country

print('Creating schema...')
init_db()

print('Loading seed data...')
seed_db()

# Verify
dests = get_destinations()
print(f'Loaded {len(dests)} destinations')

for code in ['US', 'UK', 'CA']:
    qs = get_questions_by_country(code)
    print(f'  {code}: {len(qs)} questions')

print('Database seeded successfully.')
"

# Option 2: PostgreSQL (if running via Docker)
if command -v psql &> /dev/null; then
    PGHOST="${POSTGRES_HOST:-localhost}"
    PGPORT="${POSTGRES_PORT:-5432}"
    PGDB="${POSTGRES_DB:-visawire}"
    PGUSER="${POSTGRES_USER:-visawire}"

    echo ""
    echo "--- Checking PostgreSQL connection ---"
    if pg_isready -h "$PGHOST" -p "$PGPORT" -U "$PGUSER" 2>/dev/null; then
        echo "PostgreSQL is running. Seeding..."
        PGPASSWORD="${POSTGRES_PASSWORD:-visawire_local}" psql -h "$PGHOST" -p "$PGPORT" -U "$PGUSER" -d "$PGDB" \
            -f services/visa_db/schema.sql \
            -f services/visa_db/seed/destinations.sql \
            -f services/visa_db/seed/questions.sql \
            -f services/visa_db/seed/followups.sql \
            -f services/visa_db/seed/risk_factors.sql
        echo "PostgreSQL seeded."
    else
        echo "PostgreSQL not running. Skipping."
    fi
fi

echo ""
echo "=== Database seeding complete ==="
