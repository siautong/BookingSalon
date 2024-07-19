from django.forms import ModelForm
from django import forms
from mysalon.models import tbBooking, tbLayanan
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import CustomUser
from .models import Staff
from django.contrib.auth.forms import PasswordChangeForm
from django.core.exceptions import ValidationError
from datetime import time

class FormBooking (ModelForm):
    namalayanan = forms.ModelChoiceField(
        queryset=tbLayanan.objects.all(),
        empty_label="Pilih Layanan",
        widget=forms.Select(attrs={'class': 'form-control form-control-lg'})
    )
    desk = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control form-control-lg'}))
    namauser = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control form-control-lg'}))
    alamat = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control form-control-lg'}))
    nomoruser = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control form-control-lg'}))
    tanggal = forms.DateField(widget=forms.DateInput(attrs={'class': 'form-control form-control-lg', 'type': 'date'}))
    waktu = forms.TimeField(widget=forms.TimeInput(attrs={'class': 'form-control form-control-lg', 'type': 'time'}))
    
    class Meta:
        model = tbBooking
        fields = ['namalayanan', 'desk', 'tanggal', 'waktu']
        
    def clean_waktu(self):
        waktu = self.cleaned_data.get('waktu')
        opening_time = time(10, 0)  # 10:00 AM
        closing_time = time(17, 0)  # 5:00 PM

        if not (opening_time <= waktu <= closing_time):
            raise ValidationError("Waktu booking harus antara jam 10 pagi hingga 5 sore.")

        return waktu

class FormLayanan (ModelForm):
    class Meta:
        model = tbLayanan
        fields = '__all__'
        widgets = {
            'namalayanan' : forms.TextInput({'class':'form-control'}),
}

class CustomUserCreationForm(forms.ModelForm):
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Password confirmation', widget=forms.PasswordInput)

    class Meta:
        model = CustomUser
        fields = ['email', 'username', 'nama', 'alamat', 'nohp']

    def clean_password2(self):
        # Check that the two password entries match
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't match")
        return password2

    def save(self, commit=True):
        # Save the provided password in hashed format
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user
    

from django.contrib.auth.forms import PasswordChangeForm

class CustomPasswordChangeForm(PasswordChangeForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['old_password'].widget.attrs.update({'class': 'form-control'})
        self.fields['password1'].widget.attrs.update({'class': 'form-control'})
        self.fields['password2'].widget.attrs.update({'class': 'form-control'})
        

class CustomStaffCreationForm(forms.ModelForm):
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Password confirmation', widget=forms.PasswordInput)

    class Meta:
        model = Staff
        fields = ['email', 'username', 'nama', 'alamat', 'nohp']

    def clean_password2(self):
        # Check that the two password entries match
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't match")
        return password2

    def save(self, commit=True):
        # Save the provided password in hashed format
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


