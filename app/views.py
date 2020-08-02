from django.core.mail import send_mail
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import TemplateView, CreateView, FormView, DetailView, UpdateView, ListView

from app.forms import *


class Index(TemplateView):
    template_name = 'app/index.html'

    def get_context_data(self, **kwargs):
        context = super(Index, self).get_context_data(**kwargs)
        context['quizzes'] = Quiz.objects.all()
        return context


class QuizCreate(CreateView):
    template_name = 'app/quiz/quiz_create.html'
    model = Quiz
    fields = '__all__'

    def get_success_url(self):
        return reverse_lazy('app:QuestionCreate', kwargs={'quiz_id': self.object.pk})


class QuizUpdate(UpdateView):
    template_name = 'app/quiz/quiz_create.html'
    model = Quiz
    fields = '__all__'
    pk_url_kwarg = 'quiz_id'
    success_url = reverse_lazy('app:Index')


class QuizDetail(DetailView):
    template_name = 'app/quiz/quiz_detail.html'
    model = Quiz
    pk_url_kwarg = 'quiz_id'


class QuizList(ListView):
    template_name = 'app/quiz/quiz_list.html'
    model = Quiz
    context_object_name = 'quizzes'


def quiz_delete(request, quiz_id):
    quiz = get_object_or_404(Quiz, pk=quiz_id)
    quiz.delete()
    return HttpResponseRedirect(reverse_lazy('app:Index'))


class QuestionCreate(FormView):
    template_name = 'app/quiz/question_create.html'
    form_class = QuestionForm

    def get_success_url(self):
        return reverse_lazy('app:QuizDetail', kwargs={'quiz_id': self.kwargs.get('quiz_id')})

    def get_context_data(self, *args, **kwargs):
        context = super(QuestionCreate, self).get_context_data(*args, **kwargs)
        context['title'] = Quiz.objects.get(pk=self.kwargs.get('quiz_id'))
        return context

    def get_form(self, form_class=None):
        if form_class is None:
            form_class = self.get_form_class()
        return form_class(self.kwargs['quiz_id'], **self.get_form_kwargs())

    def form_valid(self, form):
        form.save(self.kwargs['quiz_id'])
        return HttpResponseRedirect(self.get_success_url())

    def form_invalid(self, form):
        print(form.errors)
        return super().form_invalid(form)


class QuestionUpdate(FormView):
    template_name = 'app/quiz/question_create.html'
    form_class = QuestionForm

    def get_success_url(self):
        return reverse_lazy('app:QuizDetail', kwargs={'quiz_id': self.kwargs.get('quiz_id')})

    def get_context_data(self, *args, **kwargs):
        context = super(QuestionUpdate, self).get_context_data(*args, **kwargs)
        context['title'] = Quiz.objects.get(pk=self.kwargs.get('quiz_id'))
        return context

    def get_form(self, form_class=None):
        if form_class is None:
            form_class = self.get_form_class()
        return form_class(self.kwargs['quiz_id'], self.kwargs['question_id'], **self.get_form_kwargs())

    def form_valid(self, form):
        form.save(self.kwargs['quiz_id'], self.kwargs['question_id'])
        return HttpResponseRedirect(self.get_success_url())

    def form_invalid(self, form):
        print(form.errors)
        return HttpResponseRedirect(reverse_lazy('app:QuestionUpdate', kwargs={'quiz_id': self.kwargs.get('quiz_id'),
                                                                               'question_id': self.kwargs.get(
                                                                                   'question_id')}))


def question_delete(request, quiz_id, question_id):
    question = get_object_or_404(Question, pk=question_id)
    question.delete()
    return HttpResponseRedirect(reverse_lazy('app:QuizDetail', kwargs={'quiz_id': quiz_id}))


class QuizTest(FormView):
    template_name = 'app/quiz/quiz_test_form.html'
    form_class = QuizTestForm

    def get_form(self, form_class=None):
        if form_class is None:
            form_class = self.get_form_class()
        return form_class(self.kwargs['quiz_id'], **self.get_form_kwargs())

    def get_context_data(self, **kwargs):
        context = super(QuizTest, self).get_context_data(**kwargs)
        context['quiz'] = Quiz.objects.get(pk=self.kwargs.get('quiz_id'))
        return context

    def form_valid(self, form):
        answers, score = form.check_correct_answers(self.kwargs.get('quiz_id'))
        print(answers,score)
        send_mail(subject='Quiz Test Result',
                  message=f'{answers} {score}',
                  from_email='test@gmail.com',
                  recipient_list=[form.cleaned_data['email']])
        return HttpResponseRedirect(reverse_lazy('app:Index'))
