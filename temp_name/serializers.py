from rest_framework import serializers

from .models import Article, CustomUser, Newsletter, Publisher


class UserSerializer(serializers.ModelSerializer):
    '''Serializer for converting CustomUser instances to and from JSON.

    Fields:
    - id: unique integer used to identify the user.
    - username: unique string used to identify the user.
    - email: the user's email address.
    - role: The user's assigned role in the application.
    '''
    class Meta:
        model = CustomUser
        fields = [
            'id',
            'username',
            'email',
            'role',
        ]


class PublisherSerializer(serializers.ModelSerializer):
    '''Serializer used to convert Publisher instances to and from JSON.

    Fields:
    - id: unique integer used to identify the user.
    - name: the name of the publisher.
    '''
    class Meta:
        model = Publisher
        fields = [
            'id',
            'name',
        ]


class ArticleSerializer(serializers.ModelSerializer):
    '''Serializer used to convert Article instances to and from JSON.

    Fields:
    - id: unique integer used to identify the article.
    - title: string representing the title of the article.
    - content: the actual content of the article.
    - author: the registered journalist who wrote the article.
    - created_at: the date the article was created.
    - approved: Boolean showing whether the article has been approved
    by an editor or not.
    - publisher: the username of the publisher of the article.
    '''
    class Meta:
        model = Article
        fields = [
            'id',
            'title',
            'content',
            'author',
            'created_at',
            'approved',
            'publisher',
        ]
        read_only_fields = [
            'author',
            'created_at',
            'approved',
        ]


class NewsletterSerializer(serializers.ModelSerializer):
    '''Serializer used to convert Newsletter instances to and from JSON.

    Fields:
    - id: unique integer used to identify the newsletter.
    - title: Unique string defining the collection.
    - description: Description of the collection.
    - created_at: The date the newsletter was created.
    - author: The registered author who created the newsletter.
    - articles: The published articles from the Article
    model that are included in the newsletter.
    '''
    class Meta:
        model = Newsletter
        fields = [
            'id',
            'title',
            'description',
            'created_at',
            'author',
            'articles',
        ]
