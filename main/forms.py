from django import forms


class ParserStartForm(forms.Form):
    spreadsheet = forms.CharField(max_length=240)