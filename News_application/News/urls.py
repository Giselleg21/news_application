from django.urls import path
from rest_framework.authtoken.views import obtain_auth_token
from . import views
from django.contrib.auth import views as auth_views
from django.views.generic import TemplateView
from .api_views import (
    article_api_list,
    article_api_detail,
    subscribed_articles_api,
    approved_article_api)


urlpatterns = [
    path('', TemplateView.as_view(
        template_name='News/home.html'), name='home'),
    path('reader/', TemplateView.as_view(
        template_name='News/reader_home.html'), name='reader_home'),
    path('journalist/', TemplateView.as_view(
        template_name='News/journalist_home.html'), name='journalist_home'),
    path('editor/', TemplateView.as_view(
        template_name='News/editor_home.html'), name='editor_home'),
    path('register/', views.register, name='register'),
    path('login/', views.CustomLoginView.as_view(
        template_name='News/login.html'), name='login'),
    path('logout/', views.logout_confirm, name='logout'),
    path('access-denied/', views.access_denied, name='access_denied'),
    path('editor/articles/', views.review_articles, name='review_articles'),
    path('editor/articles/review/<int:article_id>/detail/',
         views.review_article_detail, name='review_article_detail'),
    path('editor/articles/<int:article_id>/approve/',
         views.approve_article, name='approve_article'),
    path('api/articles/', article_api_list, name='article_api_list'),
    path('api/articles/<int:article_id>/', article_api_detail,
         name='article_api_detail'),
    path('api/articles/subscribed/', subscribed_articles_api,
         name='subscribed_articles_api'),
    path('api/approved/', approved_article_api, name='approved_article_api'),
    path('api/token/', obtain_auth_token, name='api_token'),
    path('articles/', views.article_list, name='article_list'),
    path('my_articles/', views.my_articles, name='my_articles'),
    path('article/<int:article_id>/', views.article_detail,
         name='article_detail'),
    path('article/create/', views.article_create, name='article_create'),
    path('articles/<int:article_id>/edit/', views.article_update,
         name='article_update'),
    path('articles/<int:article_id>/delete/', views.article_delete,
         name='article_delete'),
    path('newsletters/', views.newsletter_list, name='newsletter_list'),
    path('my_newsletters/', views.my_newsletters, name='my_newsletters'),
    path('newsletters/<int:newsletter_id>/', views.newsletter_detail,
         name='newsletter_detail'),
    path('newsletter_article/<int:article_id>/detail/',
         views.newsletter_article_detail,
         name='newsletter_article_detail'),
    path('newsletters/create/', views.newsletter_create,
         name='newsletter_create'),
    path('newsletters/<int:newsletter_id>/edit/', views.newsletter_update,
         name='newsletter_update'),
    path('newsletters/<int:newsletter_id>/delete/', views.newsletter_delete,
         name='newsletter_delete'),
    path('newsletters/<int:newsletter_id>/articles/<int:article_id>/remove/',
         views.remove_article_from_newsletter,
         name='remove_article_from_newsletter'),
    path('password_reset/', auth_views.PasswordResetView.as_view(
        template_name='News/password_reset.html'), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(
        template_name='News/password_reset_done.html'),
        name='password_reset_done'),
    path('reset/<uidb64>/<token>/',
         auth_views.PasswordResetConfirmView.as_view(
         template_name='News/password_reset_confirm.html'),
         name='password_reset_confirm'),
    path('reset/done/',
         auth_views.PasswordResetCompleteView.as_view(
         template_name='News/password_reset_complete.html'),
         name='password_reset_complete'),
]
