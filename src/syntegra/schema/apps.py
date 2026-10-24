from django.apps import AppConfig


class SchemaConfig(AppConfig):
    name = "syntegra.schema"
    label = "schema"
    verbose_name = "CEDA physical schema (applies ceda/generated/mysql to each zone)"
