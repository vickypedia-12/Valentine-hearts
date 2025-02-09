from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Profile, QuestionResponse, Question

class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({'class': 'form-control'})
        self.fields['email'].widget.attrs.update({'class': 'form-control'})
        self.fields['password1'].widget.attrs.update({'class': 'form-control'})
        self.fields['password2'].widget.attrs.update({'class': 'form-control'})

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['bio', 'interests', 'gender', 'preferences', 'zodiac_sign', 'birth_date']
        widgets = {
            'bio': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Tell us about yourself...'
            }),
            'interests': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Your interests (e.g., music, movies, sports)'
            }),
            'gender': forms.Select(
                attrs={'class': 'form-control'},
                choices=Profile.GENDER_CHOICES
            ),
            'preferences': forms.Select(
                attrs={'class': 'form-control'},
                choices=Profile.PREFERENCE_CHOICES
            ),
            'zodiac_sign': forms.Select(
                attrs={'class': 'form-control'},
                choices=Profile.ZODIAC_CHOICES
            ),
            'birth_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }
class QuestionnaireForm(forms.Form):
    def __init__(self, *args, **kwargs):
        questions = kwargs.pop('questions', None)
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        if questions:
            for question in questions:
                choices = [(choice, choice) for choice in question.choices]
                field = forms.ChoiceField(
                    label=question.text,
                    choices=choices,
                    widget=forms.RadioSelect(attrs={
                        'class': 'question-choices',
                        'required': True,
                        'data-question-id': question.id
                    })
                )
                
                if user:
                    response = QuestionResponse.objects.filter(user=user, question=question).first()
                    if response:
                        field.initial = response.answer
                        field.widget.attrs['disabled'] = 'disabled'
                        field.widget.attrs['data-answered'] = 'true'
                        field.widget.attrs['data-selected'] = response.answer
                
                self.fields[f'question_{question.id}'] = field