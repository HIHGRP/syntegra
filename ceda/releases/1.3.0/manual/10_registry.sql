-- CEDA 1.3.0 expand script for the registry zone (hand-written; reviewed with the delta). Change request CR-002.
-- Both changes add NULLable columns (instant in MySQL 9.7) and one secondary index (online); nothing existing is
-- rewritten, so the script is safe on a live 1.2.0 database. Runs before the 1.3.0 delta of the same zone.
-- Existing NIN identifiers get their national token from the backfill job (clearance.federation.backfill_national_tokens).
SET NAMES utf8mb4;
ALTER TABLE `external_identifier`
  ADD COLUMN `value_national_hmac` BINARY(32) COMMENT 'National lookup token (federation key) — NIN only, for cross-state matching without exchanging the NIN (CR-002)' AFTER `value_last4`,
  ALGORITHM=INSTANT;
ALTER TABLE `external_identifier`
  ADD KEY `ix_external_identifier_scheme_value_national_hmac` (`tenant_id`, `scheme`, `value_national_hmac`), ALGORITHM=INPLACE, LOCK=NONE;
ALTER TABLE `clearance_check`
  ADD COLUMN `federation` JSON COMMENT 'National coverage: per state answered / not_on_network / unavailable, with match outcome' AFTER `pattern_flags`,
  ALGORITHM=INSTANT;
