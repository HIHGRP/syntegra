"""CEDA 1.5.0 (CR-004): education and training institutions of the security agencies.

Expand only: three widened checks (tenant kind, scope node level and ref kind, warehouse scope level), eight new
registry tables and new code-list values; safe on a live 1.4.0 database.
"""

from django.db import migrations

from syntegra.schema.ddl import apply_release


class Migration(migrations.Migration):
    dependencies = [("schema", "0004_ceda_1_4_0")]
    operations = [migrations.RunPython(apply_release("1.5.0"), migrations.RunPython.noop, elidable=False)]
