# Generated by Django 2.2.14 on 2020-08-02 23:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('learning_sequences', '0003_create_course_context_for_course_specific_models'),
    ]

    operations = [
        migrations.AddField(
            model_name='coursecontext',
            name='self_paced',
            field=models.BooleanField(default=False),
        ),
    ]
