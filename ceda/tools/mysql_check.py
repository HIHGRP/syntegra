#!/usr/bin/env python3
"""Load the generated CEDA DDL into a real MySQL 9.7 server and run conformance smoke tests.

Implements NFR-PLAT-109 for the schema itself: every zone file must load into MySQL 9.7 without error,
and the database-level guarantees CEDA relies on must actually hold.

Usage:
  MYSQL_CMD="mysql -h127.0.0.1 -P3306 -uroot -pceda" python3 ceda/tools/mysql_check.py
  MYSQL_CMD="docker exec -i mysql97 mysql -uroot -pceda" python3 ceda/tools/mysql_check.py

The command must accept SQL on stdin and a database name as its last argument.
"""
from __future__ import annotations

import os
import shlex
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DDL = ROOT / "generated" / "mysql"
CMD = shlex.split(os.environ.get("MYSQL_CMD", "mysql -h127.0.0.1 -P3306 -uroot -pceda"))

ZONES = [  # (file, schema)
    ("00_platform.sql", "ceda_platform"),
    ("10_registry.sql", "ceda_registry"),
    ("15_registry_seed_code_lists.sql", "ceda_registry"),
    ("20_ops.sql", "ceda_ops"),
    ("30_vault.sql", "ceda_vault"),
    ("40_records.sql", "ceda_records"),
    ("90_dw.sql", "ceda_dw"),
]

T1 = "UUID_TO_BIN('00000000-0000-7000-8000-000000000001')"   # state tenant (matches the seed file)
T2 = "UUID_TO_BIN('00000000-0000-7000-8000-000000000002')"   # another tenant


def run(sql: str, db: str | None = None) -> tuple[int, str]:
    args = CMD + ["--batch", "--skip-column-names"] + ([db] if db else [])
    p = subprocess.run(args, input=sql, capture_output=True, text=True)
    err = "\n".join(l for l in p.stderr.splitlines() if "Using a password" not in l)
    return p.returncode, err.strip()


def must(ok: bool, label: str, detail: str = "") -> bool:
    print(("PASS " if ok else "FAIL ") + label + (f" — {detail}" if detail and not ok else ""))
    return ok


# ---------------------------------------------------------------------------- fixtures
REGISTRY_FIXTURE = f"""
SET @t1 = {T1}; SET @t2 = {T2};
SET @state = UUID_TO_BIN('0192f1c4-0000-7000-8000-00000000a001');
SET @lga   = UUID_TO_BIN('0192f1c4-0000-7000-8000-00000000a002');
SET @inode = UUID_TO_BIN('0192f1c4-0000-7000-8000-00000000a003');
SET @inst  = UUID_TO_BIN('0192f1c4-0000-7000-8000-00000000a004');
SET @lrn   = UUID_TO_BIN('0192f1c4-0000-7000-8000-00000000a005');
INSERT INTO scope_node (id, tenant_id, level, code, name, path, depth, valid_from) VALUES
  (@state, @t1, 'state', 'NG-AB', 'Abia', 'NG.AB', 2, '2026-01-01'),
  (@lga,   @t1, 'lga', 'AB-ABS', 'Aba South', 'NG.AB.ABS', 3, '2026-01-01'),
  (@inode, @t1, 'institution', 'AB/SS/0412', 'GSS Aba', 'NG.AB.ABS.0412', 4, '2026-01-01');
INSERT INTO institution (id, tenant_id, scope_node_id, institution_code, name, category, ownership, is_public,
  operating_tenant_id, lga_scope_id, levels, address, onboarding_status, regulatory_status, status)
VALUES (@inst, @t1, @inode, 'INS-NG-004120', 'Government Secondary School Aba', 'combined_secondary', 'state', TRUE,
  @t1, @lga, JSON_ARRAY('JSS1','SSS3'), JSON_OBJECT('town','Aba'), 'live', 'public_owned', 'active');
INSERT INTO learner (id, tenant_id, global_learner_id, legal_given_name, legal_family_name, name_phonetic,
  date_of_birth, sex, status)
VALUES (@lrn, @t1, 'LRN-0004-1185-52', 'Adaeze', 'Okafor', 'ATS AKF', '2012-03-04', 'female', 'active');
"""

TESTS = [
    # (label, schema, sql, expected MySQL error code or None)
    ("registry fixture loads (scope, institution, learner)", "ceda_registry", REGISTRY_FIXTURE, None),
    ("one active primary enrolment per learner (FR-LRN-03, generated unique key)", "ceda_registry", REGISTRY_FIXTURE.split("INSERT INTO scope_node")[0] + """
INSERT INTO enrolment (id, tenant_id, scope_node_id, learner_id, institution_id, operating_tenant_id, education_level, is_primary, basis, start_on, status)
VALUES (UUID_TO_BIN(UUID()), @t1, @inode, @lrn, @inst, @t1, 'JSS1', TRUE, 'admission', '2026-09-08', 'active');
INSERT INTO enrolment (id, tenant_id, scope_node_id, learner_id, institution_id, operating_tenant_id, education_level, is_primary, basis, start_on, status)
VALUES (UUID_TO_BIN(UUID()), @t1, @inode, @lrn, @inst, @t1, 'JSS1', TRUE, 'transfer', '2026-10-01', 'active');
""", 1062),
    ("tenant-consistent foreign key refuses a cross-tenant reference", "ceda_registry", REGISTRY_FIXTURE.split("INSERT INTO scope_node")[0] + """
INSERT INTO enrolment (id, tenant_id, scope_node_id, learner_id, institution_id, operating_tenant_id, education_level, is_primary, basis, start_on, status)
VALUES (UUID_TO_BIN(UUID()), @t2, @inode, @lrn, @inst, @t2, 'JSS1', FALSE, 'admission', '2026-09-08', 'pending');
""", 1452),
    ("UBE Act: public basic-education SDAF payer must be government (FR-SUB-107)", "ceda_registry", f"""
SET @t1 = {T1};
INSERT INTO sdaf_payer_rule (id, tenant_id, scope_node_id, institution_type, education_level, is_basic_education, payer, version, status)
VALUES (UUID_TO_BIN(UUID()), @t1, UUID_TO_BIN('0192f1c4-0000-7000-8000-00000000a001'), 'primary', 'PRY4', TRUE, 'parent_or_student', 1, 'draft');
""", 3819),
    ("enum CHECK refuses an unknown status", "ceda_registry", f"""
SET @t1 = {T1};
UPDATE learner SET status = 'graduated' WHERE tenant_id = @t1;
""", 3819),
    ("append-only tables refuse UPDATE (trigger guard)", "ceda_registry", f"""
SET @t1 = {T1};
INSERT INTO match_pair_decision (id, tenant_id, entity_kind, record_a_id, record_b_id, decision)
VALUES (UUID_TO_BIN(UUID()), @t1, 'learner', UUID_TO_BIN(UUID()), UUID_TO_BIN(UUID()), 'different');
UPDATE match_pair_decision SET decision = 'same';
""", 1644),
    ("four-eyes CHECK on policy exceptions (requester ≠ approver)", "ceda_registry", f"""
SET @t1 = {T1}; SET @u = UUID_TO_BIN(UUID());
INSERT INTO policy_rule (id, tenant_id, scope_node_id, rule_key, rule_domain, title, version, expression, status, effective_from)
VALUES (UUID_TO_BIN('0192f1c4-0000-7000-8000-00000000b001'), @t1, UUID_TO_BIN('0192f1c4-0000-7000-8000-00000000a001'), 'G3', 'coverage', 'Teacher authorised', 1, 'when … then …', 'published', '2026-01-01');
INSERT INTO app_user (id, tenant_id, username, display_name, idp, status, failed_attempts)
VALUES (@u, @t1, 'head@gss-aba.example', 'Head', 'local', 'active', 0);
INSERT INTO policy_exception (id, tenant_id, scope_node_id, rule_id, reason, requested_by, approved_by, start_on, end_on, review_on, status)
VALUES (UUID_TO_BIN(UUID()), @t1, UUID_TO_BIN('0192f1c4-0000-7000-8000-00000000a003'), UUID_TO_BIN('0192f1c4-0000-7000-8000-00000000b001'), 'Cover', @u, @u, '2026-10-01', '2026-12-01', '2026-11-01', 'approved');
""", 3819),
    ("policy exception may not exceed 12 months", "ceda_registry", f"""
SET @t1 = {T1};
INSERT INTO policy_exception (id, tenant_id, scope_node_id, rule_id, reason, requested_by, start_on, end_on, review_on, status)
VALUES (UUID_TO_BIN(UUID()), @t1, UUID_TO_BIN('0192f1c4-0000-7000-8000-00000000a003'), UUID_TO_BIN('0192f1c4-0000-7000-8000-00000000b001'), 'Too long',
  (SELECT id FROM app_user LIMIT 1), '2026-10-01', '2027-12-01', '2026-11-01', 'requested');
""", 3819),
    ("ops: attendance_mark partitioned table accepts a mark", "ceda_ops", f"""
INSERT INTO attendance_mark (id, tenant_id, register_id, learner_id, enrolment_id, session_date, code, recorded_by, source)
VALUES (UUID_TO_BIN(UUID()), {T1}, UUID_TO_BIN(UUID()), UUID_TO_BIN(UUID()), UUID_TO_BIN(UUID()), '2026-10-13', 'P', UUID_TO_BIN(UUID()), 'teacher');
SELECT PARTITION_NAME FROM information_schema.PARTITIONS WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'attendance_mark' AND TABLE_ROWS >= 0 LIMIT 1;
""", None),
    ("ops: ledger entry must be one-sided (debit xor credit)", "ceda_ops", f"""
INSERT INTO ledger_entry (id, tenant_id, journal_id, account_id, posted_on, debit_minor, credit_minor, currency, source_kind, source_id)
VALUES (UUID_TO_BIN(UUID()), {T1}, UUID_TO_BIN(UUID()), UUID_TO_BIN(UUID()), '2026-10-13', 1000, 1000, 'NGN', 'journal', UUID_TO_BIN(UUID()));
""", 3819),
    ("ops: one open coverage gap per target per rule (generated unique key)", "ceda_ops", f"""
SET @csp = UUID_TO_BIN(UUID()); SET @inst = UUID_TO_BIN(UUID());
SET FOREIGN_KEY_CHECKS = 0;
INSERT INTO coverage_gap (id, tenant_id, scope_node_id, rule, severity, institution_id, class_subject_plan_id, learners_affected, owner_role, due_on, opened_at, status)
VALUES (UUID_TO_BIN(UUID()), {T1}, UUID_TO_BIN(UUID()), 'g2', 'critical', @inst, @csp, 38, 'HEAD', '2026-10-16', NOW(6), 'open');
INSERT INTO coverage_gap (id, tenant_id, scope_node_id, rule, severity, institution_id, class_subject_plan_id, learners_affected, owner_role, due_on, opened_at, status)
VALUES (UUID_TO_BIN(UUID()), {T1}, UUID_TO_BIN(UUID()), 'g2', 'critical', @inst, @csp, 38, 'HEAD', '2026-10-16', NOW(6), 'open');
""", 1062),
    ("vault: safeguarding chronology is append-only (DELETE refused)", "ceda_vault", f"""
SET FOREIGN_KEY_CHECKS = 0;
INSERT INTO safeguarding_entry (id, tenant_id, case_id, entry_kind, occurred_at, author_user_id, body)
VALUES (UUID_TO_BIN(UUID()), {T1}, UUID_TO_BIN(UUID()), 'note', NOW(6), UUID_TO_BIN(UUID()), 0x00);
DELETE FROM safeguarding_entry;
""", 1644),
]


def main() -> int:
    ok = True
    for f, db in ZONES:
        if not f.startswith("15_"):
            rc, err = run(f"DROP DATABASE IF EXISTS {db}; CREATE DATABASE {db} CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci;")
            if rc:
                return must(False, f"create schema {db}", err) and 1
        rc, err = run((DDL / f).read_text(encoding="utf-8"), db)
        ok &= must(rc == 0 and "ERROR" not in err, f"load {f} into {db}", err)
    rc, out = run("SELECT TABLE_SCHEMA, COUNT(*) FROM information_schema.TABLES WHERE TABLE_SCHEMA LIKE 'ceda\\_%' GROUP BY TABLE_SCHEMA;")
    print(subprocess.run(CMD + ["--table", "-e", "SELECT TABLE_SCHEMA AS zone_schema, COUNT(*) AS tables_loaded FROM information_schema.TABLES WHERE TABLE_SCHEMA LIKE 'ceda\\_%' GROUP BY TABLE_SCHEMA ORDER BY 1"],
                         capture_output=True, text=True).stdout)
    for label, db, sql, expect in TESTS:
        rc, err = run(sql, db)
        if expect is None:
            ok &= must(rc == 0, label, err)
        else:
            ok &= must(rc != 0 and f"ERROR {expect}" in err, label + f" (expects MySQL error {expect})", err or "statement succeeded")
    print("ALL CHECKS PASSED" if ok else "SOME CHECKS FAILED")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
