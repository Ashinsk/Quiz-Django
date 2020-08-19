import mixer
from django.test import TestCase
from app.forms import *
from app.models import *


def create_user():
    user = User.objects.create(username='ashin')
    user.set_password('ashin')
    user.save()
    return user


class QuizFormTest(TestCase):
    @classmethod
    def setUpTestData(self):
        self.user = create_user()

    def test_valid_form(self):
        data = {'author': self.user, 'title': 'Test'}
        form = QuizForm(data=data)
        self.assertTrue(form.is_valid())

    def test_invalid_form_when_no_data(self):
        data = {}
        form = QuizForm(data=data)
        self.assertFalse(form.is_valid())

    def test_invalid_form_when_no_author(self):
        data = {'author': None, 'title': 'Test'}
        form = QuizForm(data=data)
        self.assertFalse(form.is_valid())


class QuestionFormTest(TestCase):
    @classmethod
    def setUpTestData(self):
        self.user = create_user()
        self.quiz = Quiz.objects.create(title='Test', author=self.user)

    def test_valid_form(self):
        data = {
            'quiz': self.quiz.pk,
            'question': 'Question1',
            'choice1': 'A', 'choice2': 'B', 'choice3': 'C', 'choice4': 'D',
            'is_correct1': 'true', 'is_correct2': 'false', 'is_correct3': 'true', 'is_correct4': 'false'
        }
        form = QuestionForm(quiz_id=self.quiz.pk, data=data)
        self.assertTrue(form.is_valid())

    def test_invalid_form_when_no_data(self):
        data = {}
        form = QuestionForm(quiz_id=self.quiz.pk, data=data)
        self.assertFalse(form.is_valid())

    def test_invalid_form_when_no_correct_choice(self):
        data = {
            'quiz': self.quiz.pk,
            'question': 'Question1',
            'choice1': 'A', 'choice2': 'B', 'choice3': 'C', 'choice4': 'D',
            'is_correct1': 'false', 'is_correct2': 'false', 'is_correct3': 'false', 'is_correct4': 'false'
        }
        form = QuestionForm(quiz_id=self.quiz.pk, data=data)
        self.assertFalse(form.is_valid())

    def test_valid_form_when_update(self):
        question = Question.objects.create(quiz=self.quiz, question='Question 1')
        choice1 = QuestionChoice.objects.create(question=question, choice='Choice 1', is_correct=True)
        choice2 = QuestionChoice.objects.create(question=question, choice='Choice 2')
        choice3 = QuestionChoice.objects.create(question=question, choice='Choice 3')
        choice4 = QuestionChoice.objects.create(question=question, choice='Choice 4')
        form = QuestionForm(quiz_id=self.quiz.pk, question_id=question.pk)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.fields['choice1'].initial, choice1.choice)
        self.assertEqual(form.fields['choice2'].initial, choice2.choice)
        self.assertEqual(form.fields['choice3'].initial, choice3.choice)
        self.assertEqual(form.fields['choice4'].initial, choice4.choice)


class AnonymousUserFormTest(TestCase):
    def test_valid_form(self):
        data = {
            'name': 'Ashin',
            'email': 'ashin@email.com'
        }
        form = AnonymousUserForm(data=data)
        self.assertTrue(form.is_valid())

    def test_invalid_form_when_no_data(self):
        data = {}
        form = AnonymousUserForm(data=data)
        self.assertFalse(form.is_valid())

    def test_invalid_form_when_no_email(self):
        data = {
            'name': 'Ashin',
        }
        form = AnonymousUserForm(data=data)
        self.assertFalse(form.is_valid())

    def test_invalid_form_when_no_name(self):
        data = {
            'email': 'ashin@email.com'
        }
        form = AnonymousUserForm(data=data)
        self.assertFalse(form.is_valid())

    def test_invalid_form_when_invalid_email(self):
        data = {
            'name': 'Ashin',
            'email': 'ashin'
        }
        form = AnonymousUserForm(data=data)
        self.assertFalse(form.is_valid())
