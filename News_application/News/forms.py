from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Article, Newsletter, CustomUser


class RegistrationForm(UserCreationForm):
    ROLE_CHOICES = [
        ('reader', 'reader'),
        ('journalist', 'journalist'),
        ('editor', 'editor'),
    ]

    role = forms.ChoiceField(choices=ROLE_CHOICES)

    class Meta:
        model = CustomUser
        fields = [
            'username',
            'email',
            'password1',
            'password2',
            'role'
        ]


class ArticleForm(forms.ModelForm):
    '''The submitted format for articles'''
    class Meta:
        model = Article
        fields = ['title', 'content', 'author', 'publisher']


class NewsletterForm(forms.ModelForm):
    '''The submitted format for Newsletters'''
    class Meta:
        model = Newsletter
        fields = ['title', 'description', 'author', 'articles']
