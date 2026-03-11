-- Migration: Standardize seed IDs to start at 0
-- Run this against an existing galadriel.db BEFORE updating to the new version.
-- Back up your database first: cp galadriel.db galadriel.db.bak
--
-- This script shifts IDs down by 1 for three reference tables and updates
-- all foreign key references in data tables.
--
-- Strategy: disable FK checks, update FK references first, then delete and
-- reinsert reference rows with new IDs. Everything runs in a single
-- transaction for atomicity.
--
-- Idempotency: a guard checks that the DB is still in the original 1-based
-- state. If it has already been migrated the transaction is rolled back.

PRAGMA foreign_keys = OFF;

BEGIN;

-- ============================================================
-- Rerun guard: abort if IDs are already 0-based.
-- The original seed has cyclechildtypemodel starting at id=1 (Suite).
-- After migration it starts at id=0. If id=0 already exists with
-- type_name='Suite', the migration was already applied.
-- ============================================================
-- Create a temporary table to hold the guard result.
CREATE TEMP TABLE _migration_guard (already_migrated INTEGER);
INSERT INTO _migration_guard (already_migrated)
    SELECT COUNT(*) FROM cyclechildtypemodel WHERE id = 0 AND type_name = 'Suite';

-- If already migrated, roll back and stop.
-- SQLite doesn't support conditional logic in scripts, so we use a
-- constraint violation to abort: inserting into a CHECK-constrained
-- table will fail and trigger a rollback.
CREATE TEMP TABLE _migration_check (
    val INTEGER CHECK (val = 0)
);
INSERT INTO _migration_check (val)
    SELECT already_migrated FROM _migration_guard;

DROP TABLE _migration_guard;
DROP TABLE _migration_check;

-- ============================================================
-- 1. Cycle Child Types: 1-4 → 0-3
-- ============================================================

-- Update references in data tables
UPDATE cyclechildmodel SET child_type_id = child_type_id - 1 WHERE child_type_id >= 1;
UPDATE iterationsnapshotmodel SET child_type = child_type - 1 WHERE child_type >= 1;

-- Recreate the reference table rows
DELETE FROM cyclechildtypemodel WHERE id >= 0;
INSERT INTO cyclechildtypemodel (id, type_name) VALUES (0, 'Suite');
INSERT INTO cyclechildtypemodel (id, type_name) VALUES (1, 'Scenario');
INSERT INTO cyclechildtypemodel (id, type_name) VALUES (2, 'Case');
INSERT INTO cyclechildtypemodel (id, type_name) VALUES (3, 'Step');

-- ============================================================
-- 2. Iteration Snapshot Statuses: 1-5 → 0-4
-- ============================================================

-- Update references in data tables
UPDATE iterationsnapshotmodel SET child_status_id = child_status_id - 1 WHERE child_status_id >= 1;

-- Recreate the reference table rows
DELETE FROM iterationsnapshotstatusmodel WHERE id >= 0;
INSERT INTO iterationsnapshotstatusmodel (id, status_name) VALUES (0, 'to do');
INSERT INTO iterationsnapshotstatusmodel (id, status_name) VALUES (1, 'failed');
INSERT INTO iterationsnapshotstatusmodel (id, status_name) VALUES (2, 'pass');
INSERT INTO iterationsnapshotstatusmodel (id, status_name) VALUES (3, 'skipped');
INSERT INTO iterationsnapshotstatusmodel (id, status_name) VALUES (4, 'blocked');

-- ============================================================
-- 3. Suite Child Types: 1-2 → 0-1
-- ============================================================

-- Update references in data tables
UPDATE suitechildmodel SET child_type_id = child_type_id - 1 WHERE child_type_id >= 1;

-- Recreate the reference table rows
DELETE FROM suitechildtypemodel WHERE id >= 0;
INSERT INTO suitechildtypemodel (id, type_name) VALUES (0, 'Scenario');
INSERT INTO suitechildtypemodel (id, type_name) VALUES (1, 'Case');

COMMIT;

PRAGMA foreign_keys = ON;
