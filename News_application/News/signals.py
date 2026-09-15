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


@receiver(pre_save, sender=Article)
def track_article_approval(sender, instance, **kwargs):
    if not instance.pk:
        instance._was_approved = False
    else:
        old_article = sender.objects.get(pk=instance.pk)
        instance._was_approved = old_article.approved


@receiver(post_save, sender=Article)
def article_approved(sender, instance, created, **kwargs):
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
