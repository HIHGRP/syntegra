"""CEDA 1.1.0 baseline: create every zone's tables, constraints, triggers and (registry) code-list seed."""

from django.db import migrations

from syntegra.schema.ddl import apply_ceda_ddl


class Migration(migrations.Migration):
    initial = True
    dependencies: list[tuple[str, str]] = []
    operations = [migrations.RunPython(apply_ceda_ddl, migrations.RunPython.noop, elidable=False)]
