#!/bin/bash
set -e

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    SELECT 'CREATE DATABASE tskhra_db' WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'tskhra_db')\gexec
    SELECT 'CREATE DATABASE products_db' WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'products_db')\gexec
    SELECT 'CREATE DATABASE cart_db' WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'cart_db')\gexec
    SELECT 'CREATE DATABASE payment_db' WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'payment_db')\gexec
EOSQL

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "tskhra_db" <<-'EOSQL'
    DO $$ BEGIN
        IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'gender') THEN
            CREATE TYPE gender AS ENUM ('MALE', 'FEMALE');
        END IF;
        IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'kyc_status') THEN
            CREATE TYPE kyc_status AS ENUM ('NONE', 'PENDING', 'APPROVED', 'REJECTED');
        END IF;
        IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'user_status') THEN
            CREATE TYPE user_status AS ENUM ('ACTIVE', 'SUSPENDED', 'BANNED', 'DELETED');
        END IF;
        IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'activity_status') THEN
            CREATE TYPE activity_status AS ENUM ('ACTIVE', 'INACTIVE', 'DELETED');
        END IF;
        IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'business_type') THEN
            CREATE TYPE business_type AS ENUM ('INDIVIDUAL', 'COMMERCIAL');
        END IF;
        IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'week_day') THEN
            CREATE TYPE week_day AS ENUM ('MON', 'TUE', 'WED', 'THU', 'FRI', 'SAT', 'SUN');
        END IF;
        IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'call_type') THEN
            CREATE TYPE call_type AS ENUM ('OUTCALL', 'ONSITE', 'BOTH');
        END IF;
        IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'booking_status') THEN
            CREATE TYPE booking_status AS ENUM ('AWAITING', 'SCHEDULED', 'REJECTED', 'CANCELLED_BY_BUSINESS', 'CANCELLED_BY_USER', 'COMPLETED');
        END IF;
        IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'chain_status') THEN
            CREATE TYPE chain_status AS ENUM ('PROPOSED', 'ACTIVE', 'COMPLETED', 'BROKEN', 'EXPIRED');
        END IF;
        IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'item_condition') THEN
            CREATE TYPE item_condition AS ENUM ('NEW', 'LIKE_NEW', 'USED', 'DAMAGED');
        END IF;
        IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'item_status') THEN
            CREATE TYPE item_status AS ENUM ('AVAILABLE', 'HIDDEN', 'IN_TRADE', 'TRADED', 'REMOVED');
        END IF;
        IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'owning_side') THEN
            CREATE TYPE owning_side AS ENUM ('OFFERER', 'RESPONDER');
        END IF;
        IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'trade_range') THEN
            CREATE TYPE trade_range AS ENUM ('CITY_WIDE', 'COUNTRY_WIDE');
        END IF;
        IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'trade_status') THEN
            CREATE TYPE trade_status AS ENUM ('PENDING', 'ACCEPTED', 'REJECTED', 'CANCELED', 'COUNTERED', 'EXPIRED', 'COMPLETED', 'WITHDRAWN');
        END IF;
        IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'attribute_data_type') THEN
            CREATE TYPE attribute_data_type AS ENUM ('STRING', 'NUMBER', 'BOOLEAN', 'ENUM');
        END IF;
    END $$;
EOSQL