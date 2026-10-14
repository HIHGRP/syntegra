-- CEDA 1.5.0 expand script for the registry zone (hand-written; reviewed with the delta). Change request CR-004.
-- Widens two checks on scope_node so agencies and their formations can be scope nodes (agency structures are the
-- access hierarchy). Existing rows satisfy the wider checks. Runs before the 1.5.0 delta, which adds the eight
-- security-training tables and the new code-list values.
SET NAMES utf8mb4;
ALTER TABLE `scope_node` DROP CHECK `ck_scope_node__level`;
ALTER TABLE `scope_node` ADD CONSTRAINT `ck_scope_node__level` CHECK (`level` IN ('global', 'country', 'state', 'authority', 'lga', 'network', 'institution', 'campus', 'faculty', 'department', 'programme', 'class', 'agency', 'formation'));
ALTER TABLE `scope_node` DROP CHECK `ck_scope_node__ref_kind`;
ALTER TABLE `scope_node` ADD CONSTRAINT `ck_scope_node__ref_kind` CHECK (`ref_kind` IS NULL OR `ref_kind` IN ('tenant', 'institution', 'campus', 'org_unit', 'class_group', 'course_section', 'programme', 'network', 'security_agency', 'agency_unit'));
