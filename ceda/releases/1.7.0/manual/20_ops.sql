-- CEDA 1.7.0 expand script for the operations zone (hand-written; reviewed with the delta). Change request CR-006.
-- The new budget lines, funding applications and disbursements, and facility actions reference existing tables
-- through tenant-scoped composite foreign keys, which need a (tenant_id, id) unique key on the referenced table.
-- Adding a secondary unique index on columns that are already unique (id is the primary key) is an online
-- operation that cannot fail on existing data; nothing is rewritten. Runs before the 1.7.0 delta of this zone.
SET NAMES utf8mb4;
ALTER TABLE `budget` ADD UNIQUE KEY `uq_budget_tenant_id_id` (`tenant_id`, `id`), ALGORITHM=INPLACE, LOCK=NONE;
ALTER TABLE `capital_plan_item` ADD UNIQUE KEY `uq_capital_plan_item_tenant_id_id` (`tenant_id`, `id`), ALGORITHM=INPLACE, LOCK=NONE;
ALTER TABLE `maintenance_request` ADD UNIQUE KEY `uq_maintenance_request_tenant_id_id` (`tenant_id`, `id`), ALGORITHM=INPLACE, LOCK=NONE;
