from django import forms
from support.models import SupportTicket


class SupportTicketForm(forms.ModelForm):
    guest_email = forms.EmailField(
        required=False,
        widget=forms.EmailInput(attrs={
            'class': 'form-input',
            'placeholder': 'Your email (for ticket status updates)',
        })
    )

    class Meta:
        model = SupportTicket
        fields = ['subject', 'category', 'priority', 'description', 'guest_email']
        widgets = {
            'subject': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Brief summary of the issue',
                'required': True,
            }),
            'category': forms.Select(attrs={
                'class': 'form-select',
                'required': True,
            }),
            'priority': forms.Select(attrs={
                'class': 'form-select',
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-input',
                'rows': 5,
                'placeholder': 'Please provide details about what happened, steps to reproduce, or any error messages received...',
                'required': True,
            }),
        }

    def clean(self):
        cleaned_data = super().clean()
        subject = cleaned_data.get('subject')
        description = cleaned_data.get('description')
        if subject and len(subject.strip()) < 5:
            self.add_error('subject', "Subject must be at least 5 characters.")
        if description and len(description.strip()) < 10:
            self.add_error('description', "Please provide a more descriptive explanation (minimum 10 characters).")
        return cleaned_data
