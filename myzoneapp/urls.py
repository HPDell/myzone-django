from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('post/', views.post_list, name='post_list'),
    path('post/<int:post_id>/', views.post_page, name='post_page'),
    path('post/<int:post_id>/edit/', views.post_edit, name='post_edit'),
    path('post/<int:post_id>/delete/', views.post_delete, name='post_delete'),
    path('post/new/', views.post_new, name='post_new'),
    path('publication/', views.publication_list, name='pub_list'),
    path('publication/<int:pub_id>/', views.publication_page, name='pub_list')
]
