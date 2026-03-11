-- Migration: Standardize seed IDs to start at 0
-- Run this against an existing galadriel.db BEFORE updating to the new version.
-- Back up your database first: cp galadriel.db galadriel.db.bak
--
-- This script shifts IDs down by 1 for three reference tables and updates
-- all foreign key references in data tables.
--
-- Strategy: update FK references first, then delete and reinsert reference
-- rows with new IDs to avoid UNIQUE constraint collisions.

-- ============================================================
-- 1. Cycle Child Types: 1-4 → 0-3
-- ============================================================

-- Update references in data tables
UPDATE cyclechildmodel SET child_type_id = child_type_id - 1 WHERE child_type_id >= 1;
UPDATE iterationsnapshotmodel SET child_type = child_type - 1 WHERE child_type >= 1;

-- Recreate the reference table rows
DELETE FROM cyclechildtypemodel;
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
DELETE FROM iterationsnapshotstatusmodel;
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
DELETE FROM suitechildtypemodel;
INSERT INTO suitechildtypemodel (id, type_name) VALUES (0, 'Scenario');
INSERT INTO suitechildtypemodel (id, type_name) VALUES (1, 'Case');
