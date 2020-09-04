from django.contrib import admin
from django.contrib.admin import ModelAdmin
from simple_history.admin import SimpleHistoryAdmin

from app.models import *


class QuizAdmin(SimpleHistoryAdmin):
    list_display = ('title', 'author', 'is_published', 'get_total_test_counts', 'created', 'modified')
    search_fields = ('title',)
    list_filter = ('is_published','author',)
    actions = ['publish_quiz','unpublish_quiz']
    ordering = ('-modified',)

    def changelist_view(self, request, extra_context=None):
        extra_context = {'title': 'Quiz'}
        return super().changelist_view(request, extra_context=extra_context)

    def get_total_test_counts(self, obj):
        return obj.quiz_test_results.count()
    get_total_test_counts.short_description = 'Tests'

    def publish_quiz(self, request, queryset):
        for q in queryset:
            q.publish_quiz()

        self.message_user(request,f'{queryset.count()} quizzes published.')

    publish_quiz.short_description = "Publish selected quiz."

    def unpublish_quiz(self, request, queryset):
        for q in queryset:
            q.unpublish_quiz()

        self.message_user(request,f'{queryset.count()} quizzes unpublished.')
    unpublish_quiz.short_description = "Unpublish selected quiz."


class QuestionAdmin(SimpleHistoryAdmin):
    list_display = ('question', 'created', 'modified')


class QuestionChoiceAdmin(ModelAdmin):
    list_display = ('choice', 'created', 'modified')


class QuizTestResultAdmin(ModelAdmin):
    list_display = ('user', 'quiz', 'score', 'created')


admin.site.register(Quiz, QuizAdmin)
admin.site.register(Question, QuestionAdmin)
admin.site.register(QuestionChoice, QuestionChoiceAdmin)
admin.site.register(QuizTestResult, QuizTestResultAdmin)
admin.site.register(QuizTestResultAnswer)
