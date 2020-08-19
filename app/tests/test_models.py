from django.test import TestCase
from app.models import *


def create_user():
    user = User.objects.create_user(username='test',password='test')
    return user


class QuizTest(TestCase):
    @classmethod
    def setUpTestData(self):
        self.user = create_user()
        self.quiz = Quiz.objects.create(author=self.user, title='Test')

    def test_create_quiz(self):
        self.assertTrue(isinstance(self.quiz, Quiz), 'Should be of instance Quiz')
        self.assertEqual(self.quiz.title, 'Test', 'Should have same title name')
        self.assertTrue(self.quiz.created)
        self.assertTrue(self.quiz.modified)

    def test_get_quiz_by_created(self):
        # Testing for next and previous quiz of first quiz by created.
        self.assertRaises(Quiz.DoesNotExist, self.quiz.get_next_by_created)
        self.assertRaises(Quiz.DoesNotExist, self.quiz.get_previous_by_created)

        # Testing for next and previous quiz for the first and second quiz.
        quiz_2 = Quiz.objects.create(author=self.user, title='Test2')
        self.assertEqual(self.quiz.get_next_by_created().title, quiz_2.title, 'Should have next quiz by created date')
        self.assertEqual(quiz_2.get_previous_by_created().title, self.quiz.title, 'Should have previous quiz by created')
        self.assertRaises(Quiz.DoesNotExist, quiz_2.get_next_by_created)

    def test_get_quiz_by_modified(self):
        # Testing for next and previous quiz of first quiz by modified.
        quiz_2 = Quiz.objects.create(author=self.user, title='Test2')
        self.assertEqual(self.quiz.get_next_by_modified().title, quiz_2.title, 'Should have next quiz by modified date')
        self.assertEqual(quiz_2.get_previous_by_modified().title, self.quiz.title, 'Should have previous quiz by modified')

        # Testing for next and previous quiz for the first and second quiz by modified.
        self.quiz.title = 'Test1'
        self.quiz.save()
        self.assertEqual(quiz_2.get_next_by_modified().title, self.quiz.title, 'Should have next quiz by modified')
        self.assertEqual(self.quiz.get_previous_by_modified().title, quiz_2.title, 'Should have previous quiz by modified')
        self.assertRaises(Quiz.DoesNotExist, quiz_2.get_previous_by_modified)
        self.assertRaises(Quiz.DoesNotExist, self.quiz.get_next_by_modified)


class QuestionTest(TestCase):
    @classmethod
    def setUpTestData(self):
        self.user = create_user()
        self.quiz = Quiz.objects.create(author=self.user, title='Test')
        self.question = Question.objects.create(quiz=self.quiz, question='Question1')

    def test_get_question(self):
        # Testing for next and previous question of first question.
        self.assertEqual(self.question.get_previous_question(), None, 'Should have previous question to None')
        self.assertEqual(self.question.get_next_question(), None, 'Should have next question to None')

        question_2 = Question.objects.create(quiz=self.quiz, question='Question2')
        self.assertEqual(question_2.get_previous_question(), self.question, 'Should have previous question')
        self.assertEqual(question_2.get_next_question(), None, 'Should have next question')


class QuestionChoiceTest(TestCase):
    @classmethod
    def setUpTestData(self):
        self.user = create_user()
        self.quiz = Quiz.objects.create(author=self.user, title='Test')
        self.question = Question.objects.create(quiz=self.quiz, question='Question1')

    def test_question_choice(self):
        choice1 = QuestionChoice.objects.create(question=self.question, choice='Choice 1')
        self.assertEqual(choice1.is_correct, False,'Should have choice with is_correct boolean False')

        choice2 = QuestionChoice.objects.create(question=self.question, choice='Choice 2', is_correct=True)
        self.assertEqual(choice2.is_correct, True,'Should have choice with is_correct boolean True')

        choices = QuestionChoice.get_correct_choices(self.question.pk)
        self.assertEqual(choices.count(), 1,'Should have choices count 1')
        self.assertEqual(choices[0].choice, choice2.choice,'Should have same correct choices')

        choice2.is_correct = False
        choice2.save()
        self.assertEqual(choices.count(), 0,'Should have no correct choice with count 0')


class QuestionTestResultTest(TestCase):
    @classmethod
    def setUpTestData(self):
        self.user = create_user()
        self.quiz = Quiz.objects.create(author=self.user, title='Test')
        self.question = Question.objects.create(quiz=self.quiz, question='Question1')

    def test_quiz_test_result(self):
        result = QuizTestResult.objects.create(user=self.user, quiz=self.quiz, score=1)
        self.assertEqual(result.score, 1, 'Should have count 1')


class QuestionTestResultAnswerTest(TestCase):
    @classmethod
    def setUpTestData(self):
        self.user = create_user()
        self.quiz = Quiz.objects.create(author=self.user, title='Test')
        self.question = Question.objects.create(quiz=self.quiz, question='Question1')
        self.choice1 = QuestionChoice.objects.create(question=self.question, choice='Choice 1', is_correct=True)
        self.choice2 = QuestionChoice.objects.create(question=self.question, choice='Choice 2')
        self.choice3 = QuestionChoice.objects.create(question=self.question, choice='Choice 3')
        self.choice4 = QuestionChoice.objects.create(question=self.question, choice='Choice 4')
        self.result = QuizTestResult.objects.create(user=self.user, quiz=self.quiz, score=1)

    def test_quiz_test_result_answer(self):
        answer = QuizTestResultAnswer.objects.create(quiz_test=self.result, question=self.question, choice=self.choice1)
        self.assertEqual(answer.choice, self.choice1)
