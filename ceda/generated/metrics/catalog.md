# CEDA semantic-layer metric catalogue

Generated from `ceda/model/metrics.yaml`. Every indicator shown on a dashboard, return, briefing or assistant answer is defined here exactly once (MFS §7.3, FR-RPT-02, FR-RPT-04). Aggregates leaving the institution scope apply small-number suppression (cells < 10, FR-CMD-108).

## Access

| ID | Metric | Definition / formula | Grain | Refresh | Direction | Sources | Pages |
|---|---|---|---|---|---|---|---|
| `ENR-COUNT` | Learners enrolled | count of active primary enrolments | day × institution × level × sex | daily | target_band | `agg_enrolment_daily`, `enrolment` | CMD-101, CMD-02, CMD-03, CMD-04, CMD-05, CMD-06, CMD-07, ATT-02 |
| `ENR-GER` | Gross enrolment ratio | enrolled at level ÷ population of official age for level (population projections) | year × state/LGA × level × sex | termly | higher_is_better | `agg_enrolment_daily` | CMD-02, CMD-03, CMD-01 |
| `ENR-NER` | Net enrolment ratio | enrolled of official age at level ÷ population of official age | year × state/LGA × level × sex | termly | higher_is_better | `agg_enrolment_daily`, `dim_learner` | CMD-02, CMD-03 |
| `ENR-OOSC` | Out-of-school estimate | population of compulsory age − enrolled of compulsory age | year × LGA | termly | lower_is_better | `agg_enrolment_daily`, `cme_referral` | CMD-03, CMD-04 |
| `ENR-TRANSITION` | Transition rate (primary → JSS → SSS → tertiary) | learners enrolled at next stage in session t+1 ÷ learners completing stage in session t | session × LGA × stage | termly | higher_is_better | `fact_enrolment_census`, `enrolment` | CMD-02, CMD-03 |
| `INS-LIVE` | Institutions live | institutions with onboarding_status = live ÷ institutions on the register | day × LGA × ownership | daily | higher_is_better | `dim_institution`, `institution`, `onboarding_check` | CMD-101, CMD-103 |

## Participation

| ID | Metric | Definition / formula | Grain | Refresh | Direction | Sources | Pages |
|---|---|---|---|---|---|---|---|
| `ATT-RATE` | Learner attendance rate | present sessions (incl. late) ÷ possible sessions | day × class/institution/LGA/state | live_15min | higher_is_better | `live_kpi`, `agg_attendance_daily`, `attendance_mark` | CMD-101, CMD-02, CMD-03, CMD-04, CMD-05, CMD-06, ATT-02, CMD-07 |
| `ATT-PERSISTENT` | Persistent absence rate | learners with term attendance < 90% ÷ learners | term × institution × level | daily | lower_is_better | `agg_learner_attendance_term` | ATT-02, CMD-06, CMD-04 |
| `ATT-SEVERE` | Severe absence rate | learners with term attendance < 50% ÷ learners | term × institution × level | daily | lower_is_better | `agg_learner_attendance_term` | ATT-02, CMD-06 |
| `ATT-DROPOUT` | Dropout rate | enrolments ended with leaving_reason dropped_out or unknown destination at compulsory age ÷ enrolled | term × institution × level × sex | daily | lower_is_better | `agg_enrolment_daily`, `enrolment` | CMD-03, CMD-06 |
| `REG-COMPLIANCE` | Register compliance | registers submitted by deadline ÷ registers due | day × teacher/institution/LGA | live_15min | higher_is_better | `agg_attendance_daily`, `attendance_register` | ATT-102, CMD-04, CMD-101 |
| `STF-PRESENCE` | Teachers present today | staff present ÷ staff expected | day × institution/LGA/state | live_15min | higher_is_better | `live_kpi`, `fact_staff_presence` | CMD-101, CMD-04, CMD-06 |

## Teaching

| ID | Metric | Definition / formula | Grain | Refresh | Direction | Sources | Pages |
|---|---|---|---|---|---|---|---|
| `CUR-COVERAGE` | Curriculum coverage (qualified teacher of record) | mandatory class-subjects with a qualified teacher of record ÷ mandatory class-subjects | day × class/institution/LGA/state × subject × level | daily | higher_is_better | `fact_class_subject_coverage` | CUR-101, CMD-101, CMD-03, CUR-07 |
| `CUR-HOURS` | Teaching-hours coverage | Σ min(1, delivered hours ÷ pro-rata required hours to date) averaged over class-subjects | day × class/institution × subject | daily | higher_is_better | `fact_class_subject_coverage`, `fact_curriculum_delivery` | CUR-101, CUR-06 |
| `CUR-COMPLIANCE` | Curriculum compliance score | 0.20·subject coverage + 0.25·teaching hours + 0.25·objectives delivered + 0.15·assessment coverage + 0.15·qualified staff (authority-configurable, versioned); bands ≥95 compliant, 80–94.9 partial, <80 non-compliant, insufficient data = not assessed | day × institution | daily | higher_is_better | `fact_compliance_score`, `fact_class_subject_coverage` | CUR-06, CUR-07, INS-02, CMD-06 |
| `CUR-GAPS-OPEN` | Open coverage gaps by severity and age | count of open gaps; age = today − opened date | day × institution/LGA × rule × severity | daily | lower_is_better | `fact_coverage_gap` | CUR-101, CUR-103, CMD-101, CMD-04 |
| `STF-QUALIFIED-RATE` | Qualified teacher rate | teachers with valid qualification and TRCN registration ÷ teachers | day × institution/LGA × subject | daily | higher_is_better | `dim_staff`, `staff_qualification` | STF-08, CMD-03, CMD-02 |
| `PTR` | Teacher–learner ratio | enrolled learners ÷ teaching FTE (by subject using class-subject assignments) | day × institution/LGA × subject × level | daily | target_band | `agg_enrolment_daily`, `staff_post`, `teaching_assignment` | CMD-101, CMD-02, ACA-102, STF-10 |
| `TCH-DEMAND-SUPPLY` | Teacher demand vs supply | demand = Σ curriculum hours × classes ÷ max load; supply = authorised teaching capacity; gap = demand − supply | term × LGA × subject × level | daily | lower_is_better | `fact_class_subject_coverage`, `staff_qualification`, `staff_post` | STF-10, CMD-13, CMD-14 |
| `CPD-COMPLIANCE` | CPD and statutory training compliance | adults with valid mandatory training ÷ adults required | day × institution/LGA/state × course | daily | higher_is_better | `training_completion`, `cpd_record` | STF-101, STF-07 |

## Learning

| ID | Metric | Definition / formula | Grain | Refresh | Direction | Sources | Pages |
|---|---|---|---|---|---|---|---|
| `CA-AVERAGE` | Continuous assessment average | mean score % of locked CA assessments | term × class/institution × subject | termly | higher_is_better | `fact_assessment_result` | CMD-06, CMD-03 |
| `EXAM-5CREDITS` | Exam pass rate (5 credits incl. English and Mathematics) | candidates with ≥ 5 credits including English and Mathematics ÷ candidates sitting | series × institution/LGA/state × sex | per_series | higher_is_better | `fact_exam_result` | CMD-101, CMD-02, CMD-03, CMD-06, CMD-102 |
| `PROGRESS-TARGET` | Progress against target | learners at or above target grade ÷ learners with targets | term × class/institution × subject | termly | higher_is_better | `fact_assessment_result`, `target_grade` | ASM-01, CMD-06 |
| `LMS-COMPLETION` | Assignment completion rate | submissions on time or late ÷ expected submissions | week × class/institution/LGA | daily | higher_is_better | `fact_lms_activity` | LMS-108, CMD-101 |
| `LMS-ADOPTION` | Digital adoption | active course spaces; assignments set per teacher per month; teachers setting ≥ 1 online assignment per month ÷ teachers | month × institution/LGA | daily | higher_is_better | `fact_lms_activity`, `course_space` | LMS-108, CMD-101 |
| `DIGITAL-SKILLS` | Digital skills attainment | distribution of learners and teachers by level (1–5) per strand | term × institution/LGA × strand | termly | higher_is_better | `fact_digital_skill` | LMS-108 |

## Wellbeing and safety

| ID | Metric | Definition / formula | Grain | Refresh | Direction | Sources | Pages |
|---|---|---|---|---|---|---|---|
| `SAF-CONCERNS` | Safeguarding concerns (counts only) | count of concerns by category; groups < 10 suppressed above institution | day × institution/LGA × category | daily | target_band | `agg_wellbeing_safeguarding_count` | SAF-103, CMD-101 |
| `BEH-RATIO` | Positive-to-negative behaviour ratio | positive events ÷ negative events | week × institution/LGA × type | daily | higher_is_better | `fact_behaviour` | BEH-02, CMD-101 |
| `SEND-COVERAGE` | SEND provision coverage | learners on the SEND register with allocated provision ÷ learners on the register | term × institution/LGA | daily | higher_is_better | `agg_wellbeing_safeguarding_count` | SEN-04, CMD-101 |
| `FACILITY-INCIDENTS` | Facility safety incidents | count by severity | month × institution/LGA | daily | lower_is_better | `facility_incident` | OPS-03, CMD-101 |

## Infrastructure

| ID | Metric | Definition / formula | Grain | Refresh | Direction | Sources | Pages |
|---|---|---|---|---|---|---|---|
| `INFRA-CLASSROOM` | Learners per classroom | enrolled ÷ classrooms in use | term × institution/LGA | termly | lower_is_better | `fact_infrastructure` | CMD-101, CMD-13, OPS-01 |
| `INFRA-TEXTBOOK` | Textbook-to-learner ratio | textbooks issued for subject and level ÷ learners at level | term × institution/LGA × subject × level | termly | higher_is_better | `fact_infrastructure`, `resource_issue` | OPS-08, CMD-13 |
| `INFRA-BASICS` | Water | share of institutions with each facility; toilets per learner by sex | term × LGA | termly | higher_is_better | `fact_infrastructure` | CMD-101, CMD-03 |

## Finance

| ID | Metric | Definition / formula | Grain | Refresh | Direction | Sources | Pages |
|---|---|---|---|---|---|---|---|
| `CAPITATION-RECON` | Capitation received vs due | capitation received ÷ due | tranche × institution/LGA | monthly | higher_is_better | `government_funding_receipt` | BIL-08, CMD-101 |
| `FEE-COLLECTION` | Fee collection rate (private) | collected ÷ invoiced | month × institution | daily | higher_is_better | `fact_finance` | BIL-05, CMD-06 |
| `BUDGET-EXECUTION` | Budget execution | actual ÷ budget by cost centre | month × institution × cost centre | daily | target_band | `fact_finance`, `budget` | FIN-02 |
| `FEEDING-RECON` | School feeding reconciliation | meals served ÷ learners present | day × institution | daily | target_band | `meal_service`, `agg_attendance_daily` | OPS-07, CMD-101 |
| `SDAF-COLLECTION` | SDAF billed | collection rate = collected ÷ (billed − exempted); outstanding = billed − exempted − collected; remittance variance = collected − remitted (aged) | billing period × institution/LGA/institution type | daily | higher_is_better | `fact_sdaf` | SUB-105, SUB-103, SUB-104 |
| `FCL-OUTSTANDING-RATE` | Incoming learners with outstanding obligations | clearance checks with result outstanding ÷ clearance checks | month × LGA × institution type | daily | lower_is_better | `clearance_check` | FCL-01, FCL-02, FCL-03 |
| `FCL-DISPUTE-UPHELD` | Obligation disputes upheld | disputes upheld or partly upheld ÷ disputes resolved, by creditor institution (unsupported claims) | term × creditor institution | daily | lower_is_better | `obligation_dispute` | FCL-03 |
| `FCL-NATIONAL-COVERAGE` | National clearance coverage | states that answered ÷ 37 (36 states and the FCT) per clearance check; states on the network ÷ 37 | day × requesting state | daily | higher_is_better | `clearance_exchange_query`, `exchange_peer` | FCL-04 |

## Integrity and data

| ID | Metric | Definition / formula | Grain | Refresh | Direction | Sources | Pages |
|---|---|---|---|---|---|---|---|
| `DQI` | Data Quality Index | 0.30·Completeness + 0.20·Uniqueness + 0.20·Validity + 0.15·Timeliness + 0.10·Consistency + 0.05·Verification (0–100) | day × institution/LGA/state | daily | higher_is_better | `fact_data_quality` | CMD-16, CMD-101, INS-02 |
| `DUP-RATE` | Duplicate learner rate | open probable duplicates ÷ learners | day × institution/LGA | daily | lower_is_better | `match_review`, `fact_data_quality` | CMD-16, ADM-17 |
| `CERT-INTEGRITY` | Certificate verifications and integrity alerts | verifications by result; open integrity alerts | day × state/issuer | daily | lower_is_better | `fact_certificate_event`, `alert` | CMD-15, CMD-101 |
| `DIGITISATION` | Digitisation progress and quality | pages captured, indexed and searchable; key-field accuracy; hours scan-to-searchable | day × hub/LGA | daily | higher_is_better | `fact_digitisation` | DOC-101, CMD-101 |
| `DATA-FRESHNESS` | Data freshness | institutions with stale datasets ÷ institutions live | day × LGA × dataset | live_15min | lower_is_better | `dataset_freshness` | CMD-101, CMD-103 |

## Engagement

| ID | Metric | Definition / formula | Grain | Refresh | Direction | Sources | Pages |
|---|---|---|---|---|---|---|---|
| `PARENT-APP` | Parent app adoption | guardians with an active parent account ÷ guardians | week × institution/LGA | weekly | higher_is_better | `app_user`, `guardian` | CMD-101 |
| `MSG-DELIVERY` | Messages delivered | delivered ÷ sent; read ÷ delivered; median first response minutes; Σ cost | day × institution × channel | daily | higher_is_better | `fact_message` | COM-02, COM-103, CMD-101 |
| `PTM-ATTENDANCE` | Parents' meeting attendance | attended bookings ÷ learners invited | event × institution | weekly | higher_is_better | `meeting_booking` | PTM-101, CMD-101 |

## Composite

| ID | Metric | Definition / formula | Grain | Refresh | Direction | Sources | Pages |
|---|---|---|---|---|---|---|---|
| `HEALTH-INDEX` | Institution health index | Σ wᵢ·sᵢ ÷ Σ wᵢ over available indicators (0–100, normalised to policy targets); missing indicators excluded and weights renormalised (tile shows 'partial'); bands ≥80 strong, 65–79 adequate, 50–64 concern, <50 critical | day × institution (rolled up by enrolment-weighted mean) | daily | higher_is_better | `fact_health_index` | INS-05, CMD-06, CMD-101, CMD-02, CMD-03, CMD-04, CMD-05, CMD-102, CMD-11, CMD-12 |
| `INST-PERFORMANCE` | Institution performance table | per institution in scope: level, ownership, enrolment, attendance, health index, curriculum coverage, exam results, PTR, data freshness — sortable, filterable, saved views, export | day × institution | daily | target_band | `agg_metric`, `dim_institution` | CMD-101, CMD-102, CMD-11 |
| `GLOBAL-INDICATORS` | Global and national indicators (from state aggregates only) | country and global aggregates computed from in-country state aggregates; each labelled verified, calculated or estimated | year × country/state | termly | target_band | `agg_metric` | CMD-01, CMD-02 |
| `NETWORK-SUMMARY` | Network dashboard summary | member-institution aggregates of ENR-COUNT, ATT-RATE, HEALTH-INDEX, EXAM-5CREDITS, FEE-COLLECTION | day × network | daily | target_band | `agg_metric` | CMD-05 |
| `LGA-TODAY` | LGA today — attendance | live attendance, open cover gaps (G8), critical maintenance, registers missing | day × LGA × institution | live_15min | target_band | `live_kpi`, `coverage_gap`, `maintenance_request` | CMD-04 |

## Human resources

| ID | Metric | Definition / formula | Grain | Refresh | Direction | Sources | Pages |
|---|---|---|---|---|---|---|---|
| `HR-ESTAB-FILL` | Establishment fill rate | approved positions filled by an active employment record ÷ approved positions | day × institution/LGA/employer × cadre | daily | higher_is_better | `position`, `employment_record` | HRM-10, HRM-01 |
| `HR-VACANCIES` | Vacant positions by subject | approved funded positions without an active employment record, by subject specialism | day × institution/LGA × subject | daily | lower_is_better | `position`, `employment_record` | HRM-10, HRM-01, STF-10 |
| `HR-ATTRITION` | Staff attrition | separations in the last 12 months ÷ average active posts | month × employer/LGA × cadre × separation kind | daily | lower_is_better | `separation`, `employment_record` | HRM-10 |
| `HR-RETIRE-12M` | Retirements due in 12 months | active employment records with retirement_due_on within 12 months | month × employer/LGA × subject | daily | target_band | `employment_record` | HRM-10, HRM-02 |
| `HR-LEAVE-LIABILITY` | Leave liability | Σ (entitled + carried over − taken) annual-leave days across staff | leave year × employer × institution | daily | target_band | `leave_balance` | HRM-10, HRM-04 |
| `HR-INTEGRITY-OPEN` | Open payroll integrity flags | open flags by kind; pay held by decision | day × employer × flag kind | daily | lower_is_better | `hr_integrity_flag` | HRM-08, HRM-10 |

## Security training

| ID | Metric | Definition / formula | Grain | Refresh | Direction | Sources | Pages |
|---|---|---|---|---|---|---|---|
| `STI-INTAKE-FILL` | Course intake fill rate | trainees on intake ÷ intake capacity | intake × course × institution × agency | daily | higher_is_better | `trainee_record`, `security_course_intake` | STI-03, STI-04 |
| `STI-PASS-OUT-RATE` | Trainee pass-out rate | trainees passed out or commissioned ÷ trainees with a final outcome | intake × course × institution × agency | daily | higher_is_better | `trainee_record` | STI-02, STI-04 |

## Regulation

| ID | Metric | Definition / formula | Grain | Refresh | Direction | Sources | Pages |
|---|---|---|---|---|---|---|---|
| `REG-PROFILE-COMPLETE` | Institutions with a complete regulatory profile | institutions with a supervising body, an accreditor where required and an examination body for examined levels ÷ institutions | registry × category × ownership | daily | higher_is_better | `institution_regulation`, `institution` | REG-02, FED-01 |

