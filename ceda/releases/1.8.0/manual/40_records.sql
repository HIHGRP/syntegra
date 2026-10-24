-- CEDA 1.8.0 expand script for the records zone (hand-written; reviewed with the delta). Change request CR-007.
-- Adds NULLable columns (instant) and two keys on document; existing documents keep a NULL reference_no, which the
-- unique key allows. Runs before the 1.8.0 delta of the same zone, which creates document_index.
SET NAMES utf8mb4;
ALTER TABLE `document`
  ADD COLUMN `reference_no` VARCHAR(64) CHARACTER SET ascii COLLATE ascii_bin COMMENT 'Reference number, unique in the state: <institution code>/<category>/<year>/<sequence> (CR-007)' AFTER `category_id`,
  ADD COLUMN `description` VARCHAR(2000) COLLATE utf8mb4_0900_ai_ci COMMENT 'What the document is and what it contains' AFTER `title`,
  ADD COLUMN `source_reference` VARCHAR(200) COLLATE utf8mb4_0900_ai_ci COMMENT 'Reference, file or box number written on the paper original' AFTER `description`,
  ALGORITHM=INSTANT;
ALTER TABLE `document`
  ADD UNIQUE KEY `uq_document_reference_no` (`tenant_id`, `reference_no`),
  ADD KEY `ix_document_institution_id_category_id` (`tenant_id`, `institution_id`, `category_id`);
