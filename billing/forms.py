from django import forms
from .models import HistoryRecord, TransferRecord

class HistoryRecordForm(forms.ModelForm):
    class Meta:
        model = HistoryRecord
        # fields = '__all__'
        exclude = ['创建时间', '修改时间']

class TransferRecordForm(forms.ModelForm):
    class Meta:
        model = TransferRecord
        fields = '__all__'
