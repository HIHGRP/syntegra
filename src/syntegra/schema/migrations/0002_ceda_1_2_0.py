"""CEDA 1.2.0 (CR-001): enterprise HRMS and fee-clearance tables — expand only, safe on a live 1.1.0 database."""

from django.db import migrations

from syntegra.schema.ddl import apply_release


class Migration(migrations.Migration):
    dependencies = [("schema", "0001_ceda_1_1_0")]
    operations = [migrations.RunPython(apply_release("1.2.0"), migrations.RunPython.noop, elidable=False)]
