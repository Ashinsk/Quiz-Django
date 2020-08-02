from django.db import models

class Quiz(models.Model):
    """
    Quiz class
    """
    title = models.CharField(max_length=100)

    def __str__(self):
        return str(self.title)

class Question(models.Model):
    """
    Questions for the quizzes.
    """
    quiz = models.ForeignKey(Quiz,on_delete=models.CASCADE,related_name='questions',related_query_name='question')
    question = models.CharField(max_length=1024)


class QuestionChoice(models.Model):
    """
    Choices for the questions
    """
    question = models.ForeignKey(Question,on_delete=models.CASCADE,related_name='question_choices')
    choice = models.CharField(max_length=1024)
    is_correct = models.BooleanField(default=False)

    @staticmethod
    def get_correct_choices(question_id):
        return QuestionChoice.objects.filter(question_id=question_id, is_correct=True)
