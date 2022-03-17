from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('post/', views.post_list, name='post_list'),
    path('post/<int:post_id>/', views.post_page, name='post_page'),
    path('post/new/', views.post_new, name='post_new'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout')
]
