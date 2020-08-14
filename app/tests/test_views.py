from django.test import TestCase
from django.urls import reverse

from app.models import *
from app.views import *


def create_user():
    user = User.objects.create(username='test')
    user.set_password('test')
    user.save()
    return user


class IndexTest(TestCase):
    def setUp(self):
        self.index_url = reverse('app:Index')
        self.user = create_user()

    def test_index(self):
        response = self.client.get(self.index_url)
        self.assertEqual(response.resolver_match.func.__name__, Index.as_view().__name__)
        self.assertEqual(response.status_code, 200)
        self.assertEqual('quizzes' in response.context, True)
        self.assertTemplateUsed('app/index.html')

    def test_index_quizzes(self):
        # Testing empty quiz
        response = self.client.get(self.index_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['quizzes']), 0)
        self.assertNotEqual(len(response.context['quizzes']), 1)

        # Testing with single unpublished quiz
        Quiz.objects.create(title='Hello', author=self.user)
        response = self.client.get(self.index_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['quizzes']), 0)
        self.assertNotEqual(len(response.context['quizzes']), 1)

        # Testing with single published quiz
        Quiz.objects.create(title='Hello', author=self.user, is_published=True)
        response = self.client.get(self.index_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['quizzes']), 1)
        self.assertNotEqual(len(response.context['quizzes']), 0)


class QuizListTest(TestCase):
    def setUp(self):
        self.user = create_user()
        self.quiz_list_url = reverse('app:QuizList')

    def test_quiz_list(self):
        response = self.client.get(self.quiz_list_url)
        self.assertEqual(response.resolver_match.func.__name__,QuizList.as_view().__name__)
        self.assertEqual(response.status_code, 200)
        self.assertEqual('quizzes' in response.context, True)
        self.assertTemplateUsed('app/quiz/quiz_list.html')

    def test_quiz_list_quizzes(self):
        # Testing empty quiz
        response = self.client.get(self.quiz_list_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['quizzes']), 0)
        self.assertNotEqual(len(response.context['quizzes']), 1)

        # Testing with single unpublished quiz
        Quiz.objects.create(title='Hello', author=self.user)
        response = self.client.get(self.quiz_list_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['quizzes']), 0)
        self.assertNotEqual(len(response.context['quizzes']), 1)

        # Testing with single published quiz with no questions
        quiz = Quiz.objects.create(title='Hello', author=self.user, is_published=True)
        response = self.client.get(self.quiz_list_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['quizzes']), 0)
        self.assertNotEqual(len(response.context['quizzes']), 1)

        # Testing with single published quiz with questions
        Question.objects.create(quiz=quiz,question='Hi')
        response = self.client.get(self.quiz_list_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['quizzes']), 1)
        self.assertNotEqual(len(response.context['quizzes']), 0)


class QuizDetailTest(TestCase):
    def setUp(self):
        self.user = create_user()
        self.quiz = Quiz.objects.create(title='Hello', author=self.user)

    def test_quiz_detail(self):
        url = reverse('app:QuizDetail', kwargs={'quiz_id': self.quiz.id})
        response = self.client.get(url)
        self.assertEqual(response.resolver_match.func.__name__,QuizDetail.as_view().__name__)
        self.assertEqual(response.status_code, 200)
        self.assertEqual('quiz' in response.context, True)
        self.assertTemplateUsed('app/quiz/quiz_detail.html')


    def test_quiz_detail_quiz(self):
        url = reverse('app:QuizDetail', kwargs={'quiz_id': self.quiz.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        # Testing with non existing quiz_id
        url = reverse('app:QuizDetail',kwargs={'quiz_id': 2})
        response = self.client.get(url)
        self.assertEqual(response.status_code,404)


class QuizCreateTest(TestCase):
    def setUp(self):
        self.user = create_user()

