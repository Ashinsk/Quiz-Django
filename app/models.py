from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.utils import timezone
from simple_history.models import HistoricalRecords

class Quiz(models.Model):
    """
    Quizzes
    """
    author = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    title = models.CharField(max_length=100)
    is_published = models.BooleanField(default=False)
    published_date = models.DateTimeField(null=True)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    history = HistoricalRecords()

    def publish_quiz(self):
        self.is_published = True
        self.save()

    def unpublish_quiz(self):
        self.is_published = False
        self.save()

    def save(self, *args, **kwargs):
        if self.is_published:
            self.published_date = timezone.now()
        super().save(*args, **kwargs)

    def __str__(self):
        return str(self.title)


class Question(models.Model):
    """
    Questions for the quizzes.
    """
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='questions', related_query_name='question')
    question = models.CharField(max_length=1024)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    history = HistoricalRecords()

    def get_previous_question(self):
        try:
            q = self.get_previous_by_created()
        except Question.DoesNotExist:
            return None
        except Exception as e:
            raise e
        return q

    def get_next_question(self):
        try:
            q = self.get_next_by_created()
        except Question.DoesNotExist:
            return None
        except Exception as e:
            raise e
        return q


class QuestionChoice(models.Model):
    """
    Choices for the questions.
    """
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='question_choices', related_query_name='question_choice')
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
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, related_name='quiz_test_results', related_query_name='quiz_test_result')  # If user is null, it represents anonymous user.
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='quiz_test_results', related_query_name='quiz_test_result')
    score = models.IntegerField(default=0)
    created = models.DateTimeField(auto_now_add=True)

    def reevaluate_scores(self):
        if self.results_answers.exists():
            questions = self.quiz.questions.all()

            score = 0
            for question in questions:
                selected_choice = self.results_answers.filter(question=question).values_list('choice__pk', flat=True)
                correct_choices = QuestionChoice.get_correct_choices(question.pk).values_list('pk', flat=True)
                a = (set(selected_choice)).difference(set(correct_choices))
                if not a or not correct_choices:
                    score += 1

            return score
        else:
            raise ObjectDoesNotExist('Test result answers does not exist to re-evaluate.')


class QuizTestResultAnswer(models.Model):
    """
    Store results of quiz test.
    """
    quiz_test = models.ForeignKey(QuizTestResult, on_delete=models.CASCADE, related_name='results_answers', related_query_name='result_answer')
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='results_answers', related_query_name='result_answer')
    choice = models.ForeignKey(QuestionChoice, on_delete=models.CASCADE, related_name='results_answers', related_query_name='result_answer', help_text='Choice refers to the selected choice.')
