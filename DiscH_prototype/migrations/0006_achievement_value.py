# Generated by Django 4.0.4 on 2022-10-02 14:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('DiscH_prototype', '0005_achievement_question_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='achievement',
            name='value',
            field=models.CharField(default='unknown', max_length=200),
        ),
    ]