# Generated by Django 4.0.5 on 2022-06-05 18:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('DiscH_prototype', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='answer_bow',
            name='answer_text_comment',
            field=models.TextField(default=''),
        ),
    ]
