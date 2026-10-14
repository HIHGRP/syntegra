"""CEDA 1.4.0 (CR-003): two-factor authentication and federated single sign-on.

Expand only: two NULLable columns (mfa_factor.last_step, user_session.auth_method) and one new table
(identity_provider_config); safe on a live 1.3.0 database.
"""

from django.db import migrations

from syntegra.schema.ddl import apply_release


class Migration(migrations.Migration):
    dependencies = [("schema", "0003_ceda_1_3_0")]
    operations = [migrations.RunPython(apply_release("1.4.0"), migrations.RunPython.noop, elidable=False)]
