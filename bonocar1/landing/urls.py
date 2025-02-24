from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path('',views.index, name= 'index'),
    path('login/',auth_views.LoginView.as_view(template_name='landing/login.html'),name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('signup/',views.signup,name='signup'),
    path('blog/', views.blog_list, name='blog_list'),
    path('blog/new/', views.blog_create, name='blog_create'),
    path('blog/<int:pk>/edit/', views.blog_update, name='blog_update'),
    path('blog/<int:pk>/delete/', views.blog_delete, name='blog_delete'),
    path('blog/<int:pk>/', views.blog_detail, name='blog_detail'),
    path('blog/<int:pk>/like/', views.like_post, name='like_post'),
]