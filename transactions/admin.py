from django.contrib import admin

# from transactions.models import Transaction
from .models import UserTranscation , TransferManey
from .views import send_transfer_email
@admin.register(UserTranscation)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ['account', 'amount', 'balance_after_transaction', 'transaction_type', 'load_approve']
    
    def save_model(self, request, obj, form, change):
        obj.account.balance += obj.amount
        obj.balance_after_transaction = obj.account.balance
        obj.account.save()
        send_transfer_email(obj.account.user,'Loan Apporved',obj.amount,'app.html')
        super().save_model(request, obj, form, change)

admin.site.register(TransferManey)