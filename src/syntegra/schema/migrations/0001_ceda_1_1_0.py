"""CEDA 1.1.0 baseline: every zone's tables, constraints, triggers and (registry) code-list seed."""

from django.db import migrations

from syntegra.schema.ddl import apply_release


class Migration(migrations.Migration):
    initial = True
    dependencies: list[tuple[str, str]] = []
    operations = [migrations.RunPython(apply_release("1.1.0"), migrations.RunPython.noop, elidable=False)]
