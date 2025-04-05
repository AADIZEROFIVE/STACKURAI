# forms.py
from django import forms

class FinancialGoalForm(forms.Form):
    goal = forms.CharField(
        label="What is your financial goal?",
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Examples: Save for retirement, Buy a house in 5 years, Pay off student loans, Start investing for passive income...'
        }),
        max_length=500,
        help_text="Be specific about your goals and timeframe to receive a more personalized roadmap."
    )