from django.urls import path
from rest_framework.authtoken.views import obtain_auth_token
from .api_views import (
    article_api_list,
    article_api_detail,
    subscribed_articles_api,
    approved_article_api,
)

urlpatterns = [
    path('articles/', article_api_list, name='article_api_list'),
    path(
        'articles/<int:article_id>/',
        article_api_detail,
        name='article_api_detail'
    ),
    path(
        'articles/subscribed/',
        subscribed_articles_api,
        name='subscribed_articles_api'
    ),
    path('approved/', approved_article_api, name='approved_article_api'),
    path('token/', obtain_auth_token, name='api_token'),
]
