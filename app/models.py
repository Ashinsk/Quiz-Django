from django.contrib.auth.models import User
from django.db import models


class Quiz(models.Model):
    """
    Quizzes
    """
    author = models.ForeignKey(User,on_delete=models.CASCADE,null=True)
    title = models.CharField(max_length=100)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.title)


class Question(models.Model):
    """
    Questions for the quizzes.
    """
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='questions',related_query_name='question')
    question = models.CharField(max_length=1024)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)


class QuestionChoice(models.Model):
    """
    Choices for the questions.
    """
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='question_choices',related_query_name='question_choice')
    choice = models.CharField(max_length=1024)
    is_correct = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    @staticmethod
    def get_correct_choices(question_id):
        """
        Get the correct choice for the question.

        :param question_id: PK value of the question.
        :return: QuestionChoice instance of the correct choice for the question.
        """
        return QuestionChoice.objects.filter(question_id=question_id, is_correct=True)


class QuizTestResult(models.Model):
    """
    Results of quizzes.
    """
    user = models.ForeignKey(User,on_delete=models.CASCADE,null=True)
    quiz = models.ForeignKey(Quiz,on_delete=models.CASCADE,related_name='quiz_test_results',related_query_name='quiz_test_result')
    score = models.IntegerField(default=0)
    created = models.DateTimeField(auto_now_add=True)



