from django import forms
from django.contrib.auth.models import User
from app.models import Profile, Question, Tag, Answer


class LoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)

    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get('username')
        password = cleaned_data.get('password')
        if not username:
            self.add_error('username', 'Your username are required.')
        elif not password:
            self.add_error('password', 'Your password is required.')

class RegisterForm(forms.ModelForm):
    login = forms.CharField(label="Login")
    nickname = forms.CharField(label="Nickname")
    password = forms.CharField(label="Password", widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput, label="Confirm Password")
    avatar = forms.ImageField(required=False, label="Upload avatar")

    class Meta:
        model = User
        fields = ('login', 'email', 'nickname', 'password', 'confirm_password', 'avatar')

    def clean_login(self):
        login = self.cleaned_data.get('login')
        if User.objects.filter(username=login).exists():
            self.add_error('login', 'This login is already taken.')
        return login

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            self.add_error('email', 'Email is already registered.')
        return email

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm = cleaned_data.get("confirm_password")

        if password and confirm and password != confirm:
            self.add_error('confirm_password', 'The passwords do not match.')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = self.cleaned_data['login']
        user.first_name = self.cleaned_data['nickname']
        user.set_password(self.cleaned_data['password'])

        if commit:
            user.save()
            avatar = self.cleaned_data.get('avatar')
            if avatar:
                Profile.objects.create(user=user, avatar=avatar)
            else:
                Profile.objects.create(user=user, avatar='images/default_avatar.png')

        return user

class UserProfileForm(forms.ModelForm):
    login = forms.CharField(label="Login")
    nickname = forms.CharField(label="Nickname")
    avatar = forms.ImageField(required=False, label='Upload Avatar')

    class Meta:
        model = User
        fields = ('login', 'email', 'nickname', 'avatar')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance:
            self.fields['login'].initial = self.instance.username
            self.fields['nickname'].initial = self.instance.first_name
            self.fields['email'].initial = self.instance.email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = self.cleaned_data['login']
        user.first_name = self.cleaned_data['nickname']
        if commit:
            user.save()
            image = self.cleaned_data.get('avatar')
            if image:
                profile = user.profile
                profile.avatar = image
                profile.save()

class AskQuestionForm(forms.ModelForm):
    tags_field = forms.CharField(
        widget=forms.TextInput(attrs={
            'placeholder': 'e.g. css, html, flexbox',
        })
    )
    class Meta:
        model = Question
        fields = ('title', 'body', 'tags_field')
        widgets = {
            'title': forms.TextInput(attrs={
                'placeholder': 'e.g. How to center a div in CSS?'
            }),
            'body': forms.Textarea(attrs={
                'placeholder': "e.g. I tried using flexbox, but the div isn't centered..."
            })
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

    def save(self, commit=True):
        question = super().save(commit=False)
        question.questioner = self.user
        if commit:
            question.save()
            tags = self.cleaned_data['tags_field'].split(' ')
            for tag_name in tags:
                tag, _ = Tag.objects.get_or_create(name=tag_name)
                question.tags.add(tag)
        return question

class AnswerForm(forms.ModelForm):
    class Meta:
        model = Answer
        fields = ('text',)
        widgets = {
            'text': forms.Textarea(attrs={
                'placeholder': ""
            }),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        self.question_id = kwargs.pop('question_id', None)
        super().__init__(*args, **kwargs)

    def save(self, commit=True):
        answer = super().save(commit=False)
        answer.question_id = self.question_id
        answer.answerer = self.user
        if commit:
            answer.save()
        return answer