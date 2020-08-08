from django.test import TestCase
from django.urls import reverse

from app.models import *
from app.views import *


def create_user():
    user = User.objects.create(username='ashin')
    user.set_password('ashin')
    user.save()
    return user


class QuizListTest(TestCase):
    def setUp(self):
        self.user = create_user()

    def test_quiz_list(self):
        url = reverse('app:QuizList')
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.resolver_match.func.__name__,QuizList.as_view().__name__)
        self.assertEqual(len(response.context['quizzes']), 0)
        self.assertNotEqual(len(response.context['quizzes']), 1)
