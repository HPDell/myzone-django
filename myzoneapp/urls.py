from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('post/', views.post_list, name='post_list'),
    path('post/new/', views.post_new, name='post_new'),
    path('post/<str:permanent_title>/', views.post_page, name='post_page'),
    path('post/<str:permanent_title>/edit/', views.post_edit, name='post_edit'),
    path('post/<str:permanent_title>/delete/', views.post_delete, name='post_delete'),
    path('post/<str:permanent_title>/translate/<str:lang_code>/', views.post_translate, name='post_translate'),
    path('publication/', views.publication_list, name='pub_list'),
    path('publication/<int:pub_id>/', views.publication_page, name='pub_page')
]
