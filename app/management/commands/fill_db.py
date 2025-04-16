from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from app.models import Question, Answer, QuestionLike, AnswerLike, Tag, Profile
from django.db import transaction
import random
from faker import Faker

faker = Faker()

class Command(BaseCommand):
    help = 'Fill the database with test data'

    def add_arguments(self, parser):
        parser.add_argument('ratio', type=int, help='Multiplier for amount of data')

    @transaction.atomic
    def handle(self, *args, **kwargs):
        ratio = kwargs['ratio']

        num_users = ratio
        num_questions = ratio * 10
        num_answers = ratio * 100
        num_tags = ratio
        num_likes = ratio * 200

        self.stdout.write(self.style.SUCCESS('Starting to fill the database...'))

        # USERS
        users = []
        for i in range(num_users):
            username = f"{faker.user_name()}{i}"
            email = f"{faker.email().split('@')[0]}{i}@{faker.free_email_domain()}"
            user = User.objects.create_user(
                username=username,
                email=email,
                password='password'
            )
            Profile.objects.create(user=user, avatar='images/avatar.png')
            users.append(user)

        self.stdout.write(self.style.SUCCESS(f'Created {num_users} users and profiles.'))

        # TAGS
        tags = []
        for i in range(num_tags):
            tag = Tag.objects.create(name=f"{faker.word()}{i}")
            tags.append(tag)

        self.stdout.write(self.style.SUCCESS(f'Created {num_tags} tags.'))

        # QUESTIONS
        questions = []
        for _ in range(num_questions):
            question = Question.objects.create(
                title=faker.sentence(nb_words=6),
                body=faker.text(max_nb_chars=200),
                questioner=random.choice(users)
            )
            question.tags.set(random.sample(tags, k=min(3, len(tags))))  # Random tags
            questions.append(question)

        self.stdout.write(self.style.SUCCESS(f'Created {num_questions} questions.'))

        # ANSWERS
        answers = []
        for _ in range(num_answers):
            answer = Answer.objects.create(
                text=faker.text(max_nb_chars=100),
                answerer=random.choice(users),
                question=random.choice(questions)
            )
            answers.append(answer)

        self.stdout.write(self.style.SUCCESS(f'Created {num_answers} answers.'))

        # QUESTION LIKES
        for _ in range(num_likes):
            try:
                QuestionLike.objects.create(
                    question=random.choice(questions),
                    liker=random.choice(users)
                )
            except:
                pass

        self.stdout.write(self.style.SUCCESS(f'Created {num_likes} question likes.'))

        # ANSWER LIKES
        for _ in range(num_likes):
            try:
                AnswerLike.objects.create(
                    answer=random.choice(answers),
                    liker=random.choice(users)
                )
            except:
                pass

        self.stdout.write(self.style.SUCCESS(f'Created {num_likes} answer likes.'))

        self.stdout.write(self.style.SUCCESS('Database filled successfully!'))
