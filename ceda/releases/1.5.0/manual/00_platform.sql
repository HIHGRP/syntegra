-- CEDA 1.5.0 expand script for the platform zone (hand-written; reviewed with the delta). Change request CR-004.
-- Widens the tenant kind check to admit sector registries (the Federal Security Education registry, ng-fse).
-- Every existing row satisfies the wider check, so the constraint is re-created without touching data.
SET NAMES utf8mb4;
ALTER TABLE `tenant` DROP CHECK `ck_tenant__kind`;
ALTER TABLE `tenant` ADD CONSTRAINT `ck_tenant__kind` CHECK (`kind` IN ('global', 'country', 'state', 'network', 'private_provider', 'institution', 'department', 'sector_registry'));
