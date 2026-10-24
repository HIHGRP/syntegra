-- CEDA 1.6.0 expand script for the registry zone (hand-written; reviewed with the delta). Change request CR-005.
-- Widens the security institution type check to admit the agencies' secondary schools (military, navy, air force and
-- police secondary schools). Existing rows satisfy the wider check. Runs before the 1.6.0 delta, which adds the
-- federal institutions and institution regulation tables.
SET NAMES utf8mb4;
ALTER TABLE `security_institution` DROP CHECK `ck_security_institution__institution_type`;
ALTER TABLE `security_institution` ADD CONSTRAINT `ck_security_institution__institution_type` CHECK (`institution_type` IN ('secondary_school', 'military_academy', 'police_academy', 'service_academy', 'defence_university', 'staff_college', 'war_college', 'defence_college', 'depot', 'training_school', 'specialist_school', 'training_college', 'technical_institute', 'health_sciences_school', 'strategic_institute'));
