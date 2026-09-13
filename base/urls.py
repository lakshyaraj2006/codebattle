from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='home'),
    path('login/', views.login_page, name='login'),
    path('register/', views.register_page, name='register'),
    path('logout/', views.logout_user, name='logout'),
    path('event/<str:pk>/', views.event_page, name='event'),
    path('registration-confirmation/<str:pk>/', views.register_confirmation, name='registration_confirmation'),
    path('user/<str:pk>/', views.user_page, name='profile'),
    path('account/', views.account_page, name='account'),
    path('project_submission/<str:pk>/', views.project_submission, name='project_submission'),
    path('update_submission/<str:pk>/', views.update_submission, name='update_submission'),
]
