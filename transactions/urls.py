from django.urls import path,include
from . import views
urlpatterns = [
    path('Deposit/',views.DepositMoneyView.as_view(),name='deposit'),
    path('withdrow/',views.WithdrowNow.as_view(),name='withdrow'),
    path('transaction_report/',views.TransactionReportView.as_view(),name='report'),
    path('Loan/',views.LoanRequestNow.as_view(),name='loan'),
    path('LoanView/',views.ListLoanView.as_view(),name='list'),
    path('payloan<int:loan_id>/',views.PayLoanView.as_view(),name='pay'),
    path('Treansfer/',views.TransferView.as_view(),name='transfer'),
]
