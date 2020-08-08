from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin
from django.core.mail import send_mail
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import TemplateView, CreateView, FormView, DetailView, UpdateView, ListView
from django.contrib import messages

from app.forms import *


class Index(TemplateView):
    """
    Index or Home view.
    """
    template_name = 'app/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['quizzes'] = Quiz.objects.all()
        return context


class QuizCreate(LoginRequiredMixin, CreateView):
    """
    Create Quiz.
    """
    template_name = 'app/quiz/quiz_create.html'
    form_class = QuizForm

    def get_success_url(self,**kwargs):
        return reverse_lazy('app:QuestionCreate', kwargs={'quiz_id': kwargs.get('quiz_id')})

    def get_initial(self):
        return {'author': self.request.user}

    def form_valid(self, form):
        form = form.save()
        messages.add_message(self.request, messages.SUCCESS, 'Quiz Created')
        return HttpResponseRedirect(self.get_success_url(quiz_id=form.pk))
    
    def form_invalid(self, form):
        print(form.errors)
        messages.add_message(self.request, messages.ERROR, form.errors)
        return super().form_invalid(form)


class QuizUpdate(UpdateView):
    """
    Update Quiz.
    """
    template_name = 'app/quiz/quiz_create.html'
    model = Quiz
    fields = '__all__'
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
    template_name = 'app/quiz/quiz_list.html'
    model = Quiz
    context_object_name = 'quizzes'

    def get_queryset(self):
        return Quiz.objects.filter(question__isnull=False)


def quiz_delete(request, quiz_id):
    """
    Delete the quiz.

    :param request:
    :param quiz_id: PK value of the quiz.
    :return: Redirect to index view.
    """
    quiz = get_object_or_404(Quiz, pk=quiz_id)
    quiz.delete()
    return HttpResponseRedirect(reverse_lazy('app:Index'))


class QuestionCreate(FormView):
    """
    Create question for the quiz.
    """
    template_name = 'app/quiz/question_create.html'
    form_class = QuestionForm

    def get_success_url(self):
        return reverse_lazy('app:QuizDetail', kwargs={'quiz_id': self.kwargs.get('quiz_id')})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = Quiz.objects.get(pk=self.kwargs.get('quiz_id'))
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
        print(form.errors)
        messages.add_message(self.request, messages.ERROR, 'Question Add Error')
        return super().form_invalid(form)


class QuestionUpdate(FormView):
    """
    Update question for the quiz.
    """
    template_name = 'app/quiz/question_create.html'
    form_class = QuestionForm

    def get_success_url(self):
        return reverse_lazy('app:QuizDetail', kwargs={'quiz_id': self.kwargs.get('quiz_id')})

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['title'] = Quiz.objects.get(pk=self.kwargs.get('quiz_id'))
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
        print(form.errors)
        messages.add_message(self.request, messages.ERROR, 'Question Update Error')
        return HttpResponseRedirect(reverse_lazy('app:QuestionUpdate', kwargs={'quiz_id': self.kwargs.get('quiz_id'),
                                                                               'question_id': self.kwargs.get(
                                                                                   'question_id')}))


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
        return HttpResponseRedirect(self.get_success_url(quiz_id=quiz_id,name=data['name'],email=data['email']))


class QuizTest(UserPassesTestMixin, FormView):
    """
    Test Form View.
    """
    template_name = 'app/quiz/quiz_test_form.html'
    form_class = QuizTestForm
    success_url = reverse_lazy('app:Index')

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
                answers, score = form.check_correct_answers()
                send_mail(subject='Quiz Test Result',
                          message=f'{answers} {score}',
                          from_email='test@gmail.com',
                          recipient_list=[query_param['email']])
        else:
            q = form.save(quiz_id=quiz_id,user=self.request.user)
            if self.request.user.email:
                send_mail(subject='Quiz Test Result',
                          message=f'{q.score}',
                          from_email='test@gmail.com',
                          recipient_list=[self.request.user.email])

        return super().form_valid(form)


class QuizResultList(LoginRequiredMixin,ListView):
    template_name = 'app/quiz/quiz_result_list.html'
    model = QuizTestResult
    context_object_name = 'results'
    paginate_by = 12

    def get_queryset(self):
        return QuizTestResult.objects.filter(user=self.request.user)


class QuizTestResultList(LoginRequiredMixin,ListView):
    template_name = 'app/quiz/quiz_test_result_list.html'
    model = QuizTestResult
    context_object_name = 'results'
    paginate_by = 20

    def get_queryset(self):
        return QuizTestResult.objects.filter(quiz=self.kwargs.get('quiz_id'),quiz__author=self.request.user).order_by('-created')

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data()
        context['quiz'] = Quiz.objects.get(pk=self.kwargs.get('quiz_id'))
        return context