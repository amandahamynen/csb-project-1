from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('note/<int:note_id>/', views.view_note, name='view_note'),
    path('add_note/', views.add_note, name='add_note'),
]