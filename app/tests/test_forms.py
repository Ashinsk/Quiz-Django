from django.test import TestCase
from app.forms import *
from app.models import *


def create_user():
    user = User.objects.create(username='ashin')
    user.set_password('ashin')
    user.save()
    return user


class QuizFormTest(TestCase):
    def setUp(self):
        self.user = create_user()

    def test_valid_form(self):
        quiz = Quiz.objects.create(author=self.user, title='Test')
        data = {'author': quiz.author, 'title': quiz.title}
        form = QuizForm(data=data)
        self.assertTrue(form.is_valid())

    def test_invalid_form(self):
        quiz = Quiz.objects.create(author=self.user, title='Test')
        data = {'author': None, 'title': quiz.title}
        form = QuizForm(data=data)
        self.assertFalse(form.is_valid())
