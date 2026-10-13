# CEDA domain event catalogue

Generated from `ceda/model/events.yaml`. Events are named `<DOMAIN>.<PAST_TENSE_VERB>`, published through the transactional outbox of the producing zone, carried in the CloudEvents envelope (`envelope.schema.json`) and contain identifiers and minimal non-personal facts only (MFS Book 3 §16.2). Consumers fetch details through the API under their own permissions.

| Event | Producer | Aggregate | Topic | Payload | Consumers | Trigger |
|---|---|---|---|---|---|---|
| `PLT.TENANT_PROVISIONED` | `platform` | `tenant` | `syn.{region}.plt.v1` | `tenant_id`, `kind`, `parent_id` | governance, iam, analytics, comms | A tenant (state |
| `PLT.TENANT_STATUS_CHANGED` | `platform` | `tenant` | `syn.{region}.plt.v1` | `tenant_id`, `status` | iam, integration, analytics | Tenant activated |
| `GOV.SCOPE_CHANGED` | `governance` | `scope_node` | `syn.{region}.gov.v1` | `scope_node_id`, `parent_id`, `level`, `valid_from` | iam, search, analytics, comms | Hierarchy node created |
| `GOV.CONFIG_PUBLISHED` | `governance` | `config_version` | `syn.{region}.gov.v1` | `config_version_id`, `scope_node_id`, `section`, `version` | all_modules | A configuration layer section is published |
| `GOV.POLICY_PUBLISHED` | `governance` | `policy_rule` | `syn.{region}.gov.v1` | `policy_rule_id`, `rule_key`, `version`, `effective_from` | curriculum, attendance, intelligence, financing | A rule version is published after its tests pass |
| `GOV.EXCEPTION_APPROVED` | `governance` | `policy_exception` | `syn.{region}.gov.v1` | `policy_exception_id`, `rule_id`, `scope_node_id`, `end_on` | curriculum, institutions, intelligence | A time-boxed exception is approved |
| `WF.STARTED` | `governance` | `workflow_instance` | `syn.{region}.wf.v1` | `workflow_instance_id`, `subject_kind`, `subject_id` | intelligence | Workflow instance started |
| `WF.COMPLETED` | `governance` | `workflow_instance` | `syn.{region}.wf.v1` | `workflow_instance_id`, `state` | subject_module | Workflow reached a terminal state |
| `WF.TASK_ASSIGNED` | `governance` | `workflow_task` | `syn.{region}.wf.v1` | `workflow_task_id`, `assignee_user_id`, `due_at` | comms | Human task created or reassigned |
| `WF.TASK_COMPLETED` | `governance` | `workflow_task` | `syn.{region}.wf.v1` | `workflow_task_id`, `decision` | comms, integration | Task completed (synced to workspace messaging) |
| `WF.TASK_ESCALATED` | `governance` | `workflow_task` | `syn.{region}.wf.v1` | `workflow_task_id`, `escalated_to_scope_id` | comms, intelligence | SLA breached |
| `IAM.USER_CREATED` | `iam` | `app_user` | `syn.{region}.iam.v1` | `user_id`, `person_kind` | comms, analytics | Account created or invited |
| `IAM.USER_DEACTIVATED` | `iam` | `app_user` | `syn.{region}.iam.v1` | `user_id` | comms, integration | Account deactivated (e.g. HR leaving date) — workspace channels removed |
| `IAM.GRANT_CHANGED` | `iam` | `role_grant` | `syn.{region}.iam.v1` | `role_grant_id`, `user_id`, `scope_id`, `status` | search, comms | Role-at-scope granted |
| `AUTH.SIGNED_IN` | `iam` | `user_session` | `syn.{region}.auth.v1` | `user_id`, `session_id` | analytics | Successful sign-in |
| `AUTH.FAILED` | `iam` | `user_session` | `syn.{region}.auth.v1` | `user_id` | security_monitoring | Failed sign-in |
| `AUTH.LOCKED` | `iam` | `app_user` | `syn.{region}.auth.v1` | `user_id`, `locked_until` | comms, security_monitoring | Account locked after repeated failures |
| `AUTH.MFA_PASSED` | `iam` | `user_session` | `syn.{region}.auth.v1` | `user_id`, `session_id` | analytics | MFA verified |
| `AUTH.MFA_FAILED` | `iam` | `user_session` | `syn.{region}.auth.v1` | `user_id` | security_monitoring | MFA failed |
| `ID.NIN_VERIFIED` | `mdm` | `identity_verification` | `syn.{region}.id.v1` | `identity_verification_id`, `person_kind`, `person_id`, `outcome` | learners, certificates, providers | National identifier verification returned |
| `LRN.MATCH_REVIEWED` | `mdm` | `match_review` | `syn.{region}.lrn.v1` | `match_review_id`, `entity_kind` | learners | Probable-duplicate review opened |
| `MDM.MATCH_DECIDED` | `mdm` | `match_review` | `syn.{region}.mdm.v1` | `match_review_id`, `decision` | learners, families, people, analytics | Steward decided a pair |
| `MDM.MERGED` | `mdm` | `merge_journal` | `syn.{region}.mdm.v1` | `merge_journal_id`, `entity_kind`, `survivor_id`, `merged_id` | all_modules, search, analytics | Two master records merged (references re-pointed) |
| `MDM.UNMERGED` | `mdm` | `merge_journal` | `syn.{region}.mdm.v1` | `merge_journal_id`, `survivor_id`, `merged_id` | all_modules, search, analytics | Merge reversed within 90 days |
| `INS.APPLICATION_SUBMITTED` | `providers` | `provider_application` | `syn.{region}.ins.v1` | `provider_application_id`, `kind` | institutions, intelligence | Institution registration or approval application submitted |
| `INS.REGISTERED` | `institutions` | `institution` | `syn.{region}.ins.v1` | `institution_id`, `scope_node_id`, `ownership` | governance, financing, analytics, search, comms | Institution 360 activated |
| `INS.STATUS_CHANGED` | `institutions` | `institution` | `syn.{region}.ins.v1` | `institution_id`, `status`, `onboarding_status` | analytics, financing, certificates | Institution lifecycle or onboarding status changed |
| `INS.MERGED` | `institutions` | `institution` | `syn.{region}.ins.v1` | `institution_id`, `merged_into` | all_modules | Institutions amalgamated |
| `INS.LICENCE_EXPIRED` | `institutions` | `licence` | `syn.{region}.ins.v1` | `licence_id`, `institution_id`, `kind` | certificates, assessment, intelligence | Licence passed expiry (issuance and new entries blocked) |
| `INS.LICENCE_RENEWED` | `institutions` | `licence` | `syn.{region}.ins.v1` | `licence_id`, `expires_on` | certificates, assessment | Licence renewed |
| `INSP.FINDING_RECORDED` | `institutions` | `inspection_finding` | `syn.{region}.insp.v1` | `inspection_finding_id`, `inspection_id`, `requires_action` | intelligence | Finding saved in the inspection workspace |
| `INSP.REPORT_APPROVED` | `institutions` | `inspection` | `syn.{region}.insp.v1` | `inspection_id`, `institution_id` | intelligence, providers, analytics | Report approved (corrective actions created) |
| `INSP.ACTION_VERIFIED` | `institutions` | `corrective_action` | `syn.{region}.insp.v1` | `corrective_action_id`, `institution_id` | providers, intelligence | Corrective action evidence verified |
| `PVT.PROVIDER_REGISTERED` | `providers` | `provider` | `syn.{region}.pvt.v1` | `provider_id` | mdm | Proprietor organisation registered |
| `ADM.APPLICATION_SUBMITTED` | `providers` | `provider_application` | `syn.{region}.adm.v1` | `provider_application_id` | intelligence, comms | Provider application submitted (Licensing Agent) |
| `PVT.DECISION_MADE` | `providers` | `provider_application` | `syn.{region}.pvt.v1` | `provider_application_id`, `decision` | institutions, platform, comms | Four-eyes decision recorded |
| `PVT.APPROVAL_ISSUED` | `providers` | `approval` | `syn.{region}.pvt.v1` | `approval_id`, `institution_id`, `expires_on` | platform, institutions, certificates, comms | Approval certificate issued (tenant created) |
| `PVT.APPROVAL_RENEWED` | `providers` | `approval` | `syn.{region}.pvt.v1` | `approval_id`, `expires_on` | institutions, certificates | Approval renewed |
| `PVT.SANCTION_APPLIED` | `providers` | `sanction` | `syn.{region}.pvt.v1` | `sanction_id`, `institution_id`, `step` | learners, assessment, intelligence, comms | Sanction step takes effect (admissions/exam entries blocked) |
| `LRN.CREATED` | `learners` | `learner` | `syn.{region}.lrn.v1` | `learner_id`, `global_learner_id` | mdm, search, analytics, financing | Learner 360 created after matching |
| `LRN.UPDATED` | `learners` | `learner` | `syn.{region}.lrn.v1` | `learner_id`, `changed_fields` | search, analytics | Identity attributes changed (field names only) |
| `LRN.MERGED` | `learners` | `learner` | `syn.{region}.lrn.v1` | `learner_id`, `merged_into` | all_modules | Learner record became an alias |
| `LRN.VIEWED_SPECIAL` | `learners` | `learner` | `syn.{region}.lrn.v1` | `learner_id`, `viewer_user_id`, `purpose_code` | audit_monitoring | Special-category tab opened with purpose |
| `LRN.TRANSFERRED` | `learners` | `learner_transfer` | `syn.{region}.lrn.v1` | `learner_transfer_id`, `learner_id`, `to_institution_id` | attendance, finance, safeguarding, success, lms, comms | Transfer completed |
| `LRN.LEFT` | `learners` | `enrolment` | `syn.{region}.lrn.v1` | `enrolment_id`, `learner_id`, `destination_known` | learners, analytics, lms, comms | Leaver recorded (unknown destination at compulsory age → CME referral) |
| `ENR.STARTED` | `learners` | `enrolment` | `syn.{region}.enr.v1` | `enrolment_id`, `learner_id`, `institution_id` | academic, timetable, finance, curriculum, lms, financing, analytics | Enrolment became active |
| `ENR.ENDED` | `learners` | `enrolment` | `syn.{region}.enr.v1` | `enrolment_id`, `status` | academic, finance, lms, financing, analytics | Enrolment ended |
| `FAM.GUARDIAN_CREATED` | `families` | `guardian` | `syn.{region}.fam.v1` | `guardian_id` | comms, search | Guardian master created |
| `FAM.CONSENT_CHANGED` | `families` | `consent_record` | `syn.{region}.fam.v1` | `consent_record_id`, `learner_id`, `consent_type`, `decision` | comms, operations, lms, records | Consent given |
| `STF.CREATED` | `people` | `staff` | `syn.{region}.stf.v1` | `staff_id` | search, analytics | Staff 360 created |
| `STF.LEFT` | `people` | `staff` | `syn.{region}.stf.v1` | `staff_id` | iam, curriculum, comms | Staff member left all posts |
| `STF.POST_STARTED` | `people` | `staff_post` | `syn.{region}.stf.v1` | `staff_post_id`, `staff_id`, `institution_id` | iam, comms, analytics | Post started |
| `STF.POST_ENDED` | `people` | `staff_post` | `syn.{region}.stf.v1` | `staff_post_id`, `staff_id` | iam, curriculum, comms | Post ended (G9 handover check) |
| `STF.AUTHORISATION_CHANGED` | `people` | `staff_qualification` | `syn.{region}.stf.v1` | `staff_qualification_id`, `staff_id` | curriculum, timetable | Authorisation added |
| `STF.ABSENCE_RECORDED` | `people` | `staff_absence` | `syn.{region}.stf.v1` | `staff_absence_id`, `staff_id`, `starts_at`, `ends_at` | timetable, curriculum, intelligence | Staff absence recorded (cover flow |
| `STF.TRAINING_COMPLETED` | `people` | `training_completion` | `syn.{region}.stf.v1` | `training_completion_id`, `staff_id`, `passed` | learners, analytics | Statutory training completed |
| `PAY.RUN_APPROVED` | `people` | `payroll_run` | `syn.{region}.pay.v1` | `payroll_run_id` | finance | Pay run approved by two people |
| `ACA.CLASS_ACTIVATED` | `academic` | `class_group` | `syn.{region}.aca.v1` | `class_group_id`, `institution_id` | curriculum, lms, timetable, governance | Class activated for the session |
| `ACA.SUBJECT_PLAN_PUBLISHED` | `academic` | `class_subject_plan` | `syn.{region}.aca.v1` | `class_subject_plan_id`, `class_group_id` | lms, curriculum, timetable | Class subject plan published (course spaces created) |
| `ACA.COURSE_REGISTERED` | `academic` | `course_registration` | `syn.{region}.aca.v1` | `course_registration_id`, `learner_id`, `course_section_id` | lms, finance | Course registration approved |
| `CUR.APPROVED` | `curriculum` | `curriculum_version` | `syn.{region}.cur.v1` | `curriculum_version_id` | comms | Curriculum version approved |
| `CUR.PUBLISHED` | `curriculum` | `curriculum_version` | `syn.{region}.cur.v1` | `curriculum_version_id`, `curriculum_id`, `effective_from` | curriculum, lms, institutions, analytics | Version published (adoption resolved |
| `CUR.WITHDRAWN` | `curriculum` | `curriculum_version` | `syn.{region}.cur.v1` | `curriculum_version_id` | curriculum, analytics | Version withdrawn |
| `CUR.ADOPTION_RESOLVED` | `curriculum` | `curriculum_adoption` | `syn.{region}.cur.v1` | `curriculum_adoption_id`, `institution_id`, `version_id` | academic, analytics | Applicable version stamped for an institution and level |
| `CUR.ASSIGNMENT_CHANGED` | `academic` | `teaching_assignment` | `syn.{region}.cur.v1` | `teaching_assignment_id`, `staff_id` | curriculum, lms, timetable, comms | Teacher of record or co-teacher changed (G2/G3) |
| `CUR.LESSON_DELIVERED` | `curriculum` | `delivery_log` | `syn.{region}.cur.v1` | `delivery_log_id`, `teaching_assignment_id` | analytics | Lesson delivery logged (G6) |
| `CUR.GAP_OPENED` | `curriculum` | `coverage_gap` | `syn.{region}.cur.v1` | `coverage_gap_id`, `rule`, `severity`, `institution_id` | intelligence, comms, analytics | Coverage invariant breached |
| `CUR.GAP_ESCALATED` | `curriculum` | `coverage_gap` | `syn.{region}.cur.v1` | `coverage_gap_id`, `escalation_level` | comms, intelligence | Gap passed its due date |
| `CUR.GAP_CLOSED` | `curriculum` | `coverage_gap` | `syn.{region}.cur.v1` | `coverage_gap_id` | analytics, intelligence | Gap closed by a person |
| `TT.PUBLISHED` | `timetable` | `timetable` | `syn.{region}.tt.v1` | `timetable_id`, `institution_id` | attendance, curriculum, lms, comms | Timetable version published |
| `TT.COVER_ASSIGNED` | `timetable` | `cover_assignment` | `syn.{region}.tt.v1` | `cover_assignment_id`, `lesson_occurrence_id`, `is_qualified` | comms, curriculum | Cover confirmed |
| `ATT.REGISTER_SUBMITTED` | `attendance` | `attendance_register` | `syn.{region}.att.v1` | `attendance_register_id`, `class_group_id`, `session_date` | intelligence, comms, analytics | Register submitted (live tiles |
| `ATT.REGISTER_MISSING` | `attendance` | `attendance_register` | `syn.{region}.att.v1` | `attendance_register_id`, `class_group_id` | intelligence, comms | Register not taken by deadline (Register Agent) |
| `ATT.ABSENCE_REPORTED` | `attendance` | `absence_report` | `syn.{region}.att.v1` | `absence_report_id`, `learner_id`, `from_date` | attendance, comms | Parent reported an absence |
| `ATT.EVACUATION_STARTED` | `attendance` | `evacuation_event` | `syn.{region}.att.v1` | `evacuation_event_id`, `campus_id` | comms | Evacuation or drill started |
| `ASM.ASSESSMENT_CREATED` | `assessment` | `assessment` | `syn.{region}.asm.v1` | `assessment_id` | curriculum | Assessment created (G7 objective links) |
| `ASM.RESULTS_LOCKED` | `assessment` | `assessment` | `syn.{region}.asm.v1` | `assessment_id` | certificates, analytics, intelligence | Results approved and locked |
| `EXAM.RESULTS_COMMITTED` | `assessment` | `exam_result` | `syn.{region}.exam.v1` | `series_id`, `results_count` | certificates, intelligence, analytics | Results committed immutably |
| `CERT.ISSUED` | `certificates` | `certificate` | `syn.{region}.cert.v1` | `certificate_id`, `learner_id`, `institution_id` | learners, integration, analytics | Certificate signed and issued |
| `CERT.REVOKED` | `certificates` | `certificate` | `syn.{region}.cert.v1` | `certificate_id` | learners, integration, analytics | Certificate revoked (two approvers) |
| `CERT.REISSUED` | `certificates` | `certificate` | `syn.{region}.cert.v1` | `certificate_id`, `supersedes_id` | learners, integration, analytics | Reissue issued; original superseded at the same moment |
| `CERT.CORRECTED` | `certificates` | `certificate` | `syn.{region}.cert.v1` | `certificate_id`, `supersedes_id` | learners, integration | Correction issued |
| `CERT.SUSPENDED` | `certificates` | `certificate` | `syn.{region}.cert.v1` | `certificate_id` | integration | Certificate suspended |
| `CERT.VERIFIED` | `certificates` | `verification` | `syn.{region}.cert.v1` | `verification_id`, `result` | analytics, learners | Verification answered |
| `CERT.VERIFY_FAILED` | `certificates` | `verification` | `syn.{region}.cert.v1` | `verification_id` | intelligence | Verification failed (integrity patterns) |
| `CER.REISSUE_REQUESTED` | `certificates` | `reissue_case` | `syn.{region}.cer.v1` | `reissue_case_id`, `reason` | intelligence, comms | Reissue application submitted |
| `CER.REISSUE_DECIDED` | `certificates` | `reissue_case` | `syn.{region}.cer.v1` | `reissue_case_id`, `status` | comms | Reissue approved or rejected |
| `BEH.POLICY_PUBLISHED` | `success` | `behaviour_policy` | `syn.{region}.beh.v1` | `behaviour_policy_id`, `institution_id` | analytics | Behaviour policy version published |
| `BEH.EVENT_RECORDED` | `success` | `behaviour_event` | `syn.{region}.beh.v1` | `behaviour_event_id`, `learner_id`, `polarity` | intelligence, analytics, comms | Behaviour logged (intelligence events evaluated) |
| `BEH.DETENTION_SET` | `success` | `detention` | `syn.{region}.beh.v1` | `detention_id`, `learner_id` | comms | Detention created (parent notified) |
| `BEH.ONCALL_RAISED` | `success` | `oncall_request` | `syn.{region}.beh.v1` | `oncall_request_id`, `reason` | comms | On-call request raised |
| `SAF.CONCERN_RAISED` | `safeguarding` | `safeguarding_concern` | `syn.{region}.saf.v1` | `safeguarding_concern_id` | comms | Concern recorded — notification carries no detail |
| `SAF.CASE_UPDATED` | `safeguarding` | `safeguarding_case` | `syn.{region}.saf.v1` | `safeguarding_case_id` | comms | Case updated — no detail |
| `SAF.CASE_VIEWED` | `safeguarding` | `safeguarding_case` | `syn.{region}.saf.v1` | `safeguarding_case_id`, `viewer_user_id` | audit_monitoring | Case viewed |
| `SAF.STAFF_CASE_OPENED` | `safeguarding` | `staff_case` | `syn.{region}.saf.v1` | `staff_case_id` | comms | Staff case opened — designated officer notified without detail |
| `SEN.ADJUSTMENT_CHANGED` | `success` | `adjustment` | `syn.{region}.sen.v1` | `adjustment_id`, `learner_id` | timetable, assessment, lms, academic | Authorised adjustment changed (rooms |
| `WEL.CONCERN_REPORTED` | `success` | `wellbeing_concern` | `syn.{region}.wel.v1` | `wellbeing_concern_id`, `keyword_alert` | comms | Wellbeing concern reported |
| `INT.INTERVENTION_CLOSED` | `intelligence` | `intervention` | `syn.{region}.int.v1` | `intervention_id`, `status` | analytics, intelligence | Intervention closed with outcome |
| `LMS.SPACE_CREATED` | `lms` | `course_space` | `syn.{region}.lms.v1` | `course_space_id` | comms | Course space auto-created |
| `LMS.ASSIGNMENT_PUBLISHED` | `lms` | `assignment` | `syn.{region}.lms.v1` | `assignment_id`, `course_space_id`, `due_at` | comms, analytics | Assignment published to learners and parents |
| `LMS.SUBMITTED` | `lms` | `submission` | `syn.{region}.lms.v1` | `submission_id`, `assignment_id`, `is_late` | analytics, intelligence | Submission received (receipt hash issued) |
| `COM.MESSAGE_SENT` | `comms` | `message` | `syn.{region}.com.v1` | `message_id`, `channel` | analytics, records | Message sent |
| `COM.MESSAGE_RECEIVED` | `comms` | `message` | `syn.{region}.com.v1` | `message_id`, `channel`, `conversation_id` | comms, intelligence | Inbound message received and matched |
| `FRM.SUBMITTED` | `forms` | `form_response` | `syn.{region}.frm.v1` | `form_response_id`, `form_id` | governance, records, finance | Form submitted |
| `DOC.INGESTED` | `records` | `document` | `syn.{region}.doc.v1` | `document_id`, `category_id` | search, intelligence | Document stored (search indexed unless special category) |
| `DOC.LINKED` | `records` | `document_link` | `syn.{region}.doc.v1` | `document_link_id`, `record_kind`, `record_id` | search | Document linked to a record |
| `BIL.RUN_ISSUED` | `finance` | `billing_run` | `syn.{region}.bil.v1` | `billing_run_id`, `invoices` | comms, analytics | Billing run issued |
| `BIL.INVOICE_ISSUED` | `finance` | `invoice` | `syn.{region}.bil.v1` | `invoice_id`, `account_id` | comms, records | Invoice issued |
| `BIL.INVOICE_OVERDUE` | `finance` | `invoice` | `syn.{region}.bil.v1` | `invoice_id` | comms, intelligence | Invoice overdue (Fee Agent; never restricts education) |
| `PMT.RECEIVED` | `finance` | `payment` | `syn.{region}.pmt.v1` | `payment_id`, `method` | finance, comms, analytics | Payment confirmed |
| `PMT.ALLOCATED` | `finance` | `payment_allocation` | `syn.{region}.pmt.v1` | `payment_allocation_id`, `payment_id`, `invoice_id` | comms, analytics | Payment allocated to an invoice |
| `SUB.RATE_CARD_PUBLISHED` | `financing` | `sdaf_rate_card` | `syn.{region}.sub.v1` | `sdaf_rate_card_id`, `effective_from` | comms, analytics | SDAF rate card published |
| `SUB.CENSUS_FROZEN` | `financing` | `census_snapshot` | `syn.{region}.sub.v1` | `census_snapshot_id`, `institution_id`, `billable` | financing, platform, analytics | Census frozen and hashed |
| `SUB.DEMAND_ISSUED` | `financing` | `sdaf_demand` | `syn.{region}.sub.v1` | `sdaf_demand_id`, `institution_id` | comms, analytics | Demand notice or assessment issued |
| `SUB.COLLECTION_POSTED` | `financing` | `sdaf_collection` | `syn.{region}.sub.v1` | `sdaf_collection_id`, `demand_id` | analytics, comms | State collection posted idempotently |
| `SUB.REMITTANCE_RECORDED` | `financing` | `remittance` | `syn.{region}.sub.v1` | `remittance_id` | platform, analytics | Remittance to SDIN recorded |
| `SUB.STATEMENT_SIGNED` | `financing` | `reconciliation_statement` | `syn.{region}.sub.v1` | `reconciliation_statement_id`, `status` | platform, analytics | Statement signed by state or operator |
| `SUB.SUBSCRIPTION_STATUS_CHANGED` | `platform` | `subscription` | `syn.{region}.sub.v1` | `subscription_id`, `tenant_id`, `status` | iam, comms | Subscription status changed (administrative restriction only) |
| `SUB.INVOICE_ISSUED` | `platform` | `subscription_invoice` | `syn.{region}.sub.v1` | `subscription_invoice_id`, `subscription_id` | comms | Operator invoice issued |
| `SUB.PAYMENT_RECEIVED` | `platform` | `subscription_payment` | `syn.{region}.sub.v1` | `subscription_payment_id`, `invoice_id` | platform, comms | Provider payment received (access restored) |
| `ALERT.RAISED` | `intelligence` | `alert` | `syn.{region}.alert.v1` | `alert_id`, `severity`, `subject_kind`, `subject_id` | comms, analytics | Alert raised (deduplicated) |
| `ALERT.ESCALATED` | `intelligence` | `alert` | `syn.{region}.alert.v1` | `alert_id`, `escalation_level` | comms | Alert escalated |
| `ALERT.RESOLVED` | `intelligence` | `alert` | `syn.{region}.alert.v1` | `alert_id` | analytics | Alert resolved |
| `ALERT.SNOOZED` | `intelligence` | `alert` | `syn.{region}.alert.v1` | `alert_id`, `snoozed_until` | comms | Alert snoozed from the briefing |
| `INV.OPENED` | `intelligence` | `investigation` | `syn.{region}.inv.v1` | `investigation_id` | comms | Investigation opened |
| `INV.ACTION_ADDED` | `intelligence` | `investigation` | `syn.{region}.inv.v1` | `investigation_id`, `stage` | comms | Investigation advanced |
| `INV.CLOSED` | `intelligence` | `investigation` | `syn.{region}.inv.v1` | `investigation_id` | analytics | Investigation closed with outcome |
| `AI.RECOMMENDATION_DECIDED` | `intelligence` | `recommendation` | `syn.{region}.ai.v1` | `recommendation_id`, `decision` | analytics, intelligence | Human decided a recommendation (model evaluation) |
| `AI.QUERY` | `intelligence` | `assistant_conversation` | `syn.{region}.ai.v1` | `assistant_conversation_id` | audit_monitoring | Assistant query (audited as a read) |
| `AGT.PAUSED` | `intelligence` | `agent` | `syn.{region}.agt.v1` | `agent_id`, `paused_by` | comms | Kill switch used (queued actions held) |
| `AGT.LEVEL_LOWERED` | `intelligence` | `agent` | `syn.{region}.agt.v1` | `agent_id`, `level` | comms | Error threshold breached (autonomy lowered one level) |
| `RPT.RETURN_SUBMITTED` | `reporting` | `return_submission` | `syn.{region}.rpt.v1` | `return_submission_id` | integration, analytics | Government return certified and submitted |
| `ADM.APPLICATION_RECEIVED` | `sectors` | `admission_application` | `syn.{region}.adm.v1` | `admission_application_id`, `institution_id` | comms, intelligence | Admission application received (Admissions Agent acknowledges) |
