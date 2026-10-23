"""CEDA 1.9.0 (CR-008): evidence-grade document masters — object-lock store, lock mode and retain-until date on
document, the document_rendition table (searchable PDF access copies) and the document_release register — and the
mfa_recovery_code table that completes CR-003's second factor.

Expand only: NULLable columns on document and three new tables; safe on a live 1.8.0 database.
"""

from django.db import migrations

from syntegra.schema.ddl import apply_release


class Migration(migrations.Migration):
    dependencies = [("schema", "0008_ceda_1_8_0")]
    operations = [migrations.RunPython(apply_release("1.9.0"), migrations.RunPython.noop, elidable=False)]
