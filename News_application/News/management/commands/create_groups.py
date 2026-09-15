from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType

from News.models import Article, Newsletter


class Command(BaseCommand):
    help = "Creates the Reader, Journalist and Editor groups"

    def handle(self, *args, **kwargs):

        # Get the permissions for Article
        article_content_type = ContentType.objects.get_for_model(Article)

        article_view = Permission.objects.get(
            codename="view_article",
            content_type=article_content_type
        )

        article_add = Permission.objects.get(
            codename="add_article",
            content_type=article_content_type
        )

        article_change = Permission.objects.get(
            codename="change_article",
            content_type=article_content_type
        )

        article_delete = Permission.objects.get(
            codename="delete_article",
            content_type=article_content_type
        )

        # Get the permissions for Newsletter
        newsletter_content_type = ContentType.objects.get_for_model(
            Newsletter)

        newsletter_view = Permission.objects.get(
            codename="view_newsletter",
            content_type=newsletter_content_type
        )

        newsletter_add = Permission.objects.get(
            codename="add_newsletter",
            content_type=newsletter_content_type
        )

        newsletter_change = Permission.objects.get(
            codename="change_newsletter",
            content_type=newsletter_content_type
        )

        newsletter_delete = Permission.objects.get(
            codename="delete_newsletter",
            content_type=newsletter_content_type
        )

        # Create the groups
        reader_group, created = Group.objects.get_or_create(name="Reader")
        journalist_group, created = Group.objects.get_or_create(
            name="Journalist"
        )
        editor_group, created = Group.objects.get_or_create(name="Editor")

        # Reader permissions
        reader_group.permissions.set([
            article_view,
            newsletter_view
        ])

        # Journalist permissions
        journalist_group.permissions.set([
            article_view,
            article_add,
            article_change,
            article_delete,
            newsletter_view,
            newsletter_add,
            newsletter_change,
            newsletter_delete
        ])

        # Editor permissions
        editor_group.permissions.set([
            article_view,
            article_change,
            article_delete,
            newsletter_view,
            newsletter_change,
            newsletter_delete
        ])

        self.stdout.write(
            self.style.SUCCESS(
                "Reader, Journalist and Editor groups created successfully."
            )
        )
