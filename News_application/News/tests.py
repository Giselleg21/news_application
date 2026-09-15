from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group

from rest_framework.test import APITestCase
from rest_framework.authtoken.models import Token

from unittest.mock import patch

from .models import Article, Newsletter

# Create your tests here.
User = get_user_model()


class UserRoleTest(TestCase):

    def setUp(self):
        Group.objects.get_or_create(name='Reader')
        Group.objects.get_or_create(name='Journalist')
        Group.objects.get_or_create(name='Editor')

    def test_reader_is_added_to_reader_group(self):
        reader = User.objects.create_user(
            username='reader_test',
            password='TestPassword123',
            role='reader'
        )

        self.assertTrue(
            reader.groups.filter(name='Reader').exists()
        )

    def test_journalist_is_added_to_journalist_group(self):
        journalist = User.objects.create_user(
            username='journalist_test',
            password='TestPassword123',
            role='journalist'
        )

        self.assertTrue(
            journalist.groups.filter(name='Journalist').exists()
        )

    def test_editor_is_added_to_editor_group(self):
        editor = User.objects.create_user(
            username='editor_test',
            password='TestPassword123',
            role='editor'
        )

        self.assertTrue(
            editor.groups.filter(name='Editor').exists()
        )


class ReaderSubscriptionTest(TestCase):

    def setUp(self):
        Group.objects.get_or_create(name='Reader')
        Group.objects.get_or_create(name='Journalist')
        Group.objects.get_or_create(name='Editor')

        self.reader = User.objects.create_user(
            username='reader_test',
            password='TestPassword123',
            role='reader'
        )

        self.journalist = User.objects.create_user(
            username='journalist_test',
            password='TestPassword123',
            role='journalist'
        )

        self.other_journalist = User.objects.create_user(
            username='other_journalist',
            password='TestPassword123',
            role='journalist'
        )

        self.reader.journalist_subscriptions.add(
            self.journalist
        )

        self.subscribed_article = Article.objects.create(
            title='Subscribed Article',
            content='Article from subscribed journalist.',
            author=self.journalist,
            approved=True
        )

        self.unsubscribed_article = Article.objects.create(
            title='Unsubscribed Article',
            content='Article from another journalist.',
            author=self.other_journalist,
            approved=True
        )

    def test_reader_only_gets_subscribed_articles(self):
        articles = Article.objects.filter(
            approved=True,
            author__in=self.reader.journalist_subscriptions.all()
        )

        self.assertIn(
            self.subscribed_article,
            articles
        )

        self.assertNotIn(
            self.unsubscribed_article,
            articles
        )


class APIAuthenticationTest(APITestCase):

    def setUp(self):
        Group.objects.get_or_create(name='Reader')
        Group.objects.get_or_create(name='Journalist')
        Group.objects.get_or_create(name='Editor')

        self.reader = User.objects.create_user(
            username='api_reader',
            password='TestPassword123',
            role='reader'
        )

    def test_unauthenticated_user_cannot_access_articles(self):
        response = self.client.get('/api/articles/')

        self.assertEqual(
            response.status_code,
            401
        )

    def test_authenticated_reader_can_access_articles(self):
        token = Token.objects.create(user=self.reader)

        self.client.credentials(
            HTTP_AUTHORIZATION=f'Token {token.key}'
        )

        response = self.client.get('/api/articles/')

        self.assertEqual(
            response.status_code,
            200
        )


class APIArticleCreateTest(APITestCase):

    def setUp(self):
        Group.objects.get_or_create(name='Reader')
        Group.objects.get_or_create(name='Journalist')
        Group.objects.get_or_create(name='Editor')

        self.reader = User.objects.create_user(
            username='api_reader',
            password='TestPassword123',
            role='reader'
        )

        self.journalist = User.objects.create_user(
            username='api_journalist',
            password='TestPassword123',
            role='journalist'
        )

    def test_journalist_can_create_article(self):
        token = Token.objects.create(
            user=self.journalist
        )

        self.client.credentials(
            HTTP_AUTHORIZATION=f'Token {token.key}'
        )

        response = self.client.post(
            '/api/articles/',
            {
                'title': 'API Created Article',
                'content': 'Created by a journalist through the API.'
            },
            format='json'
        )

        self.assertEqual(
            response.status_code,
            201
        )

        self.assertTrue(
            Article.objects.filter(
                title='API Created Article'
            ).exists()
        )

    def test_reader_cannot_create_article(self):
        token = Token.objects.create(
            user=self.reader
        )

        self.client.credentials(
            HTTP_AUTHORIZATION=f'Token {token.key}'
        )

        response = self.client.post(
            '/api/articles/',
            {
                'title': 'Reader Article',
                'content': 'A reader should not be able to create this.'
            },
            format='json'
        )

        self.assertEqual(
            response.status_code,
            403
        )


class EditorApprovalTest(APITestCase):

    def setUp(self):
        Group.objects.get_or_create(name='Reader')
        Group.objects.get_or_create(name='Journalist')
        Group.objects.get_or_create(name='Editor')

        self.journalist = User.objects.create_user(
            username='approval_journalist',
            password='TestPassword123',
            role='journalist'
        )

        self.editor = User.objects.create_user(
            username='approval_editor',
            password='TestPassword123',
            role='editor'
        )

        self.reader = User.objects.create_user(
            username='approval_reader',
            password='TestPassword123',
            role='reader'
        )

        self.article = Article.objects.create(
            title='Article Awaiting Approval',
            content='This article needs editor approval.',
            author=self.journalist,
            approved=False
        )

    def test_editor_can_approve_article(self):
        self.client.login(
            username='approval_editor',
            password='TestPassword123'
        )

        response = self.client.post(
            reverse(
                'approve_article',
                kwargs={'article_id': self.article.id}
            )
        )

        self.assertEqual(
            response.status_code,
            302
        )

        self.article.refresh_from_db()

        self.assertTrue(
            self.article.approved
        )

    def test_reader_cannot_approve_article(self):
        self.client.login(
            username='approval_reader',
            password='TestPassword123'
        )

        self.assertFalse(
            self.reader.role == 'editor'
            or self.reader.groups.filter(name='Editor').exists()
        )

        self.article.refresh_from_db()

        self.assertFalse(
            self.article.approved
        )


class APIArticleModifyTest(APITestCase):

    def setUp(self):
        Group.objects.get_or_create(name='Reader')
        Group.objects.get_or_create(name='Journalist')
        Group.objects.get_or_create(name='Editor')

        self.journalist = User.objects.create_user(
            username='modify_journalist',
            password='TestPassword123',
            role='journalist'
        )

        self.editor = User.objects.create_user(
            username='modify_editor',
            password='TestPassword123',
            role='editor'
        )

        self.reader = User.objects.create_user(
            username='modify_reader',
            password='TestPassword123',
            role='reader'
        )

        self.article = Article.objects.create(
            title='Article To Modify',
            content='Original article content.',
            author=self.journalist,
            approved=True
        )

    def test_editor_can_update_article(self):
        token = Token.objects.create(
            user=self.editor
        )

        self.client.credentials(
            HTTP_AUTHORIZATION=f'Token {token.key}'
        )

        response = self.client.put(
            f'/api/articles/{self.article.id}/',
            {
                'title': 'Updated By Editor',
                'content': 'Updated article content.'
            },
            format='json'
        )

        self.assertEqual(
            response.status_code,
            200
        )

    def test_journalist_can_update_article(self):
        token = Token.objects.create(
            user=self.journalist
        )

        self.client.credentials(
            HTTP_AUTHORIZATION=f'Token {token.key}'
        )

        response = self.client.put(
            f'/api/articles/{self.article.id}/',
            {
                'title': 'Updated By Journalist',
                'content': 'Updated article content.'
            },
            format='json'
        )

        self.assertEqual(
            response.status_code,
            200
        )

    def test_reader_cannot_update_article(self):
        token = Token.objects.create(
            user=self.reader
        )

        self.client.credentials(
            HTTP_AUTHORIZATION=f'Token {token.key}'
        )

        response = self.client.put(
            f'/api/articles/{self.article.id}/',
            {
                'title': 'Reader Attempt',
                'content': 'This should not be allowed.'
            },
            format='json'
        )

        self.assertEqual(
            response.status_code,
            403
        )

    def test_editor_can_delete_article(self):
        token = Token.objects.create(
            user=self.editor
        )

        self.client.credentials(
            HTTP_AUTHORIZATION=f'Token {token.key}'
        )

        response = self.client.delete(
            f'/api/articles/{self.article.id}/'
        )

        self.assertEqual(
            response.status_code,
            204
        )

        self.assertFalse(
            Article.objects.filter(
                id=self.article.id
            ).exists()
        )


class SubscribedArticlesAPITest(APITestCase):

    def setUp(self):
        Group.objects.get_or_create(name='Reader')
        Group.objects.get_or_create(name='Journalist')
        Group.objects.get_or_create(name='Editor')

        self.reader = User.objects.create_user(
            username='subscription_reader',
            password='TestPassword123',
            role='reader'
        )

        self.journalist = User.objects.create_user(
            username='subscribed_journalist',
            password='TestPassword123',
            role='journalist'
        )

        self.other_journalist = User.objects.create_user(
            username='other_journalist',
            password='TestPassword123',
            role='journalist'
        )

        self.reader.journalist_subscriptions.add(
            self.journalist
        )

        self.subscribed_article = Article.objects.create(
            title='Subscribed API Article',
            content='This article should be visible.',
            author=self.journalist,
            approved=True
        )

        self.unsubscribed_article = Article.objects.create(
            title='Unsubscribed API Article',
            content='This article should not be visible.',
            author=self.other_journalist,
            approved=True
        )

    def test_reader_only_receives_subscribed_articles(self):
        token = Token.objects.create(
            user=self.reader
        )

        self.client.credentials(
            HTTP_AUTHORIZATION=f'Token {token.key}'
        )

        response = self.client.get(
            '/api/articles/subscribed/'
        )

        self.assertEqual(
            response.status_code,
            200
        )

        returned_titles = [
            article['title']
            for article in response.data
        ]

        self.assertIn(
            'Subscribed API Article',
            returned_titles
        )

        self.assertNotIn(
            'Unsubscribed API Article',
            returned_titles
        )


class NewsletterTest(TestCase):

    def setUp(self):
        Group.objects.get_or_create(name='Reader')
        Group.objects.get_or_create(name='Journalist')
        Group.objects.get_or_create(name='Editor')

        self.reader = User.objects.create_user(
            username='newsletter_reader',
            password='TestPassword123',
            role='reader'
        )

        self.journalist = User.objects.create_user(
            username='newsletter_journalist',
            password='TestPassword123',
            role='journalist'
        )

        self.editor = User.objects.create_user(
            username='newsletter_editor',
            password='TestPassword123',
            role='editor'
        )

        self.article = Article.objects.create(
            title='Newsletter Article',
            content='Article included in the newsletter.',
            author=self.journalist,
            approved=True
        )

    def test_journalist_can_create_newsletter(self):
        newsletter = Newsletter.objects.create(
            title='Journalist Newsletter',
            description='A newsletter created by a journalist.',
            author=self.journalist
        )

        newsletter.articles.add(self.article)

        self.assertEqual(
            newsletter.author,
            self.journalist
        )

        self.assertIn(
            self.article,
            newsletter.articles.all()
        )

    def test_editor_can_create_newsletter(self):
        newsletter = Newsletter.objects.create(
            title='Editor Newsletter',
            description='A newsletter created by an editor.',
            author=self.editor
        )

        newsletter.articles.add(self.article)

        self.assertEqual(
            newsletter.author,
            self.editor
        )

        self.assertIn(
            self.article,
            newsletter.articles.all()
        )

    def test_reader_cannot_create_newsletter(self):
        self.assertNotIn(
            self.reader.role,
            ['journalist', 'editor']
        )


class ArticleApprovalSignalTest(TestCase):

    def setUp(self):
        Group.objects.get_or_create(name='Reader')
        Group.objects.get_or_create(name='Journalist')
        Group.objects.get_or_create(name='Editor')

        self.journalist = User.objects.create_user(
            username='signal_journalist',
            password='TestPassword123',
            role='journalist'
        )

        self.reader = User.objects.create_user(
            username='signal_reader',
            password='TestPassword123',
            role='reader',
            email='reader@example.com'
        )

        self.reader.journalist_subscriptions.add(
            self.journalist
        )

        self.article = Article.objects.create(
            title='Signal Test Article',
            content='Testing the approval signal.',
            author=self.journalist,
            approved=False
        )

    @patch('News.signals.send_mail')
    @patch('News.signals.requests.post')
    def test_approval_sends_notification(
        self,
        mock_post,
        mock_send_mail
    ):
        self.article.approved = True
        self.article.save()

        mock_send_mail.assert_called_once()

        mock_post.assert_called_once()

        self.assertTrue(
            self.article.approved
        )
