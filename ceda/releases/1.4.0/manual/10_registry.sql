-- CEDA 1.4.0 expand script for the registry zone (hand-written; reviewed with the delta). Change request CR-003.
-- Both changes add NULLable columns (instant in MySQL 9.7); nothing existing is rewritten, so the script is safe on
-- a live 1.3.0 database. Runs before the 1.4.0 delta of the same zone, which creates identity_provider_config.
SET NAMES utf8mb4;
ALTER TABLE `mfa_factor`
  ADD COLUMN `last_step` BIGINT COMMENT 'TOTP time step of the last accepted code — a code is never accepted twice (FR-AUT-03)' AFTER `last_used_at`,
  ALGORITHM=INSTANT;
ALTER TABLE `user_session`
  ADD COLUMN `auth_method` VARCHAR(40) CHARACTER SET ascii COLLATE ascii_bin COMMENT 'password, password+totp, password+recovery, sso:<provider>, sso:<provider>+idp_mfa' AFTER `mfa_at`,
  ALGORITHM=INSTANT;
