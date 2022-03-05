from django import forms


class LoginForm(forms.Form):
    login = forms.CharField(max_length=100)
    password = forms.CharField(widget=forms.PasswordInput, max_length=100)


class SignUpForm(forms.Form):
    username = forms.CharField(max_length=100)
    email = forms.EmailField()
    first_name = forms.CharField(max_length=100, required=False, help_text='optional',
                                 widget=forms.TextInput(attrs={'placeholder': 'optional field'}))
    last_name = forms.CharField(max_length=100, required=False, help_text='optional',
                                widget=forms.TextInput(attrs={'placeholder': 'optional field'}))
    setup_password = forms.CharField(widget=forms.PasswordInput, max_length=100)
    confirm_password = forms.CharField(widget=forms.PasswordInput, max_length=100)
    terms_of_use = forms.BooleanField()
