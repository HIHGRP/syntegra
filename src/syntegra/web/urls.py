from django.urls import path

from syntegra.web import views

urlpatterns = [
    path("", views.home, name="home"),
    path("sign-in", views.sign_in, name="sign_in"),
    path("sign-out", views.sign_out, name="sign_out"),
    path("pages", views.catalogue, name="catalogue"),
    path("auth/context", views.workspace, name="workspace"),
    path("forms", views.forms_hub, name="forms_hub"),
    path("forms/<slug:key>", views.form_page, name="form_page"),
    path("verify", views.verify, name="verify"),
    path("registers/class/<uuid:class_id>", views.register, name="register"),
    path("learners/new", views.learner_new, name="learner_new"),
    path("learners/<uuid:learner_id>", views.learner, name="learner"),
    path("coverage", views.coverage, name="coverage"),
    path("admissions/clearance", views.clearance, name="clearance"),
    path("clearance/network", views.clearance_network, name="clearance_network"),
    path("security-training", views.security_training, name="security_training"),
    path("security-training/agencies/<uuid:agency_id>", views.security_agency, name="security_agency"),
    path(
        "security-training/institutions/<uuid:institution_id>", views.security_institution, name="security_institution"
    ),
    path("security-training/courses/<uuid:course_id>", views.security_course, name="security_course"),
    path("security-training/intakes/<uuid:intake_id>", views.security_intake, name="security_intake"),
    path("federal-institutions", views.federal_institutions, name="federal_institutions"),
    path("regulators", views.regulators, name="regulators"),
    path("institutions/<uuid:institution_id>/regulation", views.institution_regulation, name="institution_regulation"),
    path("hr/establishment", views.establishment, name="establishment"),
]
