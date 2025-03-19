from django import forms
from .models import User

class SignupForm(forms.ModelForm):
    # Define choices for select fields
    EDUCATION_CHOICES = [
        ('', 'Select an option'),
        ('Under 10th', 'Under 10th'),
        ('10th Pass', '10th Pass'),
        ('12th Pass', '12th Pass'),
        ('Undergraduate', 'Undergraduate'),
        ('Graduate', 'Graduate'),
        ('Postgraduate', 'Postgraduate'),
        ('No Education', 'No Education'),
    ]
    
    # Get all Indian states from your original HTML
    LOCATION_CHOICES = [
        ('', 'Select a state'),
        ('Andhra Pradesh', 'Andhra Pradesh'),
        ('Arunachal Pradesh', 'Arunachal Pradesh'),
        ('Assam', 'Assam'),
        ('Bihar', 'Bihar'),
        ('Chhattisgarh', 'Chhattisgarh'),
        ('Goa', 'Goa'),
        ('Gujarat', 'Gujarat'),
        ('Haryana', 'Haryana'),
        ('Himachal Pradesh', 'Himachal Pradesh'),
        ('Jharkhand', 'Jharkhand'),
        ('Karnataka', 'Karnataka'),
        ('Kerala', 'Kerala'),
        ('Madhya Pradesh', 'Madhya Pradesh'),
        ('Maharashtra', 'Maharashtra'),
        ('Manipur', 'Manipur'),
        ('Meghalaya', 'Meghalaya'),
        ('Mizoram', 'Mizoram'),
        ('Nagaland', 'Nagaland'),
        ('Odisha', 'Odisha'),
        ('Punjab', 'Punjab'),
        ('Rajasthan', 'Rajasthan'),
        ('Sikkim', 'Sikkim'),
        ('Tamil Nadu', 'Tamil Nadu'),
        ('Telangana', 'Telangana'),
        ('Tripura', 'Tripura'),
        ('Uttar Pradesh', 'Uttar Pradesh'),
        ('Uttarakhand', 'Uttarakhand'),
        ('West Bengal', 'West Bengal'),
    ]
    
    # Override form fields to add choices and widgets
    location = forms.ChoiceField(choices=LOCATION_CHOICES)
    education_qualification = forms.ChoiceField(choices=EDUCATION_CHOICES)
    
    class Meta:
        model = User
        fields = ['username', 'age', 'location', 'profession', 
                 'education_qualification', 'income', 'password']
        widgets = {
            'password': forms.PasswordInput(),
            'age': forms.NumberInput(),
            'income': forms.NumberInput(),
        }

class LoginForm(forms.Form):
    username = forms.CharField(max_length=150)
    password = forms.CharField(widget=forms.PasswordInput)