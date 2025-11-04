-- Minimal roles for BI users
CREATE ROLE bizlens_ro NOLOGIN;
GRANT USAGE ON SCHEMA public TO bizlens_ro;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO bizlens_ro;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT ON TABLES TO bizlens_ro;

-- Email hashing update example
UPDATE dim_customer
SET email_hash = CASE WHEN email_hash IS NULL THEN digest(random()::text, 'sha256')::text ELSE email_hash END;
