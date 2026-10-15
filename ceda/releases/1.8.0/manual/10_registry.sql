-- CEDA 1.8.0 expand script for the registry zone (hand-written; reviewed with the delta). Change request CR-007.
-- Adds NULLable columns only (instant in MySQL 9.7) and refreshes one column comment; nothing existing is rewritten,
-- so the script is safe on a live 1.7.0 database.
SET NAMES utf8mb4;
ALTER TABLE `scope_node`
  ADD COLUMN `address` JSON COMMENT 'Office address of a ministry, board, agency or LGA office (street, town, LGA, state); institutions keep theirs on institution (CR-007)' AFTER `ownership`,
  ALGORITHM=INSTANT;
ALTER TABLE `user_session`
  ADD COLUMN `ended_reason` VARCHAR(32) CHARACTER SET ascii COLLATE ascii_bin COMMENT 'Why the session ended (CR-007)' AFTER `revoked_at`,
  ADD COLUMN `affiliation_scope_id` BINARY(16) COMMENT 'Scope node of the school or office the user signed in for (soft; CR-007)' AFTER `ended_reason`,
  ADD COLUMN `affiliation_name` VARCHAR(300) COLLATE utf8mb4_0900_ai_ci COMMENT 'School or office name as shown at sign-in' AFTER `affiliation_scope_id`,
  ADD COLUMN `affiliation_address` VARCHAR(500) COLLATE utf8mb4_0900_ai_ci COMMENT 'School or office address as shown at sign-in' AFTER `affiliation_name`,
  ADD COLUMN `affiliation_confirmed_at` DATETIME(6) COMMENT 'When the user confirmed the school or office after the password' AFTER `affiliation_address`,
  ALGORITHM=INSTANT;
ALTER TABLE `user_session`
  ADD CONSTRAINT `ck_user_session__ended_reason` CHECK (`ended_reason` IS NULL OR `ended_reason` IN ('signed_out', 'idle_timeout', 'expired', 'replaced', 'ended_by_administrator', 'account_inactive'));
ALTER TABLE `role_grant`
  ADD COLUMN `office_scope_id` BINARY(16) COMMENT 'School or office the holder works in when it differs from the grant''s scope — e.g. a ministry official with state-wide scope works in the Ministry of Education (soft; CR-007)' AFTER `supervised_until`,
  ALGORITHM=INSTANT;
ALTER TABLE `role`
  MODIFY COLUMN `clearance` VARCHAR(32) CHARACTER SET ascii COLLATE ascii_bin NOT NULL COMMENT 'Highest classification the role normally receives — its access level (1 public … 5 special, CR-007)';
