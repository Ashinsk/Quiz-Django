
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin
from django.core.mail import send_mail
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.shortcuts import render
from django.template.loader import get_template
from django.urls import reverse_lazy
from django.views.decorators.http import require_GET
from django.views.generic import TemplateView, CreateView, FormView, DetailView, UpdateView, ListView

from app.export import Export
from app.forms import *
from quiz.settings.base import logger


def response_404_handler(request, exception=None):
    return render(request, "app/errors/404.html", status=404)


class Index(TemplateView):
    """
    Index or Home view.
    """
    template_name = 'app/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['quizzes'] = Quiz.objects.filter(is_published=True).order_by('-created')
        return context


class QuizCreate(LoginRequiredMixin, CreateView):
    """
    Create Quiz.
    """
    template_name = 'app/quiz/quiz_create.html'
    form_class = QuizForm

    def get_success_url(self, **kwargs):
        return reverse_lazy('app:QuestionCreate', kwargs={'quiz_id': kwargs.get('quiz_id')})

    def get_initial(self):
        return {'author': self.request.user}

    def form_valid(self, form):
        form = form.save()
        messages.add_message(self.request, messages.SUCCESS, 'Quiz Created')
        return HttpResponseRedirect(self.get_success_url(quiz_id=form.pk))

    def form_invalid(self, form):
        # print(form.errors)
        logger.error(form.errors)
        messages.add_message(self.request, messages.ERROR, form.errors)
        return super().form_invalid(form)


class QuizUpdate(LoginRequiredMixin, UpdateView):
    """
    Update Quiz.
    """
    template_name = 'app/quiz/quiz_create.html'
    model = Quiz
    form_class = QuizForm
    pk_url_kwarg = 'quiz_id'

    def get_success_url(self):
        return reverse_lazy('app:QuizDetail', kwargs={'quiz_id': self.kwargs.get('quiz_id')})

    def form_valid(self, form):
        messages.add_message(self.request, messages.SUCCESS, 'Quiz Updated')
        return super().form_valid(form)


class QuizDetail(DetailView):
    """
    Detail of the quiz.
    """
    template_name = 'app/quiz/quiz_detail.html'
    model = Quiz
    pk_url_kwarg = 'quiz_id'
    context_object_name = 'quiz'


class QuizList(ListView):
    """
    View all quizzes.
    """
    template_name = 'app/quiz/quiz_list.html'
    model = Quiz
    context_object_name = 'quizzes'

    def get_queryset(self):
        return Quiz.objects.filter(question__isnull=False, is_published=True).order_by('-created')


class UserAuthorQuizList(LoginRequiredMixin, ListView):
    """
    View user quizzes.
    """
    template_name = 'app/quiz/user_author_quiz_list.html'
    model = Quiz
    context_object_name = 'quizzes'
    paginate_by = 10

    def get_queryset(self):
        return Quiz.objects.filter(author=self.request.user).order_by('-created')


@login_required
def quiz_publish(request, quiz_id):
    """
    Publish the quiz.

    :param request:
    :param quiz_id: PK value of the quiz.
    :return: Redirect to quiz detail.
    """
    quiz = get_object_or_404(Quiz, pk=quiz_id, author=request.user)
    if quiz.questions.count() > 0:
        quiz.is_published = True
        quiz.save()
        messages.add_message(request, messages.SUCCESS, 'Published successfully.')
    else:
        messages.add_message(request, messages.SUCCESS, 'Please add questions to publish.')

    return HttpResponseRedirect(reverse_lazy('app:QuizDetail', kwargs={'quiz_id': quiz_id}))


@login_required
def quiz_delete(request, quiz_id):
    """
    Delete the quiz.

    :param request:
    :param quiz_id: PK value of the quiz.
    :return: Redirect to index view.
    """
    quiz = get_object_or_404(Quiz, pk=quiz_id, author=request.user)
    quiz.delete()
    return HttpResponseRedirect(reverse_lazy('app:UserAuthorQuizList'))


class QuestionCreate(LoginRequiredMixin, FormView):
    """
    Create question for the quiz.
    """
    template_name = 'app/quiz/question_create.html'
    form_class = QuestionForm

    def get_success_url(self):
        return reverse_lazy('app:QuizDetail', kwargs={'quiz_id': self.kwargs.get('quiz_id')})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['quiz'] = Quiz.objects.get(pk=self.kwargs.get('quiz_id'))
        return context

    def get_form(self, form_class=None):
        if form_class is None:
            form_class = self.get_form_class()
        return form_class(self.kwargs['quiz_id'], **self.get_form_kwargs())

    def form_valid(self, form):
        form.save(self.kwargs['quiz_id'])
        messages.add_message(self.request, messages.SUCCESS, 'Question Added')
        return HttpResponseRedirect(self.get_success_url())

    def form_invalid(self, form):
        # print(form.errors)
        logger.error(form.errors)
        messages.add_message(self.request, messages.ERROR, 'Question Add Error')
        return super().form_invalid(form)


class QuestionUpdate(LoginRequiredMixin, FormView):
    """
    Update question for the quiz.
    """
    template_name = 'app/quiz/question_create.html'
    form_class = QuestionForm

    def get_success_url(self):
        return reverse_lazy('app:QuizDetail', kwargs={'quiz_id': self.kwargs.get('quiz_id')})

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['quiz'] = Quiz.objects.get(pk=self.kwargs.get('quiz_id'))
        return context

    def get_form(self, form_class=None):
        if form_class is None:
            form_class = self.get_form_class()
        return form_class(self.kwargs['quiz_id'], self.kwargs['question_id'], **self.get_form_kwargs())

    def form_valid(self, form):
        form.save(self.kwargs['quiz_id'], self.kwargs['question_id'])
        messages.add_message(self.request, messages.SUCCESS, 'Question Updated')
        return HttpResponseRedirect(self.get_success_url())

    def form_invalid(self, form):
        # print(form.errors)
        logger.error(form.errors)
        messages.add_message(self.request, messages.ERROR, 'Question Update Error')
        return super().form_invalid(form)


@login_required
def question_delete(request, quiz_id, question_id):
    """
    Delete the question for the quiz.

    :param quiz_id: PK value of the quiz.
    :param question_id: PK value of the question.
    :return: Redirect to quiz detail page.
    """
    question = get_object_or_404(Question, pk=question_id)
    question.delete()
    return HttpResponseRedirect(reverse_lazy('app:QuizDetail', kwargs={'quiz_id': quiz_id}))


class AnonymousUserForm(FormView):
    """
    Get name and email of the anonymous user.
    """
    form_class = AnonymousUserForm
    template_name = 'app/anonymous_user_form.html'

    def get_success_url(self, **kwargs):
        data = kwargs
        quiz_id = data.get('quiz_id')
        name = data.get('name')
        email = data.get('email')

        return reverse_lazy('app:QuizTest', kwargs={'quiz_id': quiz_id}) + '?anonymous=' + str(True) + '&name=' + name + '&email=' + email

    def form_valid(self, form):
        quiz_id = self.request.GET.get('quiz_id')
        data = form.cleaned_data
        return HttpResponseRedirect(self.get_success_url(quiz_id=quiz_id, name=data['name'], email=data['email']))

    def form_invalid(self, form):
        logger.error(form.errors)
        return super().form_invalid(form)


class QuizTest(UserPassesTestMixin, FormView):
    """
    Test Form View.
    """
    template_name = 'app/quiz/quiz_test_form.html'
    form_class = QuizTestForm
    success_url = reverse_lazy('app:QuizList')

    def test_func(self):
        data = self.request.GET
        if self.request.user.is_authenticated or ('anonymous' in data and data['anonymous'] == 'True'):
            return True
        else:
            return False

    def handle_no_permission(self):
        return HttpResponseRedirect(reverse_lazy('app:AnonymousUserForm') + '?quiz_id=' + str(self.kwargs.get('quiz_id')))

    def get_form(self, form_class=None):
        if form_class is None:
            form_class = self.get_form_class()
        return form_class(self.kwargs['quiz_id'], **self.get_form_kwargs())

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['quiz'] = Quiz.objects.get(pk=self.kwargs.get('quiz_id'))
        return context

    def form_valid(self, form):
        query_param = self.request.GET
        quiz_id = self.kwargs.get('quiz_id')

        if 'anonymous' in query_param and query_param['anonymous'] == 'True':
            if query_param.get('email'):
                q = form.save(quiz_id=quiz_id, user=None)
                send_mail(subject='Quiz Test Result',
                          message=f'{q.score}',
                          from_email='test@gmail.com',
                          recipient_list=[query_param['email']])
        else:
            q = form.save(quiz_id=quiz_id, user=self.request.user)
            if self.request.user.email:
                send_mail(subject='Quiz Test Result',
                          message=f'{q.score}',
                          from_email='test@gmail.com',
                          recipient_list=[self.request.user.email])
        messages.add_message(self.request, messages.SUCCESS, 'Thank you for your participation.')
        return HttpResponseRedirect(reverse_lazy('app:QuizResultList'))

    def form_invalid(self, form):
        print(form.errors)
        return super().form_invalid(form)


class QuizResultList(LoginRequiredMixin, ListView):
    """
    List of results of users quiz.
    """
    template_name = 'app/quiz/quiz_result_list.html'
    model = QuizTestResult
    context_object_name = 'results'
    paginate_by = 12

    def get_queryset(self):
        return QuizTestResult.objects.filter(user=self.request.user).order_by('-created')


class UserAuthorQuizTestResultList(LoginRequiredMixin, ListView):
    """
    List of results of quizzes taken.
    """
    template_name = 'app/quiz/user_author_quiz_test_result_list.html'
    model = QuizTestResult
    context_object_name = 'results'
    paginate_by = 20

    def get_queryset(self):
        return QuizTestResult.objects.filter(quiz=self.kwargs.get('quiz_id'), quiz__author=self.request.user).order_by('-created')

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data()
        context['quiz'] = Quiz.objects.get(pk=self.kwargs.get('quiz_id'))
        return context


class QuizResultListExport:
    def __init__(self, quiz_id, *args, **kwargs):
        """
        :param quiz_id: The primary key of the quiz.
        """
        self.quiz = get_object_or_404(Quiz, pk=quiz_id)
        self.results = QuizTestResult.objects.filter(quiz=self.quiz)

    def export_csv(self):
        """
        Export csv for quiz result.

        :return: Response with csv attachment.
        """
        template = get_template('app/quiz/quiz_result_csv_template.html')
        context = {'quiz': self.quiz, 'results': self.results}
        filename = f'{self.quiz.title}-result.csv'

        response = Export.export_csv(template, context, filename)
        return response

    def export_xlsx(self):
        """
        Export csv for quiz result.

        :return: Response with csv attachment.
        """
        template = get_template('app/quiz/quiz_result_xlsx_template.html')
        context = {'quiz': self.quiz, 'results': self.results}
        filename = f'{self.quiz.title}-result.xlsx'

        response = Export.export_xlsx(template, context, filename)
        return response

    def export_pdf(self):
        """
        Export pdf for quiz result.

        :return: Response with csv attachment.
        """
        template = get_template('app/quiz/quiz_result_pdf_template.html')
        context = {'quiz': self.quiz, 'results': self.results}
        filename = f'{self.quiz.title}-result.pdf'

        response = Export.export_pdf(template, context, filename)
        return response

    def export_docx(self):
        """
        Export docx for quiz result.

        :return: Response with csv attachment.
        """
        template = get_template('app/quiz/quiz_result_docx_template.html')
        context = {'quiz': self.quiz, 'results': self.results}
        filename = f'{self.quiz.title}-result.docx'

        response = Export.export_docx(template, context, filename)
        return response


@require_GET
@login_required
def quiz_result_export(request, quiz_id, filetype):
    """
    Export quiz result.

    :param request:
    :param quiz_id: The primary key of the quiz.
    :param filetype: The type of file to be exported.
    :return: Response with attachment.
    """
    q = QuizResultListExport(quiz_id)

    if filetype == 'csv':
        return q.export_csv()

    if filetype == 'xlsx':
        return q.export_xlsx()

    if filetype == 'pdf':
        return q.export_pdf()

    if filetype == 'docx':
        return q.export_docx()


class QuizResultAnswer(LoginRequiredMixin, TemplateView):
    """
    View quiz result answers.
    """
    template_name = 'app/quiz/quiz_result_answer.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        result_id = self.kwargs.get('result_id')
        quiz_test_result = get_object_or_404(QuizTestResult, pk=result_id)
        context['result'] = quiz_test_result
        context['answers'] = QuizTestResultAnswer.objects.filter(quiz_test=quiz_test_result)
        print('Testing')
        print('Abcd')
        return context
