from typing import Any
from django.db.models.query import QuerySet
from django.shortcuts import render
from .models import UserTranscation

# Create your views here.
from django.views.generic import CreateView, ListView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from .constants import WITHDRAWAL, DEPOSIT, LOAN, LOAN_PAID
from .forms import DepositForm, WithdrawForm, LoanRequestForm, TransferForm
from django.contrib import messages
from django.http import HttpResponse
from datetime import datetime
from django.db.models import Sum
from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.template.loader import render_to_string
from django.core.mail import EmailMessage ,EmailMultiAlternatives
class TranscationCreateMixins(LoginRequiredMixin, CreateView):

    template_name = "transaction.html"
    title = ""
    model = UserTranscation
    success_url = reverse_lazy("report")

    def get_form_kwargs(self, **kwargs):
        kwargs = super().get_form_kwargs(**kwargs)
        kwargs.update(
            {
                "account": self.request.user.account,
            }
        )
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({"title": self.title})

        return context


def send_transfer_email(user,subject ,amount,template):
    message = render_to_string(template, {
            'user': user,
            'amount': amount,
        })
    send_mail = EmailMultiAlternatives(subject, "", to=[user.email])
    send_mail.attach_alternative(message,'text/html')
    send_mail.send()

# class DepositeNow(TranscationCreateMixins):
#     form_class = DepositeForm
#     title = "Deposit"

#     def get_initial(self):
#         initial = {'transaction_type':DEPOSIT}
#         return initial


#     def form_valid(self,form):
#         amount = form.cleaned_data.get('amount')
#         account = self.request.user.account
#         account.balance += amount
#         account.save(
#             update_fields = ['balance']
#         )
#         messages.success(self.request,'{amount}$ was deposite amount add sccussfully ')
#         return super().form_valid(form)


class DepositMoneyView(TranscationCreateMixins):
    form_class = DepositForm
    title = "Deposit Form"

    def get_initial(self):
        initial = {"transaction_type": DEPOSIT}
        return initial

    def form_valid(self, form):
        amount = form.cleaned_data.get("amount")
        account = self.request.user.account
        transaction = form.save(commit=False)

        transaction.account = account
        transaction.balance_after_transaction = account.balance + amount
        transaction.save()

        account.balance += amount
        account.save(update_fields=["balance"])

        messages.success(
            self.request,
            f'{"{:,.2f}".format(float(amount))}$ was deposited to your account successfully',
        )
        send_transfer_email(self.request.user,amount,'Deposit Maney ','d.html')
        return super().form_valid(form)


class WithdrowNow(TranscationCreateMixins):
    form_class = WithdrawForm
    title = "Withdraw"

    def get_initial(self):
        initial = {"transaction_type": WITHDRAWAL}
        return initial

    def get_form_kwargs(self, **kwargs):
        form_kwargs = super().get_form_kwargs(**kwargs)
        form_kwargs["account"] = self.request.user.account
        return form_kwargs

    def form_valid(self, form):
        amount = form.cleaned_data.get("amount")
        account = self.request.user.account
        transaction = form.save(commit=False)
        transaction.account = account
        transaction.balance_after_transaction = account.balance - amount
        transaction.save()
        account.balance -= amount
        account.save(update_fields=["balance"])
        messages.success(self.request, f"{amount}$ was withdrawn successfully")
        send_transfer_email(self.request.user,'Withdrowal Now',amount,'d.html')
        return super().form_valid(form)


class LoanRequestNow(TranscationCreateMixins):
    form_class = LoanRequestForm
    title = "Request of Loan"

    def get_initial(self):
        initail = {"transaction_type": LOAN}
        return initail

    def form_valid(self, form):
        amount = form.cleaned_data.get("amount")

        current_loan = UserTranscation.objects.filter(
            account=self.request.user.account, transaction_type=3, load_approve=True
        ).count()

        if current_loan >= 3:
            return HttpResponse("Sir Your Loan limited already cross")
        messages.success(self.request, "loan submitted successfully")
        send_transfer_email(self.request.user,'Loan Request',amount,'lon.html')
        return super().form_valid(form)


class TransactionReportView(LoginRequiredMixin, ListView):
    template_name = "transaction_report.html"
    model = UserTranscation
    balance = 0

    def get_queryset(self):
        queryset = super().get_queryset().filter(account=self.request.user.account)

        start_date_str = self.request.GET.get("start_date")
        end_date_str = self.request.GET.get("end_data")

        if start_date_str and end_date_str:
            statr_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
            end_date = datetime.strptime(end_date_str, "%Y-%m-%d").date()

            queryset = UserTranscation.objects.filter(
                timestamp_date_gte=statr_date, timestamp_date_lte=end_date
            )

            self.balance = UserTranscation.objects.filter(
                timestamp_date_gte=statr_date, timestamp_date_lte=end_date
            ).aaggregate(Sum("amount"))["amount__sum"]
        else:
            self.balance = self.request.user.account.balance
        return queryset.distinct()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({"account": self.request.user.account})
        return context


class PayLoanView(LoginRequiredMixin, View):
    def get(self, request, loan_id):
        loan = get_object_or_404(UserTranscation, id=loan_id)
        print(loan)
        if loan.loan_approve:
            user_account = loan.account
            # Reduce the loan amount from the user's balance
            # 5000, 500 + 5000 = 5500
            # balance = 3000, loan = 5000
            if loan.amount < user_account.balance:
                user_account.balance -= loan.amount
                loan.balance_after_transaction = user_account.balance
                user_account.save()
                loan.loan_approved = True
                loan.transaction_type = LOAN_PAID
                loan.save()
                return redirect("list")
            else:
                messages.error(
                    self.request, f"Loan amount is greater than available balance"
                )

        return redirect("loan")


class ListLoanView(LoginRequiredMixin, ListView):
    model = UserTranscation
    template_name = "loan.html"
    context_object_name = "loans"

    def get_queryset(self):
        user_account = self.request.user.account
        queryset = UserTranscation.objects.filter(
            account=user_account, transaction_type=LOAN
        )
        return queryset


class TransferView(LoginRequiredMixin, CreateView):
    template_name = "transfer.html"
    success_url = reverse_lazy('report')
    form_class = TransferForm

    def form_valid(self, form):
        sender_user = form.cleaned_data["sender_account"]
        receiver_user = form.cleaned_data["receiver_account"]
        amount = form.cleaned_data["amount"]

        if sender_user.balance >= amount:
            sender_user.balance -= amount
            receiver_user.balance += amount
            sender_user.save()
            messages.success(self.request,'Money Transfer Successfully !')
            send_transfer_email(self.request.user,'Transfer Maney',amount,'ts.html')
            receiver_user.save()
            return super().form_valid(form)
        else:
            form.add_error("amount", "Insufficient funds")
            return super().form_invalid(form)


