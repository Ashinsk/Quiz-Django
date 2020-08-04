from django.contrib import admin
from django.contrib.admin import ModelAdmin

from app.models import *


class QuizAdmin(ModelAdmin):
    list_display = ('title', 'created', 'modified')


class QuestionAdmin(ModelAdmin):
    list_display = ('question', 'created', 'modified')


class QuestionChoiceAdmin(ModelAdmin):
    list_display = ('choice', 'created', 'modified')


admin.site.register(Quiz, QuizAdmin)
admin.site.register(Question, QuestionAdmin)
admin.site.register(QuestionChoice, QuestionChoiceAdmin)
