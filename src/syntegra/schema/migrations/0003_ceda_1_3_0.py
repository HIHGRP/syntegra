"""CEDA 1.3.0 (CR-002): national clearance network — exchange directory, exchange log, national NIN token.

Expand only: two NULLable columns, one index and two new tables; safe on a live 1.2.0 database.
"""

from django.db import migrations

from syntegra.schema.ddl import apply_release


class Migration(migrations.Migration):
    dependencies = [("schema", "0002_ceda_1_2_0")]
    operations = [migrations.RunPython(apply_release("1.3.0"), migrations.RunPython.noop, elidable=False)]
