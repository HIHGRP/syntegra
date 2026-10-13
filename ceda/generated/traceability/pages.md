# Page → data traceability

Every one of the 260 pages in SYN-MFS-002 v2.4 is served by at least one CEDA entity or metric. Generated; do not edit.

| Page | Title | Module | Phase | CEDA entities and metrics | MFS master objects |
|---|---|---|---|---|---|
| ACA-01 | Academic calendar | Academic structure | P1 | `academic_period`, `calendar_event` | AcademicCalendar |
| ACA-02 | Year groups, classes & programmes | Academic structure | P1 | `class_group`, `code_value` | EducationLevel, Class, Programme 360 |
| ACA-03 | Subjects & courses | Academic structure | P1 | `course`, `subject` | Subject 360, Course |
| ACA-04 | Programme builder | Academic structure | P5 | `programme`, `programme_component`, `qualification` | Programme 360, Qualification 360 |
| ACA-05 | My class | Academic structure | P1 | `adjustment`, `class_group`, `class_membership`, `delivery_log`, `seating_plan` | Class, Learner 360, SEND 360 |
| ACA-101 | Class subject plan | Academic structure | P1 | `class_group`, `class_subject_plan`, `curriculum_adoption`, `staff_qualification`, `stream_combination_rule`, `teaching_assignment` |  |
| ACA-102 | Department 360 | Academic structure | P1 | `course`, `department`, `licence`, `metric:PTR`, `org_unit`, `programme`, `staff_post`, `subject_area` |  |
| ACA-103 | Course allocation | Academic structure | P1 | `course_section`, `department`, `teaching_assignment` |  |
| ADM-01 | Tenants | Platform administration | P1 | `feature_flag`, `glid_block`, `platform_user`, `residency_region`, `tenant` | Tenant |
| ADM-02 | Country configuration | Platform administration | P1 | `code_list`, `code_value`, `config_version`, `jurisdiction_pack` | CountryConfiguration |
| ADM-03 | Institution setup | Platform administration | P1 | `config_version`, `onboarding_check` | InstitutionConfiguration |
| ADM-04 | Users | Platform administration | P1 | `access_review`, `app_user`, `role_grant` | User, RoleGrant |
| ADM-05 | Roles & permissions | Platform administration | P1 | `role`, `role_permission` | Role, Permission |
| ADM-06 | Policy & rule engine | Platform administration | P2 | `policy_conflict`, `policy_rule`, `policy_rule_test` | PolicyRule |
| ADM-07 | Workflow designer | Platform administration | P1 | `workflow_definition` | WorkflowDefinition |
| ADM-08 | Integration marketplace | Platform administration | P1 | `api_client`, `integration_connection`, `webhook_delivery`, `webhook_subscription` | Integration |
| ADM-09 | API clients & data exchange | Platform administration | P6 | `api_client`, `data_sharing_agreement`, `exchange_transfer`, `service_identity` | DataSharingAgreement, ApiClient |
| ADM-10 | Data governance | Platform administration | P1 | `legal_hold`, `privacy_request`, `record_series` | DataSubjectRequest, RetentionRule |
| ADM-11 | Audit log | Platform administration | P1 | `audit_anchor`, `audit_event`, `break_glass_grant`, `outbox_event` | AuditEvent |
| ADM-12 | Languages | Platform administration | P1 | `config_version`, `translation` | Language |
| ADM-13 | Branding | Platform administration | P1 | `config_version`, `tenant_domain` | Branding |
| ADM-14 | Subscription & licensing | Platform administration | P1 | `subscription`, `subscription_plan` | Subscription |
| ADM-15 | Data import & migration | Platform administration | P1 | `import_job`, `import_row_issue` | ImportBatch |
| ADM-16 | System health | Platform administration | P1 | `backup_run`, `platform_user` | ServiceHealth |
| ADM-17 | Master data stewardship | Platform administration | P1 | `data_quality_issue`, `data_quality_rule`, `match_review`, `merge_journal`, `metric:DUP-RATE` | MatchReview |
| ADM-18 | Notification rules | Platform administration | P1 | `notification_rule`, `outbox_event` | NotificationRule |
| AGT-101 | Agent library | Automation agents | P3 | `agent_template` |  |
| AGT-102 | Configure agent | Automation agents | P3 | `agent`, `service_identity` |  |
| AGT-103 | Agent console | Automation agents | P3 | `agent`, `agent_action` |  |
| AGT-104 | Agent activity log | Automation agents | P3 | `agent_action` |  |
| AIX-01 | Recommendations queue | Intelligence | P7 | `recommendation` | Recommendation |
| AIX-02 | Document intelligence | Intelligence | P7 | `document`, `document_extraction`, `extracted_field` | Document, Extraction |
| AIX-03 | Model governance | Intelligence | P7 | `ai_model`, `ai_model_version`, `llm_call_log`, `model_deployment` | Model |
| ASM-01 | Markbook | Assessment | P1 | `assessment`, `assessment_result`, `external_assessment_import`, `markbook_column`, `metric:PROGRESS-TARGET`, `target_grade` | Assessment 360, Curriculum 360 |
| ASM-02 | Assessment setup | Assessment | P1 | `assessment` | Assessment 360 |
| ASM-03 | Grading scales | Assessment | P1 | `grade_band`, `grading_scale` | GradingScale |
| ASM-04 | Report cards | Assessment | P1 | `report_card`, `report_card_run` | ReportCard |
| ASM-05 | Moderation | Assessment | P1 | `moderation_sample` | Moderation |
| ATT-01 | Take register | Attendance | P1 | `attendance_mark`, `attendance_register`, `class_membership`, `enrolment`, `idempotency_key`, `lesson_occurrence`, `timetable_lesson` | Attendance 360, Learner 360 |
| ATT-02 | Attendance dashboard | Attendance | P1 | `attendance_mark`, `attendance_register`, `metric:ATT-PERSISTENT`, `metric:ATT-RATE`, `metric:ATT-SEVERE`, `metric:ENR-COUNT`, `staff_attendance` | Attendance 360 |
| ATT-03 | Absence follow-up | Attendance | P1 | `absence_contact` | Attendance 360, Family 360 |
| ATT-101 | Evacuation roll call | Attendance | P1 | `evacuation_event`, `evacuation_mark`, `staff_attendance`, `visitor_visit` |  |
| ATT-102 | Register compliance | Attendance | P1 | `attendance_register`, `metric:REG-COMPLIANCE` |  |
| ATT-103 | Parent-reported absences | Attendance | P1 | `absence_report` |  |
| AUT-01 | Sign in | Access | P1 | `app_user`, `credential_reset`, `tenant_domain`, `user_session` | User, Session |
| AUT-02 | Multi-factor verification | Access | P1 | `mfa_factor` |  |
| AUT-03 | Choose workspace | Access | P1 | `app_user`, `role_grant`, `scope_node`, `user_session` | User, RoleGrant, Scope |
| AUT-04 | Reset password | Access | P1 | `credential_reset` |  |
| BEH-01 | Log behaviour | Behaviour | P2 | `behaviour_event`, `behaviour_type` | BehaviourEvent, Learner 360 |
| BEH-02 | Behaviour overview | Behaviour | P2 | `behaviour_event`, `metric:BEH-RATIO` | BehaviourEvent |
| BEH-101 | Behaviour policy and rewards | Behaviour | P2 | `badge_award`, `behaviour_framework`, `behaviour_policy`, `behaviour_type`, `reward_badge` |  |
| BEH-102 | Seating plan and influences | Behaviour | P2 | `behaviour_event`, `influence_score`, `room_layout`, `seating_field_set`, `seating_plan`, `seating_plan_print` |  |
| BEH-103 | Intelligence events | Behaviour | P2 | `intel_firing`, `intel_firing_reversal`, `intel_rule` |  |
| BEH-104 | Detention manager | Behaviour | P2 | `detention`, `detention_type` |  |
| BEH-105 | On-call board | Behaviour | P2 | `duty_rota`, `oncall_request` |  |
| BEH-106 | On-report card | Behaviour | P2 | `on_report_card`, `on_report_rating`, `on_report_target` |  |
| BIL-01 | Fee structure & billing rules | Billing | P1 | `billing_rule`, `charge_type` | ChargeType, BillingRule |
| BIL-02 | Billing run | Billing | P1 | `billing_run`, `invoice` | Invoice, BillingRun |
| BIL-03 | Learner account | Billing | P1 | `account`, `ledger_entry` | Finance 360, Ledger |
| BIL-04 | Family statement | Billing | P1 | `account`, `family`, `invoice` | Family 360, Finance 360 |
| BIL-05 | Invoices | Billing | P1 | `credit_note`, `invoice`, `invoice_line`, `metric:FEE-COLLECTION` | Invoice |
| BIL-06 | Payment plans & hardship | Billing | P1 | `payment_plan`, `recovery_policy` | PaymentPlan, RecoveryPolicy |
| BIL-07 | Funding sources & sponsors | Billing | P1 | `funding_award`, `funding_source` | FundingSource |
| BIL-08 | Government funding reconciliation | Billing | P6 | `funding_source`, `government_funding_receipt`, `metric:CAPITATION-RECON` | Finance 360, FundingSource |
| CER-01 | Certificate register | Certificate 360 | P2 | `certificate` | Certificate 360 |
| CER-02 | Award eligibility run | Certificate 360 | P2 | `eligibility_result`, `eligibility_run` | Certificate 360 |
| CER-03 | Issue certificate | Certificate 360 | P2 | `certificate`, `eligibility_result`, `external_exam_record`, `qualification` | Certificate 360, Learner 360, Institution 360, Qualification 360, Examination 360 |
| CER-04 | Certificate 360 | Certificate 360 | P2 | `certificate`, `certificate_event`, `print_job`, `registry_publication`, `security_stock` | Certificate 360 |
| CER-05 | Revoke, correct or reissue | Certificate 360 | P2 | `certificate`, `certificate_event` | Certificate 360 |
| CER-06 | Certificate templates & signatories | Certificate 360 | P2 | `certificate_template`, `signatory`, `signing_key` | CertificateTemplate, Signatory |
| CER-07 | Verification requests | Certificate 360 | P2 | `forgery_report`, `verification` | Verification |
| CER-101 | Reissue requests | Certificate 360 | P2 | `fee_schedule`, `legacy_award`, `reissue_case` |  |
| CER-102 | Reissue review | Certificate 360 | P2 | `certificate_delivery`, `identity_check`, `identity_verification`, `reissue_case` |  |
| CMD-01 | Global education dashboard | Command centre | P7 | `metric:ENR-GER`, `metric:GLOBAL-INDICATORS` | Country 360 |
| CMD-02 | National command centre | Command centre | P6 | `metric:ATT-RATE`, `metric:ENR-COUNT`, `metric:ENR-GER`, `metric:ENR-NER`, `metric:ENR-TRANSITION`, `metric:EXAM-5CREDITS`, `metric:GLOBAL-INDICATORS`, `metric:HEALTH-INDEX`, `metric:PTR`, `metric:STF-QUALIFIED-RATE` | Country 360, Ministry 360, Institution 360 |
| CMD-03 | State command centre | Command centre | P6 | `metric:ATT-DROPOUT`, `metric:ATT-RATE`, `metric:CA-AVERAGE`, `metric:CUR-COVERAGE`, `metric:ENR-COUNT`, `metric:ENR-GER`, `metric:ENR-NER`, `metric:ENR-OOSC`, `metric:ENR-TRANSITION`, `metric:EXAM-5CREDITS`, `metric:HEALTH-INDEX`, `metric:INFRA-BASICS`, `metric:STF-QUALIFIED-RATE` | Ministry 360, Education Authority 360, Institution 360 |
| CMD-04 | LGA / district command centre | Command centre | P6 | `metric:ATT-PERSISTENT`, `metric:ATT-RATE`, `metric:CUR-GAPS-OPEN`, `metric:ENR-COUNT`, `metric:ENR-OOSC`, `metric:HEALTH-INDEX`, `metric:LGA-TODAY`, `metric:REG-COMPLIANCE`, `metric:STF-PRESENCE` | Education Authority 360, Institution 360 |
| CMD-05 | Network dashboard | Command centre | P4 | `metric:ATT-RATE`, `metric:ENR-COUNT`, `metric:HEALTH-INDEX`, `metric:NETWORK-SUMMARY` | Education Network 360, Institution 360 |
| CMD-06 | Institution dashboard | Command centre | P1 | `institution`, `metric:ATT-DROPOUT`, `metric:ATT-PERSISTENT`, `metric:ATT-RATE`, `metric:ATT-SEVERE`, `metric:CA-AVERAGE`, `metric:CUR-COMPLIANCE`, `metric:ENR-COUNT`, `metric:EXAM-5CREDITS`, `metric:FEE-COLLECTION`, `metric:HEALTH-INDEX`, `metric:PROGRESS-TARGET`, `metric:STF-PRESENCE` | Institution 360 |
| CMD-07 | Hierarchy explorer | Command centre | P6 | `metric:ATT-RATE`, `metric:ENR-COUNT`, `metric_definition`, `scope_closure`, `scope_node` | Scope, All 360 objects |
| CMD-08 | Follow the problem | Command centre | P6 | `investigation` | Investigation, Intervention, Institution 360, Teacher 360 |
| CMD-09 | Alert centre | Command centre | P6 | `alert`, `alert_rule` | Alert, AlertRule |
| CMD-10 | Alert detail | Command centre | P6 | `alert`, `alert_event` | Alert |
| CMD-101 | State education control room | Command centres | P1 / P6 | `alert`, `dataset_freshness`, `institution`, `learner`, `metric:ATT-RATE`, `metric:BEH-RATIO`, `metric:CAPITATION-RECON`, `metric:CERT-INTEGRITY`, `metric:CUR-COVERAGE`, `metric:CUR-GAPS-OPEN`, `metric:DATA-FRESHNESS`, `metric:DIGITISATION`, `metric:DQI`, `metric:ENR-COUNT`, `metric:EXAM-5CREDITS`, `metric:FACILITY-INCIDENTS`, `metric:FEEDING-RECON`, `metric:HEALTH-INDEX`, `metric:INFRA-BASICS`, `metric:INFRA-CLASSROOM`, `metric:INS-LIVE`, `metric:INST-PERFORMANCE`, `metric:LMS-ADOPTION`, `metric:LMS-COMPLETION`, `metric:MSG-DELIVERY`, `metric:PARENT-APP`, `metric:PTM-ATTENDANCE`, `metric:PTR`, `metric:REG-COMPLIANCE`, `metric:SAF-CONCERNS`, `metric:SEND-COVERAGE`, `metric:STF-PRESENCE`, `purpose_code`, `reg_snapshot` |  |
| CMD-102 | Institution league with context | Command centres | P6 | `institution_profile`, `metric:EXAM-5CREDITS`, `metric:HEALTH-INDEX`, `metric:INST-PERFORMANCE` |  |
| CMD-103 | Coverage and onboarding tracker | Command centres | P1 | `data_quality_issue`, `dataset_freshness`, `metric:DATA-FRESHNESS`, `metric:INS-LIVE`, `onboarding_check`, `onboarding_target`, `unknown_institution_reference` |  |
| CMD-104 | Education Administrator 360 | Command centres | P6 | `app_user`, `investigation`, `role_grant` |  |
| CMD-11 | Compare | Command centre | P6 | `institution_profile`, `metric:HEALTH-INDEX`, `metric:INST-PERFORMANCE` | Institution 360, Education Authority 360 |
| CMD-12 | What's working | Command centre | P7 | `intervention`, `metric:HEALTH-INDEX`, `practice_share` | Intervention, Institution 360 |
| CMD-13 | Resource allocation | Command centre | P6 | `metric:INFRA-CLASSROOM`, `metric:INFRA-TEXTBOOK`, `metric:TCH-DEMAND-SUPPLY`, `recommendation`, `resource_proposal` | Institution 360, Infrastructure 360, Teacher 360 |
| CMD-14 | Planning scenarios | Command centre | P7 | `metric:TCH-DEMAND-SUPPLY`, `planning_scenario` | PlanningScenario |
| CMD-15 | Integrity command centre | Command centre | P6 | `alert`, `exam_anomaly`, `forgery_report`, `metric:CERT-INTEGRITY`, `security_stock` | Certificate 360, Learner 360, Examination 360, Institution 360 |
| CMD-16 | Data quality command centre | Command centre | P6 | `data_quality_issue`, `data_quality_rule`, `dataset_freshness`, `metric:DQI`, `metric:DUP-RATE` | DataQualityIssue |
| COM-01 | Send a message | Communication | P1 | `broadcast_campaign`, `message` | Message, Family 360 |
| COM-02 | Communication log & templates | Communication | P1 | `mail_merge_job`, `message`, `message_template`, `metric:MSG-DELIVERY` | Message, Template |
| COM-101 | Conversations inbox | Communication | P1 | `absence_report`, `channel_contact`, `channel_opt_in`, `conversation`, `message`, `workspace_channel` |  |
| COM-102 | Channels and templates | Communication | P1 | `channel_opt_in`, `message_channel`, `message_template`, `workspace_channel` |  |
| COM-103 | Broadcast campaigns | Communication | P1 | `broadcast_campaign`, `metric:MSG-DELIVERY` |  |
| COM-104 | Staff announcements and consent requests | Communication | P1 | `announcement_recipient`, `consent_record`, `consent_request`, `staff_announcement` |  |
| CUR-01 | Curriculum library | Curriculum 360 | P2 | `curriculum` | Curriculum 360 |
| CUR-02 | Curriculum editor | Curriculum 360 | P2 | `curriculum_node`, `curriculum_version`, `subject` | Curriculum 360, Subject 360 |
| CUR-03 | Curriculum approval | Curriculum 360 | P2 | `curriculum_version` | Curriculum 360 |
| CUR-04 | Curriculum 360 | Curriculum 360 | P2 | `curriculum`, `curriculum_node`, `curriculum_version` | Curriculum 360 |
| CUR-05 | State adaptation | Curriculum 360 | P2 | `policy_rule` | Curriculum 360, PolicyRule |
| CUR-06 | Curriculum compliance | Curriculum 360 | P2 | `curriculum_adoption`, `metric:CUR-COMPLIANCE`, `metric:CUR-HOURS` | Curriculum 360, Institution 360 |
| CUR-07 | Compliance heatmap | Curriculum 360 | P6 | `metric:CUR-COMPLIANCE`, `metric:CUR-COVERAGE` | Curriculum 360 |
| CUR-08 | Policy conflicts & exceptions | Curriculum 360 | P2 | `policy_conflict`, `policy_exception`, `policy_rule` | PolicyException, PolicyRule |
| CUR-09 | Lesson plan & delivery log | Curriculum 360 | P2 | `delivery_log`, `scheme_of_work`, `scheme_week` | LessonPlan, DeliveryLog, Curriculum 360 |
| CUR-101 | Coverage assurance | Curriculum 360 | P2 | `coverage_gap`, `curriculum_adoption`, `metric:CUR-COVERAGE`, `metric:CUR-GAPS-OPEN`, `metric:CUR-HOURS` |  |
| CUR-102 | Teaching assignment matrix | Curriculum 360 | P1 | `class_subject_plan`, `coverage_gap`, `staff_qualification`, `teaching_assignment` |  |
| CUR-103 | Gap register | Curriculum 360 | P2 | `coverage_gap`, `gap_event`, `metric:CUR-GAPS-OPEN` |  |
| DOC-101 | Digitisation programme | Records & archives | P1 | `digitisation_batch`, `digitisation_site_survey`, `metric:DIGITISATION`, `qa_sample` |  |
| DOC-102 | Batches and custody | Records & archives | P1 | `custody_event`, `digitisation_batch` |  |
| DOC-103 | Indexing and QA workstation | Records & archives | P1 | `extracted_field`, `qa_sample`, `scanned_page` |  |
| DOC-104 | Records search | Records & archives | P1 | `document`, `legacy_award`, `record_request` |  |
| DOC-105 | Document viewer | Records & archives | P1 | `document`, `document_link`, `redaction` |  |
| DOC-106 | File plan and retention | Records & archives | P1 | `disposal`, `document_category`, `legal_hold`, `record_series` |  |
| EXM-01 | Examination series | Examinations | P1 | `exam_series` | Examination 360, Qualification 360 |
| EXM-02 | Candidate entries | Examinations | P1 | `exam_entry` | Examination 360, Learner 360 |
| EXM-03 | Exam timetable & seating | Examinations | P1 | `exam_paper`, `exam_sitting` | Sitting |
| EXM-04 | Results entry & import | Examinations | P1 | `exam_result`, `result_import` | Examination 360, Result |
| EXM-05 | Results approval & release | Examinations | P1 | `exam_result`, `exam_series`, `grade_broadsheet` | Examination 360 |
| EXM-06 | Transcripts | Examinations | P5 | `transcript` | Transcript, Learner 360 |
| EXM-07 | GPA & classification | Examinations | P5 | `academic_standing`, `programme` | Result, Programme 360 |
| EXM-08 | Exam anomaly review | Examinations | P6 | `exam_anomaly`, `result_import` | Examination 360 |
| EYR-01 | Observations & milestones | Early years | P1 | `authorised_collector`, `collection_record`, `eyr_observation`, `eyr_session_booking` | Observation, Learner 360 |
| EYR-02 | Development tracker | Early years | P1 | `care_log`, `development_milestone`, `eyr_observation` | Learner 360 |
| FAM-01 | Family 360 | Families | P1 | `authorised_collector`, `contact_restriction`, `family`, `family_member`, `guardian`, `learner_guardian`, `organisation_contact` | Family 360, Parent/Guardian 360, Learner 360 |
| FAM-02 | Link a guardian | Families | P1 | `guardian`, `learner_guardian`, `match_review` | Parent/Guardian 360 |
| FAM-03 | Parent home | Families | P1 | `absence_report`, `guardian`, `report_card` | Family 360, Learner 360 |
| FAM-04 | Consents | Families | P1 | `consent_record` | Consent |
| FIN-01 | Budget planning | Finance | P4 | `budget` | Budget |
| FIN-02 | Budget vs actual | Finance | P4 | `budget`, `metric:BUDGET-EXECUTION` | Budget, Ledger |
| FIN-03 | Procurement | Finance | P4 | `purchase_order`, `requisition`, `supplier` | Requisition, PurchaseOrder, Supplier 360 |
| FIN-04 | Supplier 360 | Finance | P4 | `supplier` | Supplier 360 |
| FIN-05 | General ledger | Finance | P4 | `account`, `fiscal_period`, `journal`, `ledger_entry` | Journal, Account |
| FIN-06 | Currencies & tax | Finance | P1 | `fx_rate`, `tax_rule` | Currency |
| FRM-101 | Form builder | Forms | P2 | `form_definition` |  |
| FRM-102 | Forms and Daybook | Forms | P2 | `form_response` |  |
| HED-01 | Admissions pipeline | Admissions | P1 | `admission_application`, `admission_enquiry`, `international_student_record` | Applicant, Programme 360 |
| HED-02 | Application review | Admissions | P1 | `admission_application`, `external_exam_record` | Applicant, Certificate 360 |
| HED-03 | Course registration | Higher education | P5 | `course_registration`, `course_section` | CourseRegistration, Programme 360 |
| HED-04 | Accommodation | Higher education | P5 | `accommodation_allocation`, `room` | Room, Allocation |
| HED-05 | Research students & ethics | Higher education | P5 | `ethics_application`, `research_candidature` | ResearchCandidature, EthicsApplication |
| HED-06 | Graduation & alumni | Higher education | P5 | `academic_standing`, `alumnus`, `certificate`, `graduation_list` | Certificate 360, Alumnus |
| HED-07 | Scholarships & bursaries | Finance | P4 | `funding_award`, `funding_source` | FundingSource, Award |
| HOM-01 | My briefing | Home | P6 | `alert`, `user_pin` | Alert, Education Administrator 360 |
| HOM-02 | Notifications | Home | P1 | `message`, `notification` | Notification |
| HOM-03 | My tasks | Home | P1 | `workflow_instance`, `workflow_task`, `workflow_transition` | WorkflowInstance, Task |
| HOM-04 | My profile & preferences | Home | P1 | `app_user`, `mfa_factor`, `user_pin`, `user_session` |  |
| HOM-05 | Search | Home | P1 | `document`, `institution`, `learner`, `staff` |  |
| HOM-06 | Education assistant | Intelligence | P7 | `assistant_conversation` | All permitted 360 objects |
| ILP-101 | Learning plans | Interventions | P3 | `learning_plan`, `learning_plan_template` |  |
| ILP-102 | Personal learning plan | Interventions | P3 | `learning_plan`, `learning_plan_entry`, `learning_plan_goal` |  |
| INS-01 | Institution register | Institutions | P1 | `institution` | Institution 360 |
| INS-02 | Institution 360 | Institutions | P1 | `campus`, `document_link`, `institution`, `institution_change_request`, `licence`, `metric:CUR-COMPLIANCE`, `metric:DQI`, `reg_dataset_definition` | Institution 360, Campus 360, Accreditation 360, Inspection 360 |
| INS-03 | Register an institution | Institutions | P1 | `institution`, `match_review`, `workflow_instance` | Institution 360, Licence, WorkflowInstance |
| INS-04 | Licences & accreditation | Institutions | P1 | `licence` | Accreditation 360, Licence |
| INS-05 | Health index breakdown | Institutions | P6 | `health_index_policy`, `metric:HEALTH-INDEX` | Institution 360, HealthIndexPolicy |
| INS-06 | Organisation structure | Institutions | P1 | `campus`, `org_unit` | Campus 360, OrgUnit |
| INS-07 | Inspections | Inspection & compliance | P6 | `inspection`, `inspection_programme` | Inspection 360 |
| INS-08 | Inspection workspace | Inspection & compliance | P6 | `inspection`, `inspection_finding` | Inspection 360, Curriculum 360, Institution 360 |
| INS-09 | Compliance centre | Inspection & compliance | P4 | `compliance_requirement`, `compliance_status`, `facility_check` | ComplianceRequirement, Institution 360 |
| INS-10 | Improvement workspace | Inspection & compliance | P6 | `improvement_plan`, `intervention` | ImprovementPlan, Intervention |
| INS-11 | Corrective action plan | Inspection & compliance | P6 | `corrective_action` | CorrectiveActionPlan, Institution 360 |
| INT-01 | Interventions | Interventions | P2 | `intervention` | Intervention |
| INT-02 | Early warning — learners | Interventions | P7 | `risk_flag` | RiskScore, Learner 360 |
| LMS-101 | Course space | LMS | P2 | `content_library_item`, `course_member`, `course_space`, `discussion_post`, `live_class`, `lms_content`, `lms_unit`, `scheme_of_work` |  |
| LMS-102 | Create or edit assignment | LMS | P2 | `adjustment`, `assignment`, `rubric` |  |
| LMS-103 | Submission (learner) | LMS | P2 | `quiz_attempt`, `submission`, `submission_file` |  |
| LMS-104 | Marking workspace | LMS | P2 | `extension`, `moderation_sample`, `originality_report`, `rubric`, `submission`, `submission_mark` |  |
| LMS-105 | My marking | LMS | P2 | `submission_mark` |  |
| LMS-106 | Quiz and question bank | LMS | P2 | `question`, `quiz_attempt` |  |
| LMS-107 | Learner work (my assignments) | LMS | P2 | `assignment`, `extension`, `submission`, `ussd_session` |  |
| LMS-108 | Digital learning dashboard | LMS | P2 | `digital_skill_level`, `metric:DIGITAL-SKILLS`, `metric:LMS-ADOPTION`, `metric:LMS-COMPLETION` |  |
| LMS-109 | Homework calendar | Digital learning | P2 | `assignment`, `homework_limit` |  |
| LRN-01 | Learners | Learners | P1 | `learner` | Learner 360 |
| LRN-02 | Register a learner | Learners | P1 | `external_identifier`, `identity_verification`, `learner` | Learner 360, Parent/Guardian 360, Identity |
| LRN-03 | Duplicate review | Learners | P1 | `match_pair_decision`, `match_review` | Learner 360, MatchReview |
| LRN-04 | Learner 360 | Learners | P2 | `assessment_result`, `attendance_mark`, `document_link`, `exam_result`, `external_exam_record`, `external_identifier`, `international_student_record`, `learner`, `learner_guardian`, `purpose_code`, `target_grade` | Learner 360, Attendance 360, Assessment 360, SEND 360, Safeguarding 360, Finance 360 |
| LRN-05 | Transfer a learner | Learners | P1 | `enrolment`, `exchange_transfer`, `historical_record_import`, `learner_transfer` | Learner 360, Enrolment |
| LRN-06 | Education passport | Learners | P7 | `badge_award`, `digital_skill_level`, `passport_entry`, `passport_share`, `passport_view` | Education Passport 360, Certificate 360 |
| LRN-07 | Enrolment & placement | Learners | P1 | `enrolment`, `historical_record_import` | Enrolment, Learner 360, Programme 360 |
| LRN-08 | Merge records | Learners | P1 | `merge_journal` | Learner 360, MergeHistory |
| LRN-09 | Withdraw / leaver | Learners | P1 | `cme_referral`, `destination_record`, `enrolment` | Enrolment, OutcomeRecord |
| MED-01 | Clinical placements & rotations | Medical education | P5 | `clinical_site`, `placement`, `skills_lab_session` | Placement, ClinicalSite |
| MED-02 | Clinical logbook & sign-off | Medical education | P5 | `competency_record`, `logbook_entry` | LogbookEntry, Competency |
| MED-03 | Clinical hours & registration readiness | Medical education | P5 | `exam_paper`, `professional_body`, `registration_readiness` | Learner 360, Qualification 360 |
| OPS-01 | Estate & rooms | Operations | P3 | `building`, `capital_plan_item`, `metric:INFRA-CLASSROOM`, `room` | Infrastructure 360, Room |
| OPS-02 | Asset register | Operations | P3 | `asset`, `asset_inspection` | Asset |
| OPS-03 | Maintenance | Operations | P3 | `facility_incident`, `maintenance_request`, `metric:FACILITY-INCIDENTS` | MaintenanceRequest |
| OPS-04 | Transport | Operations | P3 | `boarding_record`, `transport_allocation`, `transport_route`, `vehicle` | Route, Vehicle |
| OPS-05 | Clubs & activities | Operations | P3 | `activity`, `activity_enrolment` | Activity |
| OPS-06 | Trips & visits | Operations | P3 | `consent_record`, `consent_request`, `trip`, `trip_participant` | Trip, Consent |
| OPS-07 | Meals & nutrition | Operations | P3 | `dietary_requirement`, `meal_service`, `metric:FEEDING-RECON` | MealService |
| OPS-08 | Library | Operations | P3 | `learning_resource`, `library_item`, `library_loan`, `metric:INFRA-TEXTBOOK`, `resource_issue` | LibraryItem, Loan |
| P16-01 | Subject options | Post-16 & careers | P1 | `guidance_session`, `option_choice`, `stream_combination_rule` | OptionChoice |
| P16-02 | Applications & careers | Post-16 & careers | P5 | `destination_record`, `guidance_session`, `he_application`, `student_finance_application` | Application |
| PAY-01 | Payroll runs | People | P4 | `payroll_run`, `payroll_tax_table` | PayRun |
| PAY-02 | Pay run detail | People | P4 | `payroll_run`, `payslip` | PayRun |
| PMT-01 | Payments & receipts | Payments | P1 | `payment`, `payment_allocation` | Payment, Ledger |
| PMT-02 | Bank reconciliation | Payments | P4 | `bank_statement_line` | BankStatement |
| PMT-03 | Pay online | Payments | P1 | `idempotency_key`, `inbound_webhook`, `payment` | Payment |
| PTM-101 | Parents' meetings | Parents' meetings | P2 | `meeting_booking`, `meeting_event`, `metric:PTM-ATTENDANCE` |  |
| PUB-01 | Verify a certificate | Public verification | P2 | `verification` | Certificate 360 |
| PUB-02 | Verification result | Public verification | P2 | `certificate`, `verification` | Certificate 360 |
| PUB-03 | Online application | Admissions | P1 | `admission_application`, `admission_enquiry`, `learner` | Applicant, Learner 360, Programme 360 |
| PUB-101 | Request a certificate reissue | Public verification | P2 | `fee_schedule`, `record_request`, `reissue_case` |  |
| PVT-101 | Provider application | Private providers | P1 | `application_evidence`, `application_query`, `approval_checklist_item`, `identity_verification`, `provider_application`, `provider_person`, `regulatory_fee` |  |
| PVT-102 | Application review | Private providers | P1 | `application_evidence`, `application_query`, `approval_checklist_item`, `inspection`, `provider_application` |  |
| PVT-103 | Provider 360 | Private providers | P1 | `approval`, `closure_case`, `provider`, `provider_person`, `reg_dataset_definition`, `reg_snapshot`, `regulatory_fee`, `sanction` |  |
| PVT-104 | Private institutions register | Private providers | P1 | `approval`, `closure_case`, `institution`, `provider`, `unknown_institution_reference` |  |
| PVT-105 | Approval conditions and renewals | Private providers | P2 | `approval`, `approval_condition`, `corrective_action`, `sanction` |  |
| RPT-01 | Report library | Reporting | P1 | `report_definition`, `report_export` | ReportDefinition |
| RPT-02 | Report builder | Reporting | P6 | `metric_definition`, `report_definition`, `report_export` | ReportDefinition, Metric |
| RPT-03 | Government return | Reporting | P6 | `return_definition`, `return_submission` | Return |
| RPT-04 | Data lineage | Reporting | P6 | `metric_definition` | Metric |
| RPT-05 | Scheduled reports | Reporting | P1 | `report_schedule` | ReportSchedule |
| SAF-01 | Record a concern | Safeguarding | P2 | `safeguarding_concern` | Safeguarding 360, Learner 360 |
| SAF-02 | Safeguarding caseload | Safeguarding | P2 | `community_report`, `safeguarding_case`, `safeguarding_concern` | Safeguarding 360 |
| SAF-03 | Safeguarding case | Safeguarding | P2 | `case_access_grant`, `case_access_log`, `case_share`, `contact_restriction`, `safeguarding_case`, `safeguarding_entry` | Safeguarding 360 |
| SAF-04 | External referral | Safeguarding | P2 | `case_share`, `safeguarding_referral` | Safeguarding 360, Referral |
| SAF-101 | Staff allegations and low-level concerns | Safeguarding | P2 | `case_access_log`, `staff_case`, `staff_case_entry` |  |
| SAF-102 | Community reporting forms | Safeguarding | P2 | `community_report`, `community_report_reply`, `jurisdiction_pack`, `reporting_form` |  |
| SAF-103 | Safeguarding insights | Safeguarding | P2 | `metric:SAF-CONCERNS`, `report_definition` |  |
| SEN-01 | SEND register | SEND & inclusion | P2 | `gifted_register_entry`, `send_profile` | SEND 360 |
| SEN-02 | Learner support profile | SEND & inclusion | P2 | `adjustment`, `external_referral`, `send_need`, `send_profile` | SEND 360, Learner 360 |
| SEN-03 | Support plan & review | SEND & inclusion | P2 | `support_plan`, `support_plan_review` | SEND 360, SupportPlan |
| SEN-04 | Provision map | SEND & inclusion | P2 | `metric:SEND-COVERAGE`, `provision`, `provision_allocation` | SEND 360, Provision |
| STF-01 | Staff directory | People | P1 | `staff` | Staff 360 |
| STF-02 | Staff 360 | People | P1 | `document_link`, `staff`, `staff_post`, `staff_qualification` | Staff 360, Teacher 360 |
| STF-03 | Onboard staff | People | P4 | `external_identifier`, `match_review`, `staff`, `staff_post` | Staff 360 |
| STF-04 | Recruitment | People | P4 | `job_application`, `vacancy` | Vacancy, Application, Staff 360 |
| STF-05 | Applicant review | People | P4 | `job_application` | Application |
| STF-06 | Staff absence & cover | People | P3 | `cover_assignment`, `staff_absence` | Staff 360, Timetable, CoverAssignment |
| STF-07 | CPD & training | People | P4 | `cpd_record`, `metric:CPD-COMPLIANCE` | CPDRecord, Teacher 360 |
| STF-08 | Teacher qualifications register | People | P6 | `metric:STF-QUALIFIED-RATE`, `professional_registration_check`, `staff`, `staff_qualification` | Teacher 360, Curriculum 360 |
| STF-09 | Performance review | People | P4 | `appraisal` | Appraisal, Staff 360 |
| STF-10 | Teacher deployment | People | P6 | `metric:PTR`, `metric:TCH-DEMAND-SUPPLY`, `planning_scenario`, `staff_post` | Teacher 360, Curriculum 360 |
| STF-101 | Safeguarding training and compliance | Staff, HR and payroll | P2 | `metric:CPD-COMPLIANCE`, `staff_pulse_response`, `training_completion`, `training_course` |  |
| SUB-101 | SDAF rate card | Billing | P1 | `sdaf_rate`, `sdaf_rate_card` |  |
| SUB-102 | Term census and billable learners | Billing | P1 | `academic_period`, `billing_period`, `billing_period_billed`, `census_flag`, `census_learner`, `census_snapshot`, `enrolment`, `sdaf_exemption` |  |
| SUB-103 | SDAF demand and collections | Billing | P1 | `billing_period_billed`, `inbound_webhook`, `metric:SDAF-COLLECTION`, `sdaf_collection`, `sdaf_demand`, `unmatched_collection` |  |
| SUB-104 | Remittance and reconciliation | Billing | P1 | `metric:SDAF-COLLECTION`, `reconciliation_line`, `reconciliation_statement`, `remittance`, `remittance_allocation`, `service_credit` |  |
| SUB-105 | Programme financing dashboard | Billing | P1 | `billing_period`, `metric:SDAF-COLLECTION`, `reconciliation_statement`, `sdaf_public_summary` |  |
| SUB-106 | SDAF exemptions and payers | Billing | P1 | `sdaf_exemption`, `sdaf_exemption_category`, `sdaf_payer_rule` |  |
| SUB-107 | Subscription and billing | Billing | P1 | `subscription`, `subscription_invoice`, `subscription_invoice_line`, `subscription_payment`, `subscription_quote` |  |
| SUB-108 | Operator subscription management | Billing | P1 | `operator_receivable`, `service_credit`, `subscription`, `subscription_credit_note`, `subscription_invoice`, `subscription_payment`, `subscription_plan`, `subscription_quote` |  |
| SUB-109 | Pay the Student Digital Access Fee | Billing | Pages | `sdaf_collection`, `sdaf_demand` |  |
| TIM-01 | Timetable builder | Timetable | P3 | `period_structure`, `timetable`, `timetable_lesson` | Timetable, Curriculum 360, Teacher 360, Room |
| TIM-02 | Timetable | Timetable | P3 | `lesson_occurrence`, `timetable`, `timetable_lesson` | Timetable |
| TIM-03 | Cover board | Timetable | P3 | `cover_assignment`, `duty_rota`, `lesson_occurrence` | CoverAssignment |
| TIM-04 | Rooms & bookings | Timetable | P3 | `letting`, `room`, `room_booking` | Room, Booking |
| TVT-01 | Competency tracking | TVET | P5 | `competency_framework`, `competency_record` | Competency, Qualification 360, Learner 360 |
| TVT-02 | Workshops & practicals | TVET | P5 | `asset`, `room` | Room, Asset |
| TVT-03 | Apprenticeships & placements | TVET | P5 | `employer_partner`, `industrial_training`, `placement` | Placement, Employer 360 |
| TVT-04 | Employer partner 360 | TVET | P5 | `employer_partner` | Employer 360 |
| TVT-05 | Skills passport | TVET | P5 | `competency_record`, `passport_entry` | Education Passport 360 |
| WEL-01 | Wellbeing | Wellbeing | P2 | `wellbeing_checkin`, `wellbeing_concern` | Wellbeing, Learner 360 |
| WEL-101 | Wellbeing concerns and insights | Wellbeing | P2 | `wellbeing_checkin`, `wellbeing_concern` |  |
