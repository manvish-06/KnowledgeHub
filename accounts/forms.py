from django import forms

class RegisterForm(forms.Form):
    username = forms.CharField(max_length=150, label="Username")
    email = forms.EmailField(label="Email")
    password = forms.CharField(widget=forms.PasswordInput(), label="Password")
    confirmation = forms.CharField(widget=forms.PasswordInput(), label="Confirm Password")

    
