-- Optional: use a dedicated schema
CREATE SCHEMA IF NOT EXISTS public;
SET search_path TO public;
CREATE EXTENSION IF NOT EXISTS pgcrypto; -- for hashing PII
