-- CEDA 1.9.0 expand script for the records zone (hand-written; reviewed with the delta). Change request CR-008.
-- Adds NULLable columns (instant) recording where each master is held and how it is locked; existing documents keep
-- NULLs (held on the filesystem store before 1.9.0). Runs before the 1.9.0 delta of the same zone, which creates
-- document_rendition and document_release.
SET NAMES utf8mb4;
ALTER TABLE `document`
  ADD COLUMN `master_store` VARCHAR(20) CHARACTER SET ascii COLLATE ascii_bin COMMENT 'Where the master is held: s3 (object storage) or fs (development only) (CR-008)' AFTER `master_object_key`,
  ADD COLUMN `master_lock_mode` VARCHAR(32) CHARACTER SET ascii COLLATE ascii_bin COMMENT 'Object lock on the master: compliance in production (CR-008)' AFTER `master_store`,
  ADD COLUMN `master_retain_until` DATE COMMENT 'The master cannot be changed or deleted before this date (CR-008)' AFTER `master_lock_mode`,
  ALGORITHM=INSTANT;
ALTER TABLE `document`
  ADD CONSTRAINT `ck_document__master_lock_mode` CHECK (`master_lock_mode` IS NULL OR `master_lock_mode` IN ('none', 'governance', 'compliance'));
