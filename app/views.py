import copy
from django.core.paginator import Paginator
from django.shortcuts import render

QUESTIONS = [
    {
        'title': f"Title {i}",
        'id': i,
        'text': f"This is text for question {i}",
        "img_path": "images/avatar.png",
        'tags': ["python", "perl", "javascript", "react", "c#"],
    } for i in range(30)
]

def index(request):
    page_num = int(request.GET.get('page', 1))
    paginator = Paginator(QUESTIONS, 5)
    page = paginator.page(page_num)
    return render(request, 'new_questions.html', context={'questions': page.object_list, 'page': page})

def hot(request):
    q = list(reversed(copy.deepcopy(QUESTIONS)))
    page_num = int(request.GET.get('page', 1))
    paginator = Paginator(q, 5)
    page = paginator.page(page_num)
    return render(request, 'hot_questions.html', context={'questions': page.object_list, 'page': page})

def question(request, question_id):
    return render(request, 'single_question.html', context={'question': QUESTIONS[question_id]})

def tag(request, tag_name):
    filtered_questions = [q for q in QUESTIONS if tag_name in q['tags']]
    page_num = int(request.GET.get('page', 1))
    paginator = Paginator(filtered_questions, 5)
    page = paginator.page(page_num)
    return render(request, 'tag_questions.html', context={'questions': page.object_list, 'page': page, 'tag': tag_name})

def login(request):
    return render(request, 'login.html')

def signup(request):
    return render(request, 'register.html')

def ask(request):
    return render(request, 'ask_question.html')