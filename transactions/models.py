from django.db import models
from .constants import TRANSACTION_TYPE
# Create your models here.
from accounts.models import UserBankAccount

class UserTranscation(models.Model):
    account = models.ForeignKey(UserBankAccount,on_delete = models.CASCADE,related_name = 'transactions')
    amount = models.DecimalField(max_digits=12,decimal_places = 2)
    balance_after_transaction = models.DecimalField(max_digits=12,decimal_places = 2)
    transaction_type = models.IntegerField(choices=TRANSACTION_TYPE)
    load_approve = models.BooleanField(default = False)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['timestamp']




class TransferManey(models.Model):
    sender_account = models.ForeignKey(UserBankAccount, on_delete=models.CASCADE, related_name='sender')
    receiver_account = models.ForeignKey(UserBankAccount, on_delete=models.CASCADE, related_name='receiver')
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    
