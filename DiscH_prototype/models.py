from django.db import models
from django.contrib.auth.models import User


class Question(models.Model):
    question_id = models.IntegerField(primary_key=True)
    description = models.TextField()
    num_response = models.IntegerField(default=0)
    label_in_question = models.CharField(max_length=70)

class Achievement(models.Model):
    achievement_id = models.IntegerField(primary_key=True)
    achievement_type = models.CharField(max_length=100)
    achievement_date = models.DateField()
    account_id = models.ForeignKey(User, on_delete=models.CASCADE, default=-1)  # account_id

class Answer(models.Model):
    answer_id = models.IntegerField(primary_key=True)
    answer_category_num = models.CharField(max_length=40)
    answer_justification = models.TextField(default="")
    answer_upvote = models.IntegerField(default=0)
    account_id = models.ForeignKey(User, on_delete=models.CASCADE, default=-1)  # account_id
    question_id = models.ForeignKey(Question, on_delete=models.CASCADE)  # question_id

class Answer_BOW(models.Model):
    answer_id = models.IntegerField(primary_key=True)
    answer_category_num = models.CharField(max_length=40)
    answer_text_comment = models.TextField(default="")
    answer_justification = models.TextField(default="")
    answer_upvote = models.IntegerField(default=0)
    account_id = models.ForeignKey(User, on_delete=models.CASCADE, default=-1)  # account_id
    question_id = models.ForeignKey(Question, on_delete=models.CASCADE)  # question_id

class Comment(models.Model):
    comment_id = models.IntegerField(primary_key=True)
    comment = models.TextField()
    upvote_num = models.IntegerField(default=0)
    question_id = models.ForeignKey(Question, on_delete=models.CASCADE)  # question_id
    account = models.ForeignKey(User, on_delete=models.CASCADE, default=-1)    # account_id