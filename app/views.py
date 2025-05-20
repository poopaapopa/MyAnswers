from django.contrib.auth.forms import UserCreationForm
from django.core.paginator import Paginator
from django.core.exceptions import PermissionDenied
from django.shortcuts import render, redirect, get_object_or_404
from app.forms import LoginForm, RegisterForm, UserProfileForm, AskQuestionForm, AnswerForm
from app.models import Question, Answer, QuestionLike, AnswerLike
from django.http import Http404
from django.urls import reverse, reverse_lazy
from django.contrib import auth
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.views.decorators.http import require_POST
from django.http import JsonResponse
import json

def paginate(objects_list, request, per_page=10):
    page_num = request.GET.get('page', 1)
    paginator = Paginator(objects_list, per_page)
    page = paginator.get_page(page_num)
    return page

def handle_like(obj_id, user, is_like, is_question):
    LikeModel = QuestionLike if is_question else AnswerLike
    field_name = 'question' if is_question else 'answer'
    Model = Question if is_question else Answer

    obj = get_object_or_404(Model, id=obj_id)

    like, created = LikeModel.objects.get_or_create(
        **{field_name: obj, 'liker': user},
        defaults={'is_like': is_like})

    if not created:
        obj.rating -= 1 if like.is_like else -1
        if like.is_like != is_like:
            like.is_like = is_like
            like.save()
        else:
            like.delete()
            obj.save()
            return obj.rating

    obj.rating += 1 if is_like else -1
    obj.save()
    return obj.rating

def get_user_votes(objects, user, ids, is_question):
    user_votes = {}

    if user.is_authenticated:
        LikeModel = QuestionLike if is_question else AnswerLike
        field_name = 'question_id' if is_question else 'answer_id'

        user_votes = {
            getattr(like, field_name): like.is_like
            for like in LikeModel.objects.filter(liker=user, **{f'{field_name}__in': ids})
        }

    for obj in objects:
        obj.user_vote = user_votes.get(obj.id)

    return objects

def index(request):
    questions = Question.objects.recent()
    page = paginate(questions, request, 5)
    ids = [q.id for q in page.object_list]
    questions = [Question.objects.full_info(id) for id in ids]
    questions = get_user_votes(questions, request.user, ids, True)
    return render(request, 'new_questions.html', context={'questions': questions, 'page': page})

def hot(request):
    questions = Question.objects.popular()
    page = paginate(questions, request, 5)
    ids = [q.id for q in page.object_list]
    questions = [Question.objects.full_info(id) for id in ids]
    questions = get_user_votes(questions, request.user, ids, True)
    return render(request, 'hot_questions.html', context={'questions': questions, 'page': page})

def question(request, question_id):
    if request.method == 'POST':
        if not request.user.is_authenticated:
            return redirect('login')
        form = AnswerForm(request.POST, user=request.user, question_id=question_id)
        if form.is_valid():
            answer = form.save()
            return redirect(f"{reverse('question', args=[question_id])}#answer-{answer.id}")
    q = Question.objects.full_info(question_id)
    if not q:
        raise Http404("Question does not exist")
    q = get_user_votes([q], request.user, [question_id], True)[0]
    answers = Answer.objects.answers(q)
    answers = get_user_votes(answers, request.user, [a.id for a in answers], False)
    form = AnswerForm()
    return render(request, 'single_question.html', context={'question': q, 'answers': answers, 'form': form, 'user': request.user})

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
            user = form.save()
            auth.login(request, user)
            return redirect(reverse('edit'))
    else:
        form = RegisterForm()
    return render(request, 'register.html', {'form': form})

@login_required(login_url=reverse_lazy('login'))
def ask(request):
    if request.method == 'POST':
        form = AskQuestionForm(request.POST, user=request.user)
        if form.is_valid():
            question = form.save()
            return redirect(reverse('question', args=[question.id]))
    else:
        form = AskQuestionForm()
    return render(request, 'ask_question.html', {'form': form})

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

@require_POST
@login_required(login_url=reverse_lazy('login'))
def like(request):
    data = json.loads(request.body)
    object_id = data.get('object_id')
    is_like = data.get('is_like')
    is_question = data.get('is_question')

    rating = handle_like(object_id, request.user, is_like, True if is_question else False)

    return JsonResponse({'rating': rating})

@require_POST
def correct(request):
    data = json.loads(request.body)
    question = get_object_or_404(Question, id=data.get('question_id'))
    if question.questioner != request.user:
        raise PermissionDenied

    answer = get_object_or_404(Answer, id=data.get('answer_id'))
    if question.correct_answer != answer:
        question.correct_answer = answer
    else:
        question.correct_answer = None
    question.save()
    return JsonResponse({'success': True})