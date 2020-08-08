from django.test import TestCase
from django.urls import reverse, resolve


class TestUrls(TestCase):
    def test_quiz_list_url(self):
        url = reverse('app:QuizList')
        self.assertEqual(resolve(url).view_name,'app:QuizList')
