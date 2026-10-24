"""CEDA 1.6.0 (CR-005): federal unity colleges and federal special training institutions; education watchdogs.

Expand only: five new tables (federal_body, federal_body_unit, federal_institution and institution_regulation in the
registry zone; regulatory_body and body_dependency in the platform zone); safe on a live 1.5.0 database.
"""

from django.db import migrations

from syntegra.schema.ddl import apply_release


class Migration(migrations.Migration):
    dependencies = [("schema", "0005_ceda_1_5_0")]
    operations = [migrations.RunPython(apply_release("1.6.0"), migrations.RunPython.noop, elidable=False)]
