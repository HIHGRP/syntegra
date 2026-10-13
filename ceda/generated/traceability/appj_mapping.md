# MFS Appendix J → CEDA mapping

Each of the 174 tables in SYN-MFS-002 v2.4 Book 3 Appendix J and the CEDA entity that re-specifies it. Generated; do not edit.

| Appendix J table | Domain (MFS) | CEDA entity | CEDA zone | Note |
|---|---|---|---|---|
| `tenant` | Platform & governance | `tenant` | platform |  |
| `scope_node` | Platform & governance | `scope_node` | registry |  |
| `app_user` | Platform & governance | `app_user` | registry |  |
| `role` | Platform & governance | `role` | registry |  |
| `role_permission` | Platform & governance | `role_permission` | registry |  |
| `role_grant` | Platform & governance | `role_grant` | registry |  |
| `policy_rule` | Platform & governance | `policy_rule` | registry |  |
| `policy_exception` | Platform & governance | `policy_exception` | registry |  |
| `config_version` | Platform & governance | `config_version` | registry |  |
| `institution` | Institutions | `institution` | registry |  |
| `campus` | Institutions | `campus` | registry |  |
| `org_unit` | Institutions | `org_unit` | registry |  |
| `licence` | Institutions | `licence` | registry |  |
| `inspection` | Institutions | `inspection` | registry |  |
| `inspection_finding` | Institutions | `inspection_finding` | registry |  |
| `learner` | People | `learner` | registry |  |
| `external_identifier` | People | `external_identifier` | registry |  |
| `guardian` | People | `guardian` | registry |  |
| `learner_guardian` | People | `learner_guardian` | registry |  |
| `family` | People | `family` | ops |  |
| `family_member` | People | `family_member` | ops |  |
| `staff` | People | `staff` | registry |  |
| `staff_post` | People | `staff_post` | registry |  |
| `staff_qualification` | People | `staff_qualification` | registry |  |
| `academic_period` | Academic & curriculum | `academic_period` | registry |  |
| `subject` | Academic & curriculum | `subject` | registry |  |
| `programme` | Academic & curriculum | `programme` | registry |  |
| `programme_component` | Academic & curriculum | `programme_component` | registry |  |
| `qualification` | Academic & curriculum | `qualification` | registry |  |
| `class_group` | Academic & curriculum | `class_group` | ops |  |
| `enrolment` | Academic & curriculum | `enrolment` | registry |  |
| `curriculum` | Academic & curriculum | `curriculum` | registry |  |
| `curriculum_version` | Academic & curriculum | `curriculum_version` | registry |  |
| `curriculum_node` | Academic & curriculum | `curriculum_node` | registry |  |
| `curriculum_adoption` | Academic & curriculum | `curriculum_adoption` | registry |  |
| `lesson_plan` | Academic & curriculum | `scheme_of_work` | ops | renamed |
| `delivery_log` | Academic & curriculum | `delivery_log` | ops |  |
| `room` | Academic & curriculum | `room` | ops |  |
| `timetable_lesson` | Academic & curriculum | `timetable_lesson` | ops |  |
| `attendance_mark` | Academic & curriculum | `attendance_mark` | ops |  |
| `assessment` | Academic & curriculum | `assessment` | ops |  |
| `assessment_result` | Academic & curriculum | `assessment_result` | ops |  |
| `grading_scale` | Academic & curriculum | `grading_scale` | registry |  |
| `exam_series` | Academic & curriculum | `exam_series` | ops |  |
| `exam_entry` | Academic & curriculum | `exam_entry` | ops |  |
| `exam_result` | Academic & curriculum | `exam_result` | ops |  |
| `certificate` | Certificates | `certificate` | registry |  |
| `certificate_event` | Certificates | `certificate_event` | registry |  |
| `verification` | Certificates | `verification` | registry |  |
| `behaviour_event` | Learner success | `behaviour_event` | ops |  |
| `safeguarding_case` | Learner success | `safeguarding_case` | vault |  |
| `safeguarding_entry` | Learner success | `safeguarding_entry` | vault |  |
| `send_profile` | Learner success | `send_profile` | vault |  |
| `adjustment` | Learner success | `adjustment` | ops |  |
| `intervention` | Learner success | `intervention` | ops |  |
| `account` | Finance | `account` | ops |  |
| `billing_rule` | Finance | `billing_rule` | ops |  |
| `invoice` | Finance | `invoice` | ops |  |
| `ledger_entry` | Finance | `ledger_entry` | ops |  |
| `payment` | Finance | `payment` | ops |  |
| `funding_source` | Finance | `funding_source` | ops |  |
| `workflow_definition` | Cross-cutting | `workflow_definition` | registry |  |
| `workflow_instance` | Cross-cutting | `workflow_instance` | ops, registry |  |
| `workflow_task` | Cross-cutting | `workflow_task` | ops, registry |  |
| `match_review` | Cross-cutting | `match_review` | registry |  |
| `alert` | Cross-cutting | `alert` | ops, registry |  |
| `recommendation` | Cross-cutting | `recommendation` | ops |  |
| `document` | Cross-cutting | `document` | records |  |
| `audit_event` | Cross-cutting | `audit_event` | ops, platform, records, registry, vault |  |
| `outbox_event` | Cross-cutting | `outbox_event` | ops, platform, records, registry, vault |  |
| `subscription` | Platform & governance | `subscription` | platform |  |
| `scope_closure` | Platform & governance | `scope_closure` | registry |  |
| `supplier` | Finance | `supplier` | ops |  |
| `provider` | Private providers | `provider` | registry |  |
| `provider_application` | Private providers | `provider_application` | registry |  |
| `application_evidence` | Private providers | `application_evidence` | registry |  |
| `approval` | Private providers | `approval` | registry |  |
| `approval_condition` | Private providers | `approval_condition` | registry |  |
| `department` | Academic structure | `department` | registry |  |
| `course` | Academic structure | `course` | registry |  |
| `course_section` | Academic structure | `course_section` | ops |  |
| `class_subject_plan` | Academic structure | `class_subject_plan` | ops |  |
| `teaching_assignment` | Academic structure | `teaching_assignment` | ops |  |
| `coverage_gap` | Curriculum 360 | `coverage_gap` | ops |  |
| `gap_event` | Curriculum 360 | `gap_event` | ops |  |
| `course_space` | LMS | `course_space` | ops |  |
| `lms_unit` | LMS | `lms_unit` | ops |  |
| `lms_content` | LMS | `lms_content` | ops |  |
| `assignment` | LMS | `assignment` | ops |  |
| `rubric` | LMS | `rubric` | ops |  |
| `submission` | LMS | `submission` | ops |  |
| `submission_file` | LMS | `submission_file` | ops |  |
| `submission_mark` | LMS | `submission_mark` | ops |  |
| `extension` | LMS | `extension` | ops |  |
| `question` | LMS | `question` | ops |  |
| `digital_skill_level` | LMS | `digital_skill_level` | ops |  |
| `message_channel` | Communication | `message_channel` | ops |  |
| `message_template` | Communication | `message_template` | ops |  |
| `conversation` | Communication | `conversation` | ops |  |
| `message` | Communication | `message` | ops |  |
| `channel_opt_in` | Communication | `channel_opt_in` | ops |  |
| `security_stock` | Certificates | `security_stock` | registry |  |
| `registry_publication` | Certificates | `registry_publication` | registry |  |
| `reissue_case` | Certificates | `reissue_case` | registry |  |
| `identity_check` | Certificates | `identity_check` | registry |  |
| `agent` | Automation agents | `agent` | ops, registry |  |
| `agent_action` | Automation agents | `agent_action` | ops, registry |  |
| `digitisation_batch` | Records & archives | `digitisation_batch` | records |  |
| `custody_event` | Records & archives | `custody_event` | records |  |
| `scanned_page` | Records & archives | `scanned_page` | records |  |
| `extracted_field` | Records & archives | `extracted_field` | records |  |
| `record_series` | Records & archives | `record_series` | records |  |
| `legal_hold` | Records & archives | `legal_hold` | records |  |
| `disposal` | Records & archives | `disposal` | records |  |
| `form_definition` | Forms | `form_definition` | ops |  |
| `form_response` | Forms | `form_response` | ops |  |
| `meeting_event` | Parents’ meetings | `meeting_event` | ops |  |
| `meeting_booking` | Parents’ meetings | `meeting_booking` | ops |  |
| `seating_plan` | Behaviour | `seating_plan` | ops |  |
| `detention` | Behaviour | `detention` | ops |  |
| `industrial_training` | TVET | `industrial_training` | ops |  |
| `external_referral` | SEND | `external_referral` | vault |  |
| `authorised_collector` | Early years | `authorised_collector` | ops |  |
| `behaviour_policy` | Behaviour | `behaviour_policy` | ops |  |
| `behaviour_type` | Behaviour | `behaviour_type` | ops |  |
| `reward_badge` | Behaviour | `reward_badge` | ops |  |
| `badge_award` | Behaviour | `badge_award` | ops |  |
| `seating_field_set` | Behaviour | `seating_field_set` | ops |  |
| `influence_score` | Behaviour | `influence_score` | ops |  |
| `intel_rule` | Behaviour | `intel_rule` | ops |  |
| `intel_firing` | Behaviour | `intel_firing` | ops |  |
| `detention_type` | Behaviour | `detention_type` | ops |  |
| `oncall_request` | Behaviour | `oncall_request` | ops |  |
| `on_report_card` | Behaviour | `on_report_card` | ops |  |
| `on_report_target` | Behaviour | `on_report_target` | ops |  |
| `on_report_rating` | Behaviour | `on_report_rating` | ops |  |
| `evacuation_event` | Attendance | `evacuation_event` | ops |  |
| `evacuation_mark` | Attendance | `evacuation_mark` | ops |  |
| `absence_report` | Attendance | `absence_report` | ops |  |
| `staff_announcement` | Communication | `staff_announcement` | ops |  |
| `announcement_recipient` | Communication | `announcement_recipient` | ops |  |
| `consent_request` | Communication | `consent_request` | ops |  |
| `consent_response` | Communication | `consent_record` | ops | renamed |
| `wellbeing_concern` | Wellbeing | `wellbeing_concern` | vault |  |
| `learning_plan_template` | Learning plans | `learning_plan_template` | ops |  |
| `learning_plan` | Learning plans | `learning_plan` | ops |  |
| `learning_plan_goal` | Learning plans | `learning_plan_goal` | ops |  |
| `learning_plan_entry` | Learning plans | `learning_plan_entry` | ops |  |
| `staff_case` | Safeguarding | `staff_case` | vault |  |
| `staff_case_entry` | Safeguarding | `staff_case_entry` | vault |  |
| `reporting_form` | Safeguarding | `reporting_form` | ops |  |
| `community_report` | Safeguarding | `community_report` | vault |  |
| `training_course` | Staff | `training_course` | ops |  |
| `training_completion` | Staff | `training_completion` | ops |  |
| `homework_limit` | LMS | `homework_limit` | ops |  |
| `professional_body` | Medical education | `professional_body` | registry |  |
| `learning_resource` | Operations | `learning_resource` | ops |  |
| `resource_issue` | Operations | `resource_issue` | ops |  |
| `guidance_session` | Post-16 & careers | `guidance_session` | ops |  |
| `sdaf_rate_card` | Programme financing | `sdaf_rate_card` | registry |  |
| `sdaf_rate` | Programme financing | `sdaf_rate` | registry |  |
| `billing_period` | Programme financing | `billing_period` | registry |  |
| `census_snapshot` | Programme financing | `census_snapshot` | registry |  |
| `census_learner` | Programme financing | `census_learner` | registry |  |
| `sdaf_payer_rule` | Programme financing | `sdaf_payer_rule` | registry |  |
| `sdaf_exemption` | Programme financing | `sdaf_exemption` | registry |  |
| `sdaf_demand` | Programme financing | `sdaf_demand` | registry |  |
| `sdaf_collection` | Programme financing | `sdaf_collection` | registry |  |
| `remittance` | Programme financing | `remittance` | registry |  |
| `remittance_allocation` | Programme financing | `remittance_allocation` | registry |  |
| `reconciliation_statement` | Programme financing | `reconciliation_statement` | registry |  |
| `subscription_plan` | Programme financing | `subscription_plan` | platform |  |
| `subscription_invoice` | Programme financing | `subscription_invoice` | platform |  |
| `subscription_payment` | Programme financing | `subscription_payment` | platform |  |
