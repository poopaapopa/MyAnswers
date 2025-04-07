import copy
from django.core.paginator import Paginator
from django.shortcuts import render

QUESTIONS = [
    {
        'title': f"Title {i}",
        'id': i,
        'text': f"I have a question regarding R function syntax. "
                f"I've noticed that the following function works fine without curly braces. "
                f"This is text for question {i}",
        "img_path": "images/avatar.png",
        'tags': ["python", "perl", "javascript", "react", "c#"],
        'rating': 5,
    } for i in range(30)
]

ANSWERS = [
    {
        'id': i,
        'text': f"The general format of a function is a header followed by a single statement that makes up the body of the function. "
                f"Using braces around several statements makes them appear to the parser as a single statement. "
                f"This is text for answer {i}",
        "img_path": "images/avatar.png",
    } for i in range(3)
]

def paginate(objects_list, request, per_page=10):
    page_num = int(request.GET.get('page', 1))
    paginator = Paginator(objects_list, per_page)
    page = paginator.page(page_num)
    return page

def index(request):
    page = paginate(QUESTIONS, request, 5)
    return render(request, 'new_questions.html', context={'questions': page.object_list, 'page': page})

def hot(request):
    q = list(reversed(copy.deepcopy(QUESTIONS)))
    page = paginate(q, request, 5)
    return render(request, 'hot_questions.html', context={'questions': page.object_list, 'page': page})

def question(request, question_id):
    return render(request, 'single_question.html', context={'question': QUESTIONS[question_id], 'answers': ANSWERS})

def tag(request, tag_name):
    filtered_questions = [q for q in QUESTIONS if tag_name in q['tags']]
    page = paginate(filtered_questions, request, 5)
    return render(request, 'tag_questions.html', context={'questions': page.object_list, 'page': page, 'tag': tag_name})

def login(request):
    return render(request, 'login.html')

def signup(request):
    return render(request, 'register.html')

def ask(request):
    return render(request, 'ask_question.html')