from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_page, name='home'),
    path('login/', views.login_page, name='login'),
    path('register/', views.register_page, name='register'),
    path('logout/', views.logout_user, name='logout'),
    path('event/<str:pk>/', views.event_page, name='event'),
    path('registration-confirmation/<str:pk>/', views.register_confirmation, name='registration_confirmation'),
    path('search/', views.search_page, name='search'),
    path('user/<str:pk>/', views.user_page, name='profile'),
    path('account/', views.account_page, name='account'),
    path('account/edit/', views.edit_account, name='edit_account'),
    path('account/change-password/', views.change_password, name='change_password'),
    path('project_submission/<str:pk>/', views.project_submission, name='project_submission'),
    path('update_submission/<str:pk>/', views.update_submission, name='update_submission'),
]
