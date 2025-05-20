from django.db import models
from django.contrib.auth.models import User
from django.db.models import Count

class QuestionManager(models.Manager):

    def full_info(self, question_id):
        return (
            self.get_queryset()
            .select_related('questioner')
            .filter(pk=question_id)
            .order_by('-id')
            .prefetch_related('tags')
            .annotate(answer_count=Count('answers'))
            .first()
        )

    def recent(self):
        return self.get_queryset().order_by('-id')

    def popular(self):
        return self.get_queryset().annotate(
            like_count=Count('likes', distinct=True)
        ).order_by('-like_count')

    def by_tag(self, tag_name):
        return self.get_queryset().prefetch_related('tags').filter(tags__name=tag_name)

class AnswerManager(models.Manager):
    def answer_with_full_info(self):
        return (self.get_queryset()
                .select_related('answerer'))

    def answers(self, question):
        return self.answer_with_full_info().filter(question=question)

class Question(models.Model):
    title = models.CharField(max_length=255)
    body = models.TextField()
    questioner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='questioner')
    rating = models.IntegerField(default=0)
    correct_answer = models.OneToOneField(
        'Answer',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='correct_answer'
    )

    objects = QuestionManager()

class Answer(models.Model):
    text = models.TextField()
    answerer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='answerer')
    question = models.ForeignKey('Question', on_delete=models.CASCADE, related_name='answers')
    rating = models.IntegerField(default=0)

    objects = AnswerManager()

class QuestionLike(models.Model):
    question = models.ForeignKey('Question', on_delete=models.CASCADE, related_name='likes')
    liker = models.ForeignKey(User, on_delete=models.CASCADE, related_name='liked_questions')
    is_like = models.BooleanField()

    class Meta:
        unique_together = ('question', 'liker')

class AnswerLike(models.Model):
    answer = models.ForeignKey('Answer', on_delete=models.CASCADE, related_name='likes')
    liker = models.ForeignKey(User, on_delete=models.CASCADE, related_name='liked_answers')
    is_like = models.BooleanField()

    class Meta:
        unique_together = ('answer', 'liker')

class Tag(models.Model):
    name = models.CharField(max_length=255)
    questions = models.ManyToManyField('Question', related_name='tags')

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    avatar = models.ImageField(upload_to='avatars')