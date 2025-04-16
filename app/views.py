from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404
from app.models import Question, Answer
from django.http import Http404

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
    return render(request, 'login.html')

def signup(request):
    return render(request, 'register.html')

def ask(request):
    return render(request, 'ask_question.html')