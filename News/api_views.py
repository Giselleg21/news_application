from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404

from .models import Article
from .serializers import ArticleSerializer


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def article_api_list(request):
    """List approved articles or create an article."""

    if request.method == 'GET':
        articles = Article.objects.filter(approved=True)
        serializer = ArticleSerializer(articles, many=True)

        return Response(serializer.data)

    if request.user.role != 'journalist':
        return Response(
            {'error': 'Only journalists can create articles.'},
            status=status.HTTP_403_FORBIDDEN
        )

    serializer = ArticleSerializer(data=request.data)

    if serializer.is_valid():
        serializer.save(
            author=request.user,
            approved=False
        )

        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED
        )

    return Response(
        serializer.errors,
        status=status.HTTP_400_BAD_REQUEST
    )


@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def article_api_detail(request, article_id):
    """View, update or delete an article."""

    article = get_object_or_404(
        Article,
        id=article_id
    )

    if request.method == 'GET':
        if not article.approved:
            return Response(
                {'error': 'Article not found.'},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = ArticleSerializer(article)
        return Response(serializer.data)

    if request.user.role not in ['journalist', 'editor']:
        return Response(
            {'error': 'You do not have permission to modify articles.'},
            status=status.HTTP_403_FORBIDDEN
        )

    if request.method == 'PUT':
        serializer = ArticleSerializer(
            article,
            data=request.data
        )

        if serializer.is_valid():
            serializer.save()

            return Response(serializer.data)

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

    article.delete()

    return Response(
        status=status.HTTP_204_NO_CONTENT
    )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def subscribed_articles_api(request):
    """Return approved articles from the reader's subscriptions."""

    if request.user.role != 'reader':
        return Response(
            {'error': 'Only readers can access subscribed articles.'},
            status=status.HTTP_403_FORBIDDEN
        )

    journalist_ids = request.user.journalist_subscriptions.values_list(
        'id',
        flat=True
    )

    publisher_ids = request.user.publisher_subscriptions.values_list(
        'id',
        flat=True
    )

    articles = Article.objects.filter(
        approved=True
    ).filter(
        author_id__in=journalist_ids
    ) | Article.objects.filter(
        approved=True,
        publisher_id__in=publisher_ids
    )

    articles = articles.distinct()

    serializer = ArticleSerializer(articles, many=True)

    return Response(serializer.data)


@api_view(['POST'])
def approved_article_api(request):
    """Receive an article after it has been approved."""

    return Response(
        {
            'message': 'Approved article received.',
            'article_id': request.data.get('article_id')
        },
        status=status.HTTP_200_OK
    )
