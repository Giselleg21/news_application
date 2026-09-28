from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from .models import Article
from django.conf import settings
from django.core.mail import send_mail
import requests


User = get_user_model()


@receiver(post_save, sender=User)
def assign_user_group(sender, instance, created, **kwargs):
    '''
    Assigns a newly created user to the Django group that matches
    their selected role.

    Args:
        sender: The model class that triggered the signal.
        instance: The newly created CustomUser instance.
        created: True if the user was newly created.
        **kwargs: Additional arguments provided by the signal.
    '''
    if created:
        if instance.role == 'reader':
            group = Group.objects.get(name='Reader')
            instance.groups.add(group)

        elif instance.role == 'journalist':
            group = Group.objects.get(name='Journalist')
            instance.groups.add(group)

        elif instance.role == 'editor':
            group = Group.objects.get(name='Editor')
            instance.groups.add(group)

        elif instance.role == 'publisher':
            group = Group.objects.get(name='Publisher')
            instance.groups.add(group)


@receiver(pre_save, sender=Article)
def track_article_approval(sender, instance, **kwargs):
    '''
    Records the article's previous approval status before it is saved.

    Args:
        sender: The Article model class that triggered the signal.
        instance: The Article instance being saved.
        **kwargs: Additional arguments provided by the signal.
    '''
    if not instance.pk:
        instance._was_approved = False
    else:
        old_article = sender.objects.get(pk=instance.pk)
        instance._was_approved = old_article.approved


@receiver(post_save, sender=Article)
def article_approved(sender, instance, created, **kwargs):
    '''
    Sends notifications when an existing article changes from
    unapproved to approved.

    Email notifications are sent to users subscribed to the article's
    journalist or publisher. A POST request is also sent to the
    approved articles API endpoint.

    Args:
        sender: The Article model class that triggered the signal.
        instance: The saved Article instance.
        created: True if the article was newly created.
        **kwargs: Additional arguments provided by the signal.
    '''
    if (
        not created
        and instance.approved
        and not getattr(instance, '_was_approved', False)
    ):
        subscribers = set()

        journalist_subscribers = (
            instance.author.journalist_subscribers
            .exclude(email='')
            .values_list('email', flat=True)
        )

        subscribers.update(journalist_subscribers)

        if instance.publisher:
            publisher_subscribers = (
                instance.publisher.subscribed_readers
                .exclude(email='')
                .values_list('email', flat=True)
            )

            subscribers.update(publisher_subscribers)

        if subscribers:
            send_mail(
                subject=f'New approved article: {instance.title}',
                message=(
                    f'{instance.title}\n\n'
                    f'{instance.content}'
                ),
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=list(subscribers),
                fail_silently=False,
            )

        try:
            requests.post(
                'http://127.0.0.1:8000/api/approved/',
                json={
                    'article_id': instance.id,
                    'title': instance.title,
                },
                timeout=5
            )
        except requests.RequestException:
            pass
