from django.test import TestCase
from django.urls import reverse, resolve


class IndexTest(TestCase):
    def test_index_url(self):
        url = reverse('app:Index')
        self.assertEqual(resolve(url).view_name,'app:Index')


class QuizTestUrls(TestCase):
    def test_quiz_list_url(self):
        url = reverse('app:QuizList')
        self.assertEqual(resolve(url).view_name,'app:QuizList')

    def test_quiz_list_author_url(self):
        url = reverse('app:UserAuthorQuizList')
        self.assertEqual(resolve(url).view_name,'app:UserAuthorQuizList')

    def test_quiz_create_url(self):
        url = reverse('app:QuizCreate')
        self.assertEqual(resolve(url).view_name,'app:QuizCreate')

    def test_quiz_update_url(self):
        url = reverse('app:QuizUpdate',kwargs={'quiz_id':1})
        self.assertEqual(resolve(url).view_name,'app:QuizUpdate')

    def test_quiz_detail_url(self):
        url = reverse('app:QuizDetail',kwargs={'quiz_id':1})
        self.assertEqual(resolve(url).view_name,'app:QuizDetail')

    def test_quiz_delete_url(self):
        url = reverse('app:quiz_delete',kwargs={'quiz_id':1})
        self.assertEqual(resolve(url).func.__name__,'quiz_delete')

    def test_quiz_publish_url(self):
        url = reverse('app:quiz_publish', kwargs={'quiz_id': 1})
        self.assertEqual(resolve(url).func.__name__, 'quiz_publish')


class QuestionTestUrl(TestCase):
    def test_question_create_url(self):
        url = reverse('app:QuestionCreate', kwargs={'quiz_id': 1})
        self.assertEqual(resolve(url).view_name, 'app:QuestionCreate')

    def test_question_update_url(self):
        url = reverse('app:QuestionUpdate', kwargs={'quiz_id': 1,'question_id':1})
        self.assertEqual(resolve(url).view_name, 'app:QuestionUpdate')

    def test_question_delete_url(self):
        url = reverse('app:question_delete', kwargs={'quiz_id': 1,'question_id':1})
        self.assertEqual(resolve(url).func.__name__, 'question_delete')


class QuizResultTestUrl(TestCase):
    def test_quiz_test_url(self):
        url = reverse('app:QuizTest', kwargs={'quiz_id': 1})
        self.assertEqual(resolve(url).view_name, 'app:QuizTest')

    def test_quiz_result_list_url(self):
        url = reverse('app:QuizResultList')
        self.assertEqual(resolve(url).view_name, 'app:QuizResultList')

    def test_quiz_test_result_list_url(self):
        url = reverse('app:UserAuthorQuizTestResultList', kwargs={'quiz_id': 1})
        self.assertEqual(resolve(url).view_name, 'app:UserAuthorQuizTestResultList')

    def test_quiz_result_list_export_url(self):
        url = reverse('app:quiz_result_export',kwargs={'quiz_id':1,'filetype':'csv'})
        self.assertEqual(resolve(url).func.__name__, 'quiz_result_export')

    def test_quiz_result_answer_url(self):
        url = reverse('app:QuizResultAnswer',kwargs={'result_id':1})
        self.assertEqual(resolve(url).view_name,'app:QuizResultAnswer')


class AnonymousUserFormTestUrl(TestCase):
    def test_anonymous_user_form(self):
        url = reverse('app:AnonymousUserForm')
        assert resolve(url).view_name == 'app:AnonymousUserForm'
