"""CEDA 1.8.0 (CR-007): the user's school or office at sign-in; one session per account; document management for
digitised paper records with a full-text index; access levels.

Expand only: NULLable columns on scope_node (office address), user_session (school or office, end reason) and
document (reference number, description, paper reference), two keys on document, and the new document_index table
with its FULLTEXT key; safe on a live 1.7.0 database.
"""

from django.db import migrations

from syntegra.schema.ddl import apply_release


class Migration(migrations.Migration):
    dependencies = [("schema", "0007_ceda_1_7_0")]
    operations = [migrations.RunPython(apply_release("1.8.0"), migrations.RunPython.noop, elidable=False)]
