# CEDA data dictionary

Generated from the CEDA model (SYN-CEDA-001 v1.5.0). Do not edit by hand.

| Domain | Code | Module (Django app) | Default zone | Entities |
|---|---|---|---|---|
| [Platform, tenancy and operator commercial records](01_platform.md) | PLT | `platform` | platform | 17 |
| [Governance hierarchy, configuration, reference data, policy and workflow](02_governance.md) | GOV | `governance` | registry | 18 |
| [Identity, access, permissions and service identities](03_iam.md) | IAM | `iam` | registry | 13 |
| [Master data management, identity matching and data quality](04_mdm.md) | MDM | `mdm` | registry | 9 |
| [Institution 360, state institution register, licensing, inspection and compliance](05_institutions.md) | INS | `institutions` | registry | 17 |
| [Private education provider admission and regulation](06_providers.md) | PVT | `providers` | registry | 13 |
| [Learner 360, state enrolment register, transfer and Education Passport](07_learners.md) | LRN | `learners` | registry | 9 |
| [Family 360, guardians, contacts, contact restrictions and consent](08_families.md) | FAM | `families` | registry | 7 |
| [Staff / Teacher 360, authorisations, HR, cover, recruitment, CPD, training and payroll](09_staff.md) | STF | `people` | registry | 16 |
| [Academic structure — calendars, subjects, programmes, qualifications, classes, departments and courses](10_academic.md) | ACA | `academic` | registry | 16 |
| [Curriculum 360, adoption, teaching chain evidence and zero-gap coverage assurance](11_curriculum.md) | CUR | `curriculum` | registry | 9 |
| [Timetable, lesson occurrences, cover rota, duties and room bookings](12_timetable.md) | TIM | `timetable` | ops | 7 |
| [Attendance registers, absence reporting and follow-up, staff sign-in, visitors and evacuation roll call](13_attendance.md) | ATT | `attendance` | ops | 8 |
| [Assessment, grading, moderation, targets, report cards, examinations, results, GPA and transcripts](14_assessment.md) | ASM | `assessment` | ops | 20 |
| [Certificate 360 and the state certificate registry — eligibility, issuance, signing, verification, reissue and anti-fraud](15_certificates.md) | CER | `certificates` | registry | 17 |
| [Behaviour, rewards, seating plans and influences, intelligence events, detentions, on-call and on-report](16_behaviour.md) | BEH | `success` | ops | 20 |
| [Safeguarding — concerns, cases, chronologies, referrals, secure sharing, allegations about adults and community reporting](17_safeguarding.md) | SAF | `safeguarding` | vault | 12 |
| [SEND and inclusion, gifted and talented, wellbeing, interventions and personal learning plans](18_inclusion_wellbeing.md) | SEN | `success` | vault | 16 |
| [Sector extensions — early years, post-16 and careers, TVET, higher education and medical/health education](19_sectors.md) | SEC | `sectors` | ops | 29 |
| [Online coursework — course spaces, content, assignments, submissions, marking, quizzes, live classes and digital skills](20_lms.md) | LMS | `lms` | ops | 19 |
| [Communication — messaging gateway, WhatsApp and Zenzap, templates, conversations, broadcasts, notifications, announcements and consent requests](21_comms.md) | COM | `comms` | ops | 14 |
| [Billing, payments, funding, ledger, budgets, procurement and suppliers](22_finance.md) | FIN | `finance` | ops | 24 |
| [Programme financing — Student Digital Access Fee (SDAF) rates, census, payers, exemptions, demand, collection, remittance and reconciliation](23_financing.md) | SUB | `financing` | registry | 18 |
| [Operations — estate, rooms, assets, maintenance, safety incidents, capital plan, transport, clubs, trips, meals, library and learning resources](24_operations.md) | OPS | `operations` | ops | 21 |
| [Forms and Daybook engine and parents' meetings](25_forms_meetings.md) | FRM | `forms` | ops | 4 |
| [Records and archives — document store, file plan, retention, legal holds, disposal and the digitisation pipeline](26_records.md) | DOC | `records` | records | 14 |
| [Intelligence and automation — alerts, investigations, improvement, recommendations, early warning, model register, agents, assistant and planning](27_intelligence.md) | INT | `intelligence` | ops | 24 |
| [Reporting, semantic layer registry, government returns, scheduled reports and lineage](28_reporting.md) | RPT | `reporting` | registry | 6 |
| [Integration, data exchange, imports, webhooks, idempotency and data-subject requests](29_integration.md) | INTG | `integration` | registry | 16 |
| [Audit trail, chain anchors and the transactional outbox](30_audit.md) | AUD | `core` | ops | 20 |
| [Enterprise Human Resource Management Suite — establishment, employment, postings, leave, promotion, employee relations, separation, payroll elements and payroll integrity](31_hrms.md) | HRM | `hr` | registry | 18 |
| [Fee-clearance due diligence — learner obligations register, clearance checks, admission decisions and disputes](32_fee_clearance.md) | FCL | `clearance` | registry | 5 |
| [Education and training institutions of the security agencies — agency structures, ranks, courses, intakes](33_security_training.md) | STI | `security_training` | registry | 8 |
| [Analytics warehouse — conformed dimensions, facts, aggregates, live KPI read model and feature store](90_warehouse.md) | DW | `analytics` | dw | 38 |
