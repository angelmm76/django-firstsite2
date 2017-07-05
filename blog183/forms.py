from django import forms
from django.forms import ModelForm
from django.contrib.auth.models import User
from .models import BlogPost

class SignupForm0(forms.Form):
	username = forms.CharField(label="username", max_length=30)
	firstname = forms.CharField(label="firstname", max_length=30, required=False)
	lastname = forms.CharField(label="lastname", max_length=30, required=False)
	email = forms.EmailField()

class SignupForm(ModelForm):
	password1 = forms.CharField(label=("Password"), widget=forms.PasswordInput)
	password2 = forms.CharField(label=("Password confirmation"),
		widget=forms.PasswordInput,
		help_text=("Enter the same password as above, for verification."))

	def clean(self):
		cleaned_data = super(SignupForm, self).clean()
		pw1 = cleaned_data.get('password1')
		pw2 = cleaned_data.get('password2')

		if pw1 != pw2:
			raise forms.ValidationError("Passwords don't match")

	class Meta:
		model = User
		fields = ['username', 'first_name', 'last_name', 'email']


class EditForm(ModelForm):
	class Meta:
		model = BlogPost
		fields = ['blogpost_title', 'blogpost_content', 'image']       