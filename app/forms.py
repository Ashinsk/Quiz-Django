from django import forms
from django.core.exceptions import ValidationError

from app.models import Question, QuestionChoice, Quiz, QuizTestResult


class QuizForm(forms.ModelForm):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.fields['author'].widget = forms.HiddenInput()

    class Meta:
        model = Quiz
        fields = "__all__"


class QuestionForm(forms.Form):
    quiz = forms.IntegerField(widget=forms.HiddenInput())
    question = forms.CharField(max_length=1024, required=True)

    choice1 = forms.CharField(max_length=1024, required=True)
    is_correct1 = forms.BooleanField(required=False, label='')

    choice2 = forms.CharField(max_length=1024, required=True)
    is_correct2 = forms.BooleanField(required=False, label='')

    choice3 = forms.CharField(max_length=1024)
    is_correct3 = forms.BooleanField(required=False, label='')

    choice4 = forms.CharField(max_length=1024)
    is_correct4 = forms.BooleanField(required=False, label='')

    def __init__(self, quiz_id, question_id=None, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['quiz'].initial = quiz_id
        if question_id is not None:
            question = Question.objects.get(pk=question_id)
            choices = question.question_choices.all()

            self.fields['question'].initial = question.question

            self.fields['choice1'].initial = choices[0].choice
            self.fields['is_correct1'].initial = choices[0].is_correct

            self.fields['choice2'].initial = choices[1].choice
            self.fields['is_correct2'].initial = choices[1].is_correct

            self.fields['choice3'].initial = choices[2].choice
            self.fields['is_correct3'].initial = choices[2].is_correct

            self.fields['choice4'].initial = choices[3].choice
            self.fields['is_correct4'].initial = choices[3].is_correct

    def clean(self):
        super().clean()
        data = self.cleaned_data
        if not any([data['is_correct1'], data['is_correct2'], data['is_correct3'], data['is_correct4']]):
            raise ValidationError('Please select a correct choice.')
        return self.cleaned_data

    def save(self, quiz_id, question_id=None, **kwargs):
        data = self.cleaned_data
        question, created = Question.objects.update_or_create(pk=question_id, defaults={'quiz_id': data['quiz'], 'question': data['question']})

        if not question_id:
            QuestionChoice.objects.create(question=question, choice=data['choice1'], is_correct=data['is_correct1'])
            QuestionChoice.objects.create(question=question, choice=data['choice2'], is_correct=data['is_correct2'])
            QuestionChoice.objects.create(question=question, choice=data['choice3'], is_correct=data['is_correct3'])
            QuestionChoice.objects.create(question=question, choice=data['choice4'], is_correct=data['is_correct4'])

        if question_id:
            choices = question.question_choices.all()
            QuestionChoice.objects.update_or_create(pk=choices[0].id, defaults={'choice': data['choice1'], 'is_correct': data['is_correct1']})
            QuestionChoice.objects.update_or_create(pk=choices[1].id, defaults={'choice': data['choice2'], 'is_correct': data['is_correct2']})
            QuestionChoice.objects.update_or_create(pk=choices[2].id, defaults={'choice': data['choice3'], 'is_correct': data['is_correct3']})
            QuestionChoice.objects.update_or_create(pk=choices[3].id, defaults={'choice': data['choice4'], 'is_correct': data['is_correct4']})

        return question


class AnonymousUserForm(forms.Form):
    name = forms.CharField(max_length=200, required=True)
    email = forms.EmailField(required=True)


class QuestionChoiceModelChoiceField(forms.ModelMultipleChoiceField):
    def label_from_instance(self, obj):
        return obj.choice


class QuizTestForm(forms.Form):
    def __init__(self, quiz_id, **kwargs):
        super().__init__(**kwargs)

        quiz = Quiz.objects.get(pk=quiz_id)
        questions = quiz.questions.all()
        for question in questions:
            self.fields[str(question.pk)] = QuestionChoiceModelChoiceField(queryset=question.question_choices.all(), widget=forms.CheckboxSelectMultiple())
            self.fields[str(question.pk)].label = question.question

    def check_correct_answers(self, quiz_id, **kwargs):
        data = self.cleaned_data
        quiz = Quiz.objects.get(pk=quiz_id)
        questions = quiz.questions.all()

        score = 0
        answers = dict()
        for question in questions:
            selected_choice = data.get(str(question.pk))
            correct_choices = QuestionChoice.get_correct_choices(quiz.pk)
            a = (set(selected_choice)).difference(set(correct_choices))
            if not a or not correct_choices:
                score += 1
            answers[question] = {'correct': correct_choices, 'selected': selected_choice}
        return answers, score

    def save(self,quiz_id,user,**kwargs):
        answers, score = self.check_correct_answers(quiz_id)
        q = QuizTestResult.objects.create(user=user,quiz_id=quiz_id,score=score)
        return q