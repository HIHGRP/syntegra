from django.apps import AppConfig


class WebConfig(AppConfig):
    name = "syntegra.web"
    label = "web"
    default_auto_field = "django.db.models.BigAutoField"

    def ready(self) -> None:
        # the API refuses writes below the level of the form that performs the same action (CR-008, FR-ADM-203)
        from syntegra.core import access
        from syntegra.web import forms

        access.register_write_levels(forms.write_levels())
