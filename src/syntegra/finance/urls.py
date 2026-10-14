from django.urls import path

from syntegra.finance import api

urlpatterns = [
    path("finance/cost-centres", api.CostCentres.as_view()),
    path("finance/budgets", api.Budgets.as_view()),
    path("finance/budgets/<uuid:pk>/approve", api.BudgetApproval.as_view()),
    path("finance/commitments", api.Commitments.as_view()),
    path("finance/commitments/<uuid:pk>/spend", api.CommitmentSpend.as_view()),
    path("finance/commitments/<uuid:pk>/release", api.CommitmentRelease.as_view()),
    path("finance/virements", api.Virements.as_view()),
    path("finance/virements/<uuid:pk>/decision", api.VirementDecision.as_view()),
    path("finance/imprest", api.ImprestList.as_view()),
    path("finance/imprest/<uuid:pk>/approval", api.ImprestApproval.as_view()),
    path("finance/imprest/<uuid:pk>/retirement", api.ImprestRetirement.as_view()),
]
