"""CEDA 1.7.0 (CR-006): institutional accounting and budgets; funding and loan platforms; government property,
facility usability and proactive actions; the infrastructure, budget and funding warehouse marts; security-agency
curricula through each agency's structure.

Expand only: 24 new tables (cost centres, budget lines, commitments, virements, imprest; funding programmes,
applications, agreements, disbursements, instalments, repayments; property sites, facility assessments, maintenance
schedules, facility actions; two security-curriculum tables in the registry; six warehouse tables), new code-list
values, and a (tenant_id, id) unique key on three existing operations tables; safe on a live 1.6.0 database.
"""

from django.db import migrations

from syntegra.schema.ddl import apply_release


class Migration(migrations.Migration):
    dependencies = [("schema", "0006_ceda_1_6_0")]
    operations = [migrations.RunPython(apply_release("1.7.0"), migrations.RunPython.noop, elidable=False)]
