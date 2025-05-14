from django.contrib.auth.forms import UserCreationForm
from django.core.paginator import Paginator
from django.shortcuts import render, redirect
from app.forms import LoginForm, RegisterForm, UserProfileForm
from app.models import Question, Answer
from django.http import Http404
from django.urls import reverse, reverse_lazy
from django.contrib import auth
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User

def paginate(objects_list, request, per_page=10):
    page_num = request.GET.get('page', 1)
    paginator = Paginator(objects_list, per_page)
    page = paginator.get_page(page_num)
    return page

def index(request):
    questions = Question.objects.recent()
    page = paginate(questions, request, 5)
    ids = [q.id for q in page.object_list]
    questions = [Question.objects.full_info(id) for id in ids]
    return render(request, 'new_questions.html', context={'questions': questions, 'page': page})

def hot(request):
    questions = Question.objects.popular()
    page = paginate(questions, request, 5)
    ids = [q.id for q in page.object_list]
    questions = [Question.objects.full_info(id) for id in ids]
    return render(request, 'hot_questions.html', context={'questions': questions, 'page': page})

def question(request, question_id):
    q = Question.objects.full_info(question_id)
    if not q:
        raise Http404("Question does not exist")
    answers = Answer.objects.answers(q)
    return render(request, 'single_question.html', context={'question': q, 'answers': answers})

def tag(request, tag_name):
    filtered_questions = Question.objects.by_tag(tag_name)
    if not filtered_questions:
        raise Http404("Tag does not exist")
    page = paginate(filtered_questions, request, 5)
    ids = [q.id for q in page.object_list]
    questions = [Question.objects.full_info(id) for id in ids]
    return render(request, 'tag_questions.html', context={'questions': questions, 'page': page, 'tag': tag_name})

def login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            user = auth.authenticate(request, **form.cleaned_data)
            if user:
                auth.login(request, user)
                return redirect(reverse('edit'))
            else:
                form.add_error(field=None, error="User not found")
    else:
        form = LoginForm()
    return render(request, 'login.html', {'form': form})

def signup(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect(reverse('edit'))
    else:
        form = RegisterForm()
    return render(request, 'register.html', {'form': form})

def ask(request):
    return render(request, 'ask_question.html')

@login_required(login_url=reverse_lazy('login'))
def profile_edit(request):
    user = request.user
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
        return redirect(reverse('edit'))
    else:
        form = UserProfileForm(instance=user, initial={'avatar': user.profile.avatar})
    return render(request, 'profile_edit.html', {'form': form, 'nickname': user.first_name})

@login_required(login_url=reverse_lazy('login'))
def logout(request):
    auth.logout(request)
    return redirect('/')