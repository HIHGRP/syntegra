-- CEDA 1.5.0 expand script for the warehouse zone (hand-written). Change request CR-004.
-- The scope dimension mirrors scope_node levels; widen its check the same way.
SET NAMES utf8mb4;
ALTER TABLE `dim_scope` DROP CHECK `ck_dim_scope__level`;
ALTER TABLE `dim_scope` ADD CONSTRAINT `ck_dim_scope__level` CHECK (`level` IN ('global', 'country', 'state', 'authority', 'lga', 'network', 'institution', 'campus', 'faculty', 'department', 'programme', 'class', 'agency', 'formation'));
