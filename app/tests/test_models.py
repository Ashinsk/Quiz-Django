from django.test import TestCase
from app.models import *


def create_user():
    user = User.objects.create(username='ashin')
    user.set_password('ashin')
    user.save()
    return user


class QuizTest(TestCase):
    def setUp(self):
        self.user = create_user()

    def test_create_quiz(self):
        quiz = Quiz.objects.create(author=self.user,title='Test')
        self.assertTrue(isinstance(quiz,Quiz))
        self.assertEqual(quiz.title,'Test')
