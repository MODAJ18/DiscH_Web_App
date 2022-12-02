from django.urls import path, include
from . import views
# from django.conf.urls import url

from rest_framework.routers import DefaultRouter
from .views import QuestionViewSet

router = DefaultRouter()
router.register(r'questions', QuestionViewSet)


urlpatterns = [
    path('', views.starting, name='starting'),
    path('Login/', views.Login, name='Login'),
    path('reg/', views.reg, name='reg'),
    path('questions/', views.questions, name='questions'),
    path('questions/<int:question_id>/', views.question_page, name='question_page'),
    path('questions/search/<str:search_term>/', views.search_page, name='search_page'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('about/', views.about, name='about'),
    path('reset/', views.email, name='email')
    
    # path(r'^api/public/', views.public),
    # path(r'^api/private/', views.private)
]


# In the code above, the router class generates the following URL patterns:
#
# /recipes/ - CREATE and READ operations can be performed on this route.
# /recipes/{id} - READ, UPDATE, and DELETE operations can be performed on this route.