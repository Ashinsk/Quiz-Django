from django.test import TestCase
from django.urls import reverse

from app.models import *
from app.views import *


def create_user():
    user = User.objects.create_user(username='test', password='test')
    return user


class IndexTest(TestCase):
    @classmethod
    def setUpTestData(self):
        self.index_url = reverse('app:Index')
        self.user = create_user()

    def test_index(self):
        response = self.client.get(self.index_url)
        self.assertEqual(response.resolver_match.func.__name__, Index.as_view().__name__)
        self.assertEqual(response.status_code, 200)
        self.assertEqual('quizzes' in response.context, True)
        self.assertTemplateUsed(response, 'app/index.html')

    def test_index_quizzes_with_empty_quiz(self):
        # Testing empty quiz
        response = self.client.get(self.index_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['quizzes']), Quiz.objects.filter(is_published=True).count())

    def test_index_quizzes_with_single_unpublished_quiz(self):
        # Testing with single unpublished quiz
        Quiz.objects.create(title='Hello', author=self.user)
        response = self.client.get(self.index_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['quizzes']), Quiz.objects.filter(is_published=True).count())

    def test_index_quizzes_with_single_published_quiz(self):
        # Testing with single published quiz
        Quiz.objects.create(title='Hello', author=self.user, is_published=True)
        response = self.client.get(self.index_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['quizzes']), Quiz.objects.filter(is_published=True).count())


class QuizCreateTest(TestCase):
    @classmethod
    def setUpTestData(self):
        self.user = create_user()
        self.quiz_create_url = reverse('app:QuizCreate')

    def test_quiz_create_get_when_no_login(self):
        response = self.client.get(self.quiz_create_url)
        self.assertEqual(response.resolver_match.func.__name__, QuizCreate.as_view().__name__)
        self.assertEqual(response.status_code, 302)

    def test_quiz_create_get_when_login(self):
        self.client.login(username='test', password='test')
        response = self.client.get(self.quiz_create_url)
        self.assertEqual(response.status_code, 200)
        self.assertTrue('form' in response.context)
        self.assertTemplateUsed(response, 'app/quiz/quiz_create.html')

    def test_quiz_create_post_when_no_login(self):
        response = self.client.post(self.quiz_create_url, {'title': 'Quiz', 'author': self.user.pk})
        self.assertEqual(response.status_code, 302)

    def test_quiz_create_post_when_login(self):
        self.client.login(username='test', password='test')
        response = self.client.post(self.quiz_create_url, {'title': 'Quiz', 'author': self.user.pk})
        self.assertRedirects(response, reverse_lazy('app:QuestionCreate', kwargs={'quiz_id': Quiz.objects.first().pk}), 302, 200)
        self.assertEqual(Quiz.objects.all().count(), 1)


class QuizUpdateTest(TestCase):
    @classmethod
    def setUpTestData(self):
        self.user = create_user()
        self.quiz = Quiz.objects.create(title='Test', author=self.user)
        self.quiz_update_url = reverse('app:QuizUpdate', kwargs={"quiz_id": self.quiz.pk})

    def test_quiz_create_get(self):
        # Testing when not logged in.
        response = self.client.get(self.quiz_update_url)
        self.assertEqual(response.resolver_match.func.__name__, QuizUpdate.as_view().__name__)
        self.assertEqual(response.status_code, 302)

        # Testing with logged in.
        self.client.login(username='test', password='test')
        response = self.client.get(self.quiz_update_url)
        self.assertEqual(response.status_code, 200)
        self.assertTrue('form' in response.context)
        self.assertTemplateUsed(response, 'app/quiz/quiz_create.html')

    def test_quiz_create_post(self):
        # Testing when not logged in.
        response = self.client.post(self.quiz_update_url, {'title': 'Quiz 2', 'author': self.user.pk})
        self.assertEqual(response.status_code, 302)

        # Testing with logged in.
        self.client.login(username='test', password='test')
        response = self.client.post(self.quiz_update_url, {'title': 'Quiz', 'author': self.user.pk})
        self.assertRedirects(response, reverse_lazy('app:QuizDetail', kwargs={'quiz_id': self.quiz.pk}), 302, 200)
        self.quiz.refresh_from_db()
        self.assertEqual(self.quiz.title, 'Quiz')


class QuizListTest(TestCase):
    @classmethod
    def setUpTestData(self):
        self.user = create_user()
        self.quiz_list_url = reverse('app:QuizList')

    def test_quiz_list(self):
        response = self.client.get(self.quiz_list_url)
        self.assertEqual(response.resolver_match.func.__name__, QuizList.as_view().__name__)
        self.assertEqual(response.status_code, 200)
        self.assertEqual('quizzes' in response.context, True)
        self.assertTemplateUsed(response, 'app/quiz/quiz_list.html')

    def test_quiz_list_quizzes(self):
        # Testing empty quiz
        response = self.client.get(self.quiz_list_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['quizzes']), Quiz.objects.all().count())

        # Testing with single unpublished quiz
        Quiz.objects.create(title='Hello', author=self.user)
        response = self.client.get(self.quiz_list_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['quizzes']), Quiz.objects.filter(is_published=True).count())

        # Testing with single published quiz with no questions
        quiz = Quiz.objects.create(title='Hello', author=self.user, is_published=True)
        response = self.client.get(self.quiz_list_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['quizzes']), Quiz.objects.filter(is_published=True, question__isnull=False).count())

        # Testing with single published quiz with questions
        Question.objects.create(quiz=quiz, question='Hi')
        response = self.client.get(self.quiz_list_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['quizzes']), Quiz.objects.filter(is_published=True, question__isnull=False).count())


class QuizDetailTest(TestCase):
    @classmethod
    def setUpTestData(self):
        self.user = create_user()
        self.quiz = Quiz.objects.create(title='Hello', author=self.user)

    def test_quiz_detail(self):
        url = reverse('app:QuizDetail', kwargs={'quiz_id': self.quiz.id})
        response = self.client.get(url)
        self.assertEqual(response.resolver_match.func.__name__, QuizDetail.as_view().__name__)
        self.assertEqual(response.status_code, 200)
        self.assertEqual('quiz' in response.context, True)
        self.assertTemplateUsed(response, 'app/quiz/quiz_detail.html')

    def test_quiz_detail_quiz(self):
        url = reverse('app:QuizDetail', kwargs={'quiz_id': self.quiz.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        # Testing with non existing quiz_id
        url = reverse('app:QuizDetail', kwargs={'quiz_id': 2})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)


class UserAuthorQuizListTest(TestCase):
    @classmethod
    def setUpTestData(self):
        self.user = create_user()
        self.quiz_list_url = reverse('app:UserAuthorQuizList')

    def test_quiz_list(self):
        # Testing when not logged in.
        response = self.client.get(self.quiz_list_url)
        self.assertEqual(response.resolver_match.func.__name__, UserAuthorQuizList.as_view().__name__)
        self.assertEqual(response.status_code, 302)

        # Testing with logged in.
        self.client.login(username='test', password='test')
        response = self.client.get(self.quiz_list_url)
        self.assertEqual(response.status_code, 200)

        self.assertEqual('quizzes' in response.context, True)
        self.assertTemplateUsed(response, 'app/quiz/user_author_quiz_list.html')

    def test_quiz_list_quizzes(self):
        self.client.login(username='test', password='test')

        # Testing empty quiz
        response = self.client.get(self.quiz_list_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['quizzes']), Quiz.objects.filter(author=self.user).count())

        # Testing with single unpublished quiz
        Quiz.objects.create(title='Hello', author=self.user)
        response = self.client.get(self.quiz_list_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['quizzes']), Quiz.objects.filter(author=self.user).count())


class QuizPublishTest(TestCase):
    @classmethod
    def setUpTestData(self):
        self.user = create_user()
        self.quiz = Quiz.objects.create(title='Test', author=self.user)
        self.quiz_publish_url = reverse('app:quiz_publish', kwargs={'quiz_id': self.quiz.pk})

    def test_quiz_publish_when_no_login(self):
        response = self.client.get(self.quiz_publish_url)
        self.assertEqual(response.status_code, 302)

    def test_quiz_publish_when_login(self):
        self.client.login(username='test', password='test')

        # Testing with quiz with no questions.
        response = self.client.get(self.quiz_publish_url)
        self.assertEqual(self.quiz.is_published, False)
        self.assertRedirects(response, reverse_lazy('app:QuizDetail', kwargs={'quiz_id': self.quiz.pk}), 302, 200)

        # Testing with non authored user.
        quiz_2 = Quiz.objects.create(title='Test')
        response = self.client.get(self.quiz_publish_url)
        self.assertEqual(quiz_2.is_published, False)
        self.assertRedirects(response, reverse_lazy('app:QuizDetail', kwargs={'quiz_id': self.quiz.pk}), 302, 200)

        # Testing with quiz with questions.
        Question.objects.create(question='What is?', quiz=self.quiz)
        response = self.client.get(self.quiz_publish_url)
        self.quiz.refresh_from_db()
        self.assertEqual(self.quiz.is_published, True)
        self.assertIsNotNone(self.quiz.published_date)
        self.assertRedirects(response, reverse_lazy('app:QuizDetail', kwargs={'quiz_id': self.quiz.pk}), 302, 200)


class QuizDeleteTest(TestCase):
    @classmethod
    def setUpTestData(self):
        self.user = create_user()
        self.quiz = Quiz.objects.create(title='Test', author=self.user)
        self.quiz_delete = reverse('app:quiz_delete', kwargs={'quiz_id': self.quiz.pk})

    def test_quiz_delete_when_no_login(self):
        response = self.client.get(self.quiz_delete)
        self.assertEqual(response.resolver_match.func.__name__, quiz_delete.__name__)
        self.assertEqual(response.status_code, 302)

    def test_quiz_delete_when_login(self):
        self.client.login(username='test', password='test')
        response = self.client.get(self.quiz_delete)
        self.assertFalse(Quiz.objects.filter(pk=self.quiz.pk).exists())
        self.assertRedirects(response, reverse_lazy('app:UserAuthorQuizList'), 302, 200)


class QuestionCreateTest(TestCase):
    @classmethod
    def setUpTestData(self):
        self.user = create_user()
        self.quiz = Quiz.objects.create(title='Test', author=self.user)
        self.question_create_url = reverse('app:QuestionCreate', kwargs={'quiz_id': self.quiz.pk})
        self.question_data = {
            'quiz': self.quiz.pk,
            'question': 'Question1',
            'choice1': 'A', 'choice2': 'B', 'choice3': 'C', 'choice4': 'D',
            'is_correct1': 'false', 'is_correct2': 'false', 'is_correct3': 'true', 'is_correct4': 'false'
        }

    def test_question_create_get_when_no_login(self):
        response = self.client.get(self.question_create_url)
        self.assertEqual(response.resolver_match.func.__name__, QuestionCreate.as_view().__name__)
        self.assertEqual(response.status_code, 302)

    def test_question_create_get_when_login(self):
        self.client.login(username='test', password='test')
        response = self.client.get(self.question_create_url)
        self.assertEqual(response.status_code, 200)
        self.assertTrue('form' in response.context)
        self.assertTrue('quiz' in response.context)
        self.assertTemplateUsed(response, 'app/quiz/question_create.html')

    def test_question_create_post_when_no_login(self):
        response = self.client.post(self.question_create_url, self.question_data)
        self.assertEqual(response.status_code, 302)

    def test_question_create_post_with_data(self):
        self.client.login(username='test', password='test')
        response = self.client.post(self.question_create_url, self.question_data)
        self.assertRedirects(response, reverse_lazy('app:QuizDetail', kwargs={'quiz_id': self.quiz.pk}), 302, 200)
        self.assertEqual(self.quiz.questions.count(), 1)

    def test_question_create_post_with_no_data(self):
        self.client.login(username='test', password='test')
        response = self.client.post(self.question_create_url, {})
        self.assertTrue('form' in response.context)
        self.assertTrue(len(response.context['form'].errors) > 0)


class QuestionUpdateTest(TestCase):
    @classmethod
    def setUpTestData(self):
        self.user = create_user()
        self.quiz = Quiz.objects.create(title='Test', author=self.user)
        self.question = Question.objects.create(quiz=self.quiz, question='Question1')
        self.choice1 = QuestionChoice.objects.create(question=self.question, choice='Choice 1', is_correct=True)
        self.choice2 = QuestionChoice.objects.create(question=self.question, choice='Choice 2')
        self.choice3 = QuestionChoice.objects.create(question=self.question, choice='Choice 3')
        self.choice4 = QuestionChoice.objects.create(question=self.question, choice='Choice 4')
        self.question_update_url = reverse('app:QuestionUpdate', kwargs={'quiz_id': self.quiz.pk, 'question_id': self.question.pk})

    def test_question_update_get_when_no_login(self):
        response = self.client.get(self.question_update_url)
        self.assertEqual(response.resolver_match.func.__name__, QuestionUpdate.as_view().__name__)
        self.assertEqual(response.status_code, 302)

    def test_question_update_get_when_login(self):
        self.client.login(username='test', password='test')
        response = self.client.get(self.question_update_url)
        self.assertEqual(response.status_code, 200)
        self.assertTrue('form' in response.context)
        self.assertTrue('quiz' in response.context)
        self.assertTemplateUsed(response, 'app/quiz/question_create.html')

    def test_question_update_post_when_no_login(self):
        response = self.client.post(self.question_update_url, {})
        self.assertEqual(response.status_code, 302)

    def test_question_update_post_with_data(self):
        self.client.login(username='test', password='test')
        data = {
            'quiz': self.quiz.pk,
            'question': 'Question12',
            'choice1': 'A', 'choice2': 'B', 'choice3': 'C', 'choice4': 'D',
            'is_correct1': 'true', 'is_correct2': 'false', 'is_correct3': 'true', 'is_correct4': 'false'
        }
        response = self.client.post(self.question_update_url, data)
        self.assertRedirects(response, reverse_lazy('app:QuizDetail', kwargs={'quiz_id': self.quiz.pk}), 302, 200)
        self.assertEqual(self.quiz.questions.count(), 1)

    def test_question_update_post_with_no_correct_choice(self):
        self.client.login(username='test', password='test')
        data = {
            'quiz': self.quiz.pk,
            'question': 'Question12',
            'choice1': 'A', 'choice2': 'B', 'choice3': 'C', 'choice4': 'D',
            'is_correct1': 'false', 'is_correct2': 'false', 'is_correct3': 'false', 'is_correct4': 'false'
        }
        response = self.client.post(self.question_update_url, data)
        self.assertTrue('form' in response.context)
        self.assertTrue(len(response.context['form'].errors) > 0)

    def test_question_upate_post_with_no_data(self):
        self.client.login(username='test', password='test')
        response = self.client.post(self.question_update_url, {})
        self.assertTrue('form' in response.context)
        self.assertTrue(len(response.context['form'].errors) > 0)


class QuestionDeleteTest(TestCase):
    @classmethod
    def setUpTestData(self):
        self.user = create_user()
        self.quiz = Quiz.objects.create(title='Test', author=self.user)
        self.question = Question.objects.create(quiz=self.quiz, question='Question1')
        self.question_delete = reverse('app:question_delete', kwargs={'quiz_id': self.quiz.pk, 'question_id': self.question.pk})

    def test_quiz_delete_when_no_login(self):
        response = self.client.get(self.question_delete)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.resolver_match.func.__name__, question_delete.__name__)

    def test_quiz_delete_when_login(self):
        self.client.login(username='test', password='test')
        response = self.client.get(self.question_delete)
        self.assertFalse(Question.objects.filter(pk=self.quiz.pk).exists())
        self.assertRedirects(response, reverse_lazy('app:QuizDetail', kwargs={'quiz_id': self.quiz.pk}), 302, 200)


class AnonymousUserFormViewTest(TestCase):
    @classmethod
    def setUpTestData(self):
        self.user = create_user()
        self.quiz = Quiz.objects.create(title='Test', author=self.user)
        self.form_url = reverse('app:AnonymousUserForm') + '?quiz_id=' + str(self.quiz.pk)

    def test_anonymous_user_get(self):
        response = self.client.get(self.form_url)
        self.assertEqual(response.status_code, 200)
        self.assertTrue('form' in response.context)
        self.assertTemplateUsed(response, 'app/anonymous_user_form.html')

    def test_anonymous_user_post_data(self):
        data = {
            'name': 'Ashin',
            'email': 'ashin@gmail.com'
        }
        response = self.client.post(self.form_url, data)
        self.assertRedirects(response, reverse_lazy('app:QuizTest', kwargs={'quiz_id': self.quiz.pk}) + '?anonymous=' + str(True) + '&name=' + data['name'] + '&email=' + data['email'],
                             302, 200)

    def test_anonymous_user_post_no_data(self):
        response = self.client.post(self.form_url, {})
        self.assertTrue('form' in response.context)
        self.assertTrue(len(response.context['form'].errors) > 0)


class QuizTestTest(TestCase):
    @classmethod
    def setUpTestData(self):
        self.user = create_user()
        self.quiz = Quiz.objects.create(title='Test', author=self.user)
        self.question = Question.objects.create(question='Test', quiz=self.quiz)
        self.choice1 = QuestionChoice.objects.create(question=self.question, choice='Choice 1', is_correct=True)
        self.choice2 = QuestionChoice.objects.create(question=self.question, choice='Choice 2')
        self.choice3 = QuestionChoice.objects.create(question=self.question, choice='Choice 3')
        self.choice4 = QuestionChoice.objects.create(question=self.question, choice='Choice 4')
        self.form_url = reverse('app:QuizTest', kwargs={'quiz_id': self.quiz.pk})

    def test_quiz_test_get_no_login(self):
        response = self.client.get(self.form_url)
        self.assertEqual(response.resolver_match.func.__name__, QuizTest.as_view().__name__)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse_lazy('app:AnonymousUserForm') + '?quiz_id=' + str(self.quiz.pk), 302, 200)

    def test_quiz_test_get_login(self):
        self.client.login(username='test', password='test')
        response = self.client.get(self.form_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'app/quiz/quiz_test_form.html')

    def test_quiz_test_get_anonymous(self):
        data = {
            'name': 'Ashin',
            'email': 'ashin@gmail.com'
        }
        response = self.client.get(self.form_url + '?anonymous=' + str(True) + '&name=' + data['name'] + '&email=' + data['email'])
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'app/quiz/quiz_test_form.html')

    def test_quiz_test_post_anonymous(self):
        query_param = {
            'name': 'Ashin',
            'email': 'ashin@gmail.com'
        }

        data = {
            self.question.pk: [self.choice1.pk]
        }

        response = self.client.post(self.form_url + '?anonymous=' + str(True) + '&name=' + query_param['name'] + '&email=' + query_param['email'], data)
        self.assertEqual(response.status_code, 302)

    def test_quiz_test_post_login(self):
        data = {
            self.question.pk: [self.choice1.pk]
        }
        self.client.login(username='test', password='test')
        response = self.client.post(self.form_url, data)
        self.assertRedirects(response, reverse_lazy('app:QuizResultList'), 302, 200)
        self.assertTrue(QuizTestResult.objects.count() == 1)


class QuizResultListTest(TestCase):
    @classmethod
    def setUpTestData(self):
        self.user = create_user()
        self.quiz_list_url = reverse('app:QuizResultList')

    def test_quiz_list_when_no_login(self):
        response = self.client.get(self.quiz_list_url)
        self.assertEqual(response.status_code, 302)

    def test_quiz_list_when_login(self):
        self.client.login(username='test', password='test')
        response = self.client.get(self.quiz_list_url)
        self.assertEqual(response.resolver_match.func.__name__, QuizResultList.as_view().__name__)
        self.assertEqual(response.status_code, 200)
        self.assertEqual('results' in response.context, True)
        self.assertTemplateUsed(response, 'app/quiz/quiz_result_list.html')

    def test_quiz_list_results(self):
        self.client.login(username='test', password='test')
        response = self.client.get(self.quiz_list_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['results']), QuizTestResult.objects.filter(user=self.user).count())


class UserAuthorQuizTestResultListTest(TestCase):
    @classmethod
    def setUpTestData(self):
        self.user = create_user()
        self.quiz = Quiz.objects.create(question='Quiz 1', author=self.user)
        self.quiz_list_url = reverse('app:UserAuthorQuizTestResultList', kwargs={'quiz_id': self.quiz.pk})

    def test_quiz_result_list_when_no_login(self):
        response = self.client.get(self.quiz_list_url)
        self.assertEqual(response.status_code, 302)

    def test_quiz_result_list_when_login(self):
        self.client.login(username='test', password='test')
        response = self.client.get(self.quiz_list_url)
        self.assertEqual(response.resolver_match.func.__name__, UserAuthorQuizTestResultList.as_view().__name__)
        self.assertEqual(response.status_code, 200)
        self.assertEqual('results' in response.context, True)
        self.assertEqual('quiz' in response.context, True)
        self.assertTemplateUsed(response, 'app/quiz/user_author_quiz_test_result_list.html')

    def test_quiz_result_list_results(self):
        self.client.login(username='test', password='test')
        response = self.client.get(self.quiz_list_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['results']), QuizTestResult.objects.filter(quiz=self.quiz.pk, quiz__author=self.user).count())


class QuizResultExportTest(TestCase):
    @classmethod
    def setUpTestData(self):
        self.user = create_user()
        self.quiz = Quiz.objects.create(title='Quiz 1', author=self.user)
        self.export_csv = reverse('app:quiz_result_export', kwargs={'quiz_id': self.quiz.pk, 'filetype': 'csv'})
        self.export_xlsx = reverse('app:quiz_result_export', kwargs={'quiz_id': self.quiz.pk, 'filetype': 'xlsx'})
        self.export_pdf = reverse('app:quiz_result_export', kwargs={'quiz_id': self.quiz.pk, 'filetype': 'pdf'})
        self.export_docx = reverse('app:quiz_result_export', kwargs={'quiz_id': self.quiz.pk, 'filetype': 'docx'})

    def test_quiz_result_export_when_no_login(self):
        response = self.client.get(self.export_csv)
        self.assertEqual(response.status_code, 302)

    def test_quiz_export_list_when_login(self):
        self.client.login(username='test', password='test')
        response = self.client.get(self.export_csv)
        self.assertEqual(response.resolver_match.func.__name__, quiz_result_export.__name__)
        self.assertEqual(response.status_code, 200)

        response = self.client.get(self.export_xlsx)
        self.assertEqual(response.resolver_match.func.__name__, quiz_result_export.__name__)
        self.assertEqual(response.status_code, 200)

        response = self.client.get(self.export_docx)
        self.assertEqual(response.resolver_match.func.__name__, quiz_result_export.__name__)
        self.assertEqual(response.status_code, 200)

        response = self.client.get(self.export_pdf)
        self.assertEqual(response.resolver_match.func.__name__, quiz_result_export.__name__)


class QuizResultAnswerTest(TestCase):
    @classmethod
    def setUpTestData(self):
        self.user = create_user()
        self.quiz = Quiz.objects.create(title='Quiz 1', author=self.user)
        self.result = QuizTestResult.objects.create(quiz=self.quiz, user=self.user, score=1)
        self.quiz_result_answer_url = reverse('app:QuizResultAnswer', kwargs={'result_id': self.result.pk})

    def test_quiz_list_when_no_login(self):
        response = self.client.get(self.quiz_result_answer_url)
        self.assertEqual(response.status_code, 302)

    def test_quiz_list_when_login(self):
        self.client.login(username='test', password='test')
        response = self.client.get(self.quiz_result_answer_url)
        self.assertEqual(response.resolver_match.func.__name__, QuizResultAnswer.as_view().__name__)
        self.assertEqual(response.status_code, 200)
        self.assertEqual('result' in response.context, True)
        self.assertEqual('answers' in response.context, True)
        self.assertTemplateUsed(response, 'app/quiz/quiz_result_answer.html')
