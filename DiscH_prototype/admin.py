from django.contrib import admin
from .models import Question, Achievement, Answer, Comment
# Register your models here.

admin.site.register(Question)
admin.site.register(Achievement)
admin.site.register(Answer)
admin.site.register(Comment)