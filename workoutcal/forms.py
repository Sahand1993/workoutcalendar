from django import forms
from django.contrib.postgres.fields import JSONField
from .models import User
from django.utils.translation import gettext as _

class NameForm(forms.Form):
	your_name = forms.CharField(label = 'Your name', max_length=100)

class ContactForm(forms.Form):
	subject = forms.CharField(max_length=100)
	message = forms.CharField(widget=forms.Textarea)
	sender = forms.EmailField()
	cc_myself = forms.BooleanField(required=False)

class AddLiftForm(forms.Form):
	name = forms.CharField(max_length=100)

class UserForm(forms.ModelForm):
	password = forms.CharField(widget=forms.PasswordInput)
	confirm_password = forms.CharField(widget=forms.PasswordInput)

	class Meta:
		model = User
		fields = ['username','email','password']

	def clean_password(self):
		password = self.cleaned_data['password']

		#Password has to be long enough
		if len(password) < 8:
			raise forms.ValidationError(_('The password needs to be at least 8 characters long'))

		return password

	def clean(self):
		cleaned_data = super(UserForm, self).clean()
		try:
			password = cleaned_data['password']
			confirm_password = cleaned_data['confirm_password']
			if not password == confirm_password:
				raise forms.ValidationError(_('The passwords do not match'))
		except KeyError:
			pass

class LoginForm(forms.Form):
	email = forms.EmailField()
	password = forms.CharField(widget=forms.PasswordInput)