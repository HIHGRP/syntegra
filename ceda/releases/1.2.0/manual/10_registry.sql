-- CEDA 1.2.0 expand script for the registry zone (hand-written; reviewed with the delta).
-- New tenant-consistent foreign keys (employment_record → staff_post, clearance_check → learner_transfer)
-- reference (tenant_id, id), which needs a unique key on the parent. Adding a unique key over the primary key
-- plus tenant_id cannot fail on existing data and is an online operation in MySQL 9.7 (ALGORITHM=INPLACE).
-- Runs before the 1.2.0 delta of the same zone.
ALTER TABLE `staff_post` ADD UNIQUE KEY `uq_staff_post_tenant_id_id` (`tenant_id`, `id`), ALGORITHM=INPLACE, LOCK=NONE;
ALTER TABLE `learner_transfer` ADD UNIQUE KEY `uq_learner_transfer_tenant_id_id` (`tenant_id`, `id`), ALGORITHM=INPLACE, LOCK=NONE;
