from django.db import models
from django.contrib.auth.models import AbstractUser


class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ('reader', 'Reader'),
        ('journalist', 'Journalist'),
        ('editor', 'Editor'),
    )

    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES
    )

    publisher_subscriptions = models.ManyToManyField(
        'Publisher',
        blank=True,
        related_name='subscribed_readers'
    )

    journalist_subscriptions = models.ManyToManyField(
        'self',
        blank=True,
        symmetrical=False,
        related_name='journalist_subscribers'
    )


class Publisher(models.Model):
    '''Model representing publishers of articles and newsletters.

    Fields:
    - name: The name of the publisher in string format.
    - Journalists: Users who wrote articles and
    newsletters publsihed by this publisher.
    - Editors: Editors who edited articles and
    newsletters published by this publisher.
    '''
    name = models.CharField(max_length=100, unique=True)
    journalists = models.ManyToManyField(CustomUser,
                                         related_name='publisher_journalists')
    editors = models.ManyToManyField(CustomUser,
                                     related_name='publisher_editors')

    def __str__(self):
        return self.name


class Article(models.Model):
    '''Model representing articles created by journalists.

    Fields:
    - title: Unique string used to identify the article.
    - Content: Content of the article.
    - author: username of the registered journalist who wrote the article.
    - created_at: The date the article was published.
    - approved: Boolean showing whether the article
    has been approved by an editor or not.
    - publisher: The username of the publisher of the article.
    '''

    title = models.CharField(max_length=30, unique=True)
    content = models.TextField()
    author = models.ForeignKey(CustomUser, on_delete=models.CASCADE,
                               related_name='articles')
    created_at = models.DateTimeField(auto_now_add=True)
    approved = models.BooleanField(default=False)
    publisher = models.ForeignKey(Publisher, on_delete=models.SET_NULL,
                                  null=True, blank=True,
                                  related_name='articles')

    def __str__(self):
        return self.title


class Newsletter(models.Model):
    '''Model representing collections of articles.

    Fields:
    - title: Unique string defining the collection.
    - description: Description of the collection.
    - created_at: The date the newsletter was created.
    - author: The registered author who created the newsletter.
    - articles: The published articles from the Article
    model that are included in the newsletter.
    '''

    title = models.CharField(max_length=30, unique=True)
    description = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(CustomUser, on_delete=models.CASCADE,
                               related_name='newsletters')
    articles = models.ManyToManyField(Article, related_name='newsletters')

    def __str__(self):
        return self.title
