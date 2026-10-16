from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Article, Newsletter, CustomUser, Publisher


class RegistrationForm(UserCreationForm):
    '''The submitted format for users to register on the application.'''
    ROLE_CHOICES = [
        ('reader', 'reader'),
        ('journalist', 'journalist'),
        ('editor', 'editor'),
        ('publisher', 'publisher')
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

    def clean_email(self):
        email = self.cleaned_data['email']

        if CustomUser.objects.filter(email=email).exists():
            raise forms.ValidationError(
                'An account with this email address already exists.'
            )

        return email


class ArticleForm(forms.ModelForm):
    '''The submitted format for articles'''

    class Meta:
        model = Article
        fields = ['title', 'content', 'publisher']

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        self.fields['publisher'].empty_label = 'Publish Independently'

        self.fields['publisher'].queryset = Publisher.objects.filter(
            journalists=user
        ) if user else Publisher.objects.none()


class NewsletterForm(forms.ModelForm):
    '''The submitted format for Newsletters'''
    class Meta:
        model = Newsletter
        fields = ['title', 'description', 'articles']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['articles'].queryset = Article.objects.filter(
            approved=True
        )
        if not self.fields['articles'].queryset.exists():
            self.fields['articles'].empty_label = "No articles available"


class PublisherForm(forms.ModelForm):
    '''Form used by publishers to create their publication.'''

    journalists = forms.ModelMultipleChoiceField(
        queryset=CustomUser.objects.filter(role='journalist'),
        required=False,
        widget=forms.CheckboxSelectMultiple
    )

    editors = forms.ModelMultipleChoiceField(
        queryset=CustomUser.objects.filter(role='editor'),
        required=False,
        widget=forms.CheckboxSelectMultiple
    )

    class Meta:
        model = Publisher
        fields = ['name', 'journalists', 'editors']


class PublisherNameForm(forms.ModelForm):
    '''Form used to update only the name of a publication.'''

    class Meta:
        model = Publisher
        fields = ['name']


class ReaderSubscriptionForm(forms.ModelForm):
    '''Form used for readers to subscribe to publishers and journalists.'''

    journalist_subscriptions = forms.ModelMultipleChoiceField(
        queryset=CustomUser.objects.filter(role='journalist'),
        required=False,
        widget=forms.CheckboxSelectMultiple
    )

    publisher_subscriptions = forms.ModelMultipleChoiceField(
        queryset=Publisher.objects.all(),
        required=False,
        widget=forms.CheckboxSelectMultiple
    )

    class Meta:
        model = CustomUser
        fields = ['journalist_subscriptions', 'publisher_subscriptions']
