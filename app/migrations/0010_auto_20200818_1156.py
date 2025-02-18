# Generated by Django 3.1 on 2020-08-18 11:56

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0009_auto_20200809_1235'),
    ]

    operations = [
        migrations.AddField(
            model_name='quiz',
            name='published_date',
            field=models.DateTimeField(null=True),
        ),
        migrations.AlterField(
            model_name='quiztestresultanswer',
            name='choice',
            field=models.ForeignKey(help_text='Choice refers to the selected choice.', on_delete=django.db.models.deletion.CASCADE, related_name='results_answers', related_query_name='result_answer', to='app.questionchoice'),
        ),
    ]
