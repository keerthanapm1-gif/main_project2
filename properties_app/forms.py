from django import forms
from django import forms
from django.contrib.auth.models import User
from .models import PropertyReview, Inquiry

class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-input', 'placeholder': 'Password'}))
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-input', 'placeholder': 'Confirm Password'}))
    
    class Meta:
        model = User
        fields = ['username', 'email']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Username'}),
            'email': forms.EmailInput(attrs={'class': 'form-input', 'placeholder': 'Email Address'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password != confirm_password:
            self.add_error('confirm_password', "Password does not match.")
        
        return cleaned_data

class PropertyReviewForm(forms.ModelForm):
    class Meta:
        model = PropertyReview
        fields = ['rating', 'review_text']
        widgets = {
            'rating': forms.Select(attrs={'class': 'form-input'}),
            'review_text': forms.Textarea(attrs={'class': 'form-input', 'rows': 3, 'placeholder': 'Write your review here...'}),
        }

class InquiryForm(forms.ModelForm):
    class Meta:
        model = Inquiry
        fields = ['name', 'email', 'phone', 'message', 'inquiry_type']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Your Name'}),
            'email': forms.EmailInput(attrs={'class': 'form-input', 'placeholder': 'Your Email'}),
            'phone': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Your Phone Number'}),
            'message': forms.Textarea(attrs={'class': 'form-input', 'rows': 4, 'placeholder': 'Your Message'}),
            'inquiry_type': forms.Select(attrs={'class': 'form-input'}),
        }

