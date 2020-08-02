from django.urls import path
from app import views

app_name = 'app'
urlpatterns = [
    path('', views.Index.as_view(), name='Index'),

    path('create/', views.QuizCreate.as_view(), name='QuizCreate'),
    path('<int:quiz_id>/update/', views.QuizUpdate.as_view(), name='QuizUpdate'),
    path('<int:quiz_id>/detail/', views.QuizDetail.as_view(), name='QuizDetail'),
    path('list/', views.QuizList.as_view(), name='QuizList'),
    path('<int:quiz_id>/delete/', views.quiz_delete, name='quiz_delete'),

    path('<int:quiz_id>/question/create/', views.QuestionCreate.as_view(), name='QuestionCreate'),
    path('<int:quiz_id>/question/<int:question_id>/update/', views.QuestionUpdate.as_view(), name='QuestionUpdate'),
    path('<int:quiz_id>/question/<int:question_id>/delete/', views.question_delete, name='question_delete'),

    path('<int:quiz_id>/test/', views.QuizTest.as_view(), name='QuizTest'),
]