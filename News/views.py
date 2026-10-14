from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.contrib.auth.models import Group
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.views import LoginView
from django.contrib.auth import logout, authenticate, login
from django.db.models import Q

from .models import (Article,
                     Newsletter,
                     CustomUser,
                     Publisher)
from .forms import (RegistrationForm,
                    NewsletterForm,
                    ArticleForm,
                    PublisherForm,
                    PublisherNameForm,
                    ReaderSubscriptionForm)


def home(request):
    '''Display the home page.'''
    return render(request, 'home.html')


def register(request):
    '''Register a new Reader, Journalist, Editor or Publisher.'''

    if request.method == "POST":
        form = RegistrationForm(request.POST)

        if form.is_valid():
            user = form.save()

            role = form.cleaned_data['role']
            group_names = {
                'reader': 'Reader',
                'journalist': 'Journalist',
                'editor': 'Editor',
                'publisher': 'Publisher'
            }

            group, created = Group.objects.get_or_create(
                name=group_names[role])
            user.groups.add(group)

            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            authenticated_user = authenticate(request, username=username,
                                              password=password)
            if authenticated_user is not None:
                login(request, authenticated_user)
                if authenticated_user.role == 'journalist':
                    return redirect('journalist_home')

                elif authenticated_user.role == 'editor':
                    return redirect('editor_home')

                elif authenticated_user.role == 'reader':
                    return redirect('reader_home')

                else:
                    return redirect('publisher_home')

    else:
        form = RegistrationForm()

    return render(request, 'news/register.html', {
        'form': form
    })


def login_redirect(request):
    '''Redirect users to the appropriate page after they log in.'''

    if request.user.groups.filter(name='Reader').exists():
        return redirect('reader_home')

    if request.user.groups.filter(name='Editor').exists():
        return redirect('editor_home')

    if request.user.groups.filter(name='Publisher').exists():
        return redirect('publisher_home')

    return redirect('journalist_home')


class CustomLoginView(LoginView):
    '''Log users in and redirect them based on their group.'''

    def get_success_url(self):
        return login_redirect(self.request).url


@login_required
def logout_confirm(request):
    '''Confirm logout before logging the user out.'''

    if request.method == 'POST':
        logout(request)
        return redirect('home')

    return render(
        request,
        'news/logout_confirm.html'
    )


@login_required
def reader_subscriptions(request):
    '''Allows readers to manage their publisher
    and journalist subscriptions.'''

    if request.user.role != 'reader':
        return redirect('home')

    if request.method == 'POST':
        form = ReaderSubscriptionForm(
            request.POST,
            instance=request.user
        )

        if form.is_valid():
            form.save()
            return redirect('reader_home')

    else:
        form = ReaderSubscriptionForm(instance=request.user)

    return render(
        request,
        'news/reader_subscriptions.html',
        {'form': form}
    )


@login_required
@require_POST
def subscribe_to_journalist(request, article_id):
    '''Allow readers to subscribe to a journalist via an article'''

    if request.user.role != 'reader':
        return redirect('home')

    article = get_object_or_404(Article, id=article_id)
    author = article.author

    if request.method == 'POST':
        request.user.journalist_subscriptions.add(author)
        return redirect('article_detail', article_id=article_id)


@login_required
def unsubscribe_from_journalist(request, article_id):
    '''Allow readers to unsubscribe from a journalist via an article'''

    if request.user.role != 'reader':
        return redirect('home')

    article = get_object_or_404(Article, id=article_id)
    author = article.author

    if request.method == 'POST':
        request.user.journalist_subscriptions.remove(author)
        return redirect('article_detail', article_id=article_id)

    return render(request, 'news/confirm_unsubscribe_from_journalist.html',
                  {'article': article})


@login_required
@require_POST
def subscribe_to_publication(request, article_id):
    '''Allow readers to subscribe to a publication via an article'''

    if request.user.role != 'reader':
        return redirect('home')

    article = get_object_or_404(Article, id=article_id)
    publisher = article.publisher

    if request.method == 'POST':
        if publisher is not None:
            request.user.publisher_subscriptions.add(publisher)
        return redirect('article_detail', article_id=article_id)


@login_required
def unsubscribe_from_publication(request, article_id):
    '''Allow readers to unsubscribe from a publication via an article'''

    if request.user.role != 'reader':
        return redirect('home')

    article = get_object_or_404(Article, id=article_id)
    publisher = article.publisher

    if request.method == 'POST':
        if publisher is not None:
            request.user.publisher_subscriptions.remove(publisher)
        return redirect('article_detail', article_id=article_id)

    return render(request, 'news/confirm_unsubscribe_from_publication.html',
                           {'article': article})


@login_required
def review_articles(request):
    '''Allow editors to review articles.'''
    if not (
        request.user.role == 'editor'
        or request.user.groups.filter(name='Editor').exists()
    ):
        return render(request, 'news/access_denied.html', status=403)

    articles = Article.objects.filter(approved=False,
                                      publisher__isnull=False).order_by(
                                          '-created_at')

    return render(
        request,
        'news/review_articles.html',
        {'articles': articles}
    )


@login_required
def review_article_detail(request, article_id):
    '''Display an article to be reviewd.'''

    article = get_object_or_404(Article, id=article_id)

    return render(
        request,
        'news/review_article_detail.html',
        {
            'article': article,
        }
    )


@login_required
def my_articles(request):
    '''Display articles created by the current user.'''

    articles = Article.objects.filter(
        author=request.user
    )

    return render(
        request,
        'news/my_articles.html',
        {'articles': articles}
    )


@login_required
def my_newsletters(request):
    '''Display newsletters created by the current user.'''

    newsletters = Newsletter.objects.filter(
        author=request.user
    )

    return render(
        request,
        'news/my_newsletters.html',
        {'newsletters': newsletters}
    )


@login_required
def approve_article(request, article_id):
    '''Allow editors to approve an article.'''
    if not (
        request.user.role == 'editor'
        or request.user.groups.filter(name='Editor').exists()
    ):
        return render(request, 'news/access_denied.html', status=403)

    article = get_object_or_404(Article, id=article_id)

    if request.method == 'POST':
        article.approved = True
        article.save()

        return redirect('review_articles')

    return render(
        request,
        'news/approve_article.html',
        {'article': article}
    )


@login_required
def publish_independently(request, article_id):
    '''Allow independent journalist to publish their own articles'''

    if not (
        request.user.role == 'journalist'
        or request.user.groups.filter(name='Journalist').exists()
    ):
        return render(request, 'news/access_denied.html', status=403)

    article = get_object_or_404(Article, id=article_id)

    if request.method == 'POST':
        article.approved = True
        article.save()

        return redirect('my_articles')

    return render(
        request,
        'news/publish_independently.html',
        {'article': article}
    )


@login_required
def article_list(request):
    '''Display articles available to the logged-in user.'''

    if request.user.role == 'journalist':
        articles = Article.objects.filter(
            author=request.user
        )

    elif request.user.role == 'editor':
        articles = Article.objects.all()

    elif request.user.role == 'publisher':
        try:
            publisher = request.user.owned_publisher
            articles = Article.objects.filter(
                publisher=publisher
            )
        except Publisher.DoesNotExist:
            articles = Article.objects.none()

    elif request.user.role == 'reader':
        articles = Article.objects.filter(
            approved=True
        )

    else:
        return render(
            request,
            'news/access_denied.html',
            status=403
        )

    return render(
        request,
        'news/article_list.html',
        {
            'articles': articles
        }
    )


def article_detail(request, article_id):
    '''Display the details of a single article.'''
    article = get_object_or_404(Article, id=article_id)
    return render(request, 'news/article_detail.html', {
                  'article': article})


@login_required
def article_create(request):
    '''Allows journalists to create articles.'''

    if request.user.role != 'journalist':
        return redirect('home')

    if request.method == 'POST':
        form = ArticleForm(request.POST, user=request.user)

        if form.is_valid():
            article = form.save(commit=False)
            article.author = request.user
            article.save()

            return redirect(
                'article_detail',
                article_id=article.id
            )

    else:
        form = ArticleForm(user=request.user)

    return render(
        request,
        'news/article_form.html',
        {
            'form': form,
        }
    )


@login_required
def article_update(request, article_id):
    '''Allow specific users to update articles.'''

    if request.user.role not in ['journalist', 'editor']:
        return render(
            request,
            'news/access_denied.html',
            status=403
        )

    article = get_object_or_404(
        Article,
        id=article_id
    )

    if request.user.role == 'journalist':
        if article.author != request.user:
            return render(
                request,
                'news/access_denied.html',
                status=403
            )

    if request.method == 'POST':
        form = ArticleForm(
            request.POST,
            instance=article,
            user=request.user
        )

        if form.is_valid():
            form.save()

            return redirect(
                'article_detail',
                article_id=article.id
            )

    else:
        form = ArticleForm(instance=article,
                           user=request.user)

    return render(
        request,
        'news/article_update.html',
        {
            'form': form,
            'article': article
        }
    )


@login_required
def article_delete(request, article_id):
    '''Allow specific users to delete articles.'''

    if request.user.role not in ['journalist', 'editor']:
        return render(
            request,
            'news/access_denied.html',
            status=403
        )

    article = get_object_or_404(
        Article,
        id=article_id
    )

    if request.user.role == 'journalist':
        if article.author != request.user:
            return render(
                request,
                'news/access_denied.html',
                status=403
            )

    if request.method == 'POST':
        article.delete()
        if request.user.role == 'journalist':
            return redirect('my_articles')
        else:
            return redirect('article_list')

    return render(
        request,
        'news/article_confirm_delete.html',
        {'article': article}
    )


@login_required
def newsletter_list(request):
    '''Display newsletters available to the logged-in user.'''

    if request.user.role == 'journalist':
        newsletters = Newsletter.objects.filter(
            author=request.user
        )

    elif request.user.role == 'editor':
        newsletters = Newsletter.objects.filter(
            author=request.user
        )

    elif request.user.role == 'publisher':
        try:
            publisher = request.user.owned_publisher

            journalist_ids = publisher.journalists.values_list(
                'id',
                flat=True
            )

            editor_ids = publisher.editors.values_list(
                'id',
                flat=True
            )

            newsletters = Newsletter.objects.filter(
                Q(author_id__in=journalist_ids) |
                Q(author_id__in=editor_ids)
            )

        except Publisher.DoesNotExist:
            newsletters = Newsletter.objects.none()

    elif request.user.role == 'reader':
        newsletters = Newsletter.objects.all()

    else:
        return render(
            request,
            'news/access_denied.html',
            status=403
        )

    newsletters = newsletters.order_by('-created_at')

    return render(
        request,
        'news/newsletter_list.html',
        {'newsletters': newsletters}
    )


def newsletter_detail(request, newsletter_id):
    '''Display the details of a single newsletter.'''
    newsletter = get_object_or_404(
        Newsletter,
        id=newsletter_id
    )

    return render(
        request,
        'news/newsletter_detail.html',
        {'newsletter': newsletter}
    )


@login_required
def newsletter_create(request):
    '''Allow journalists to create newsletters.'''

    articles = Article.objects.filter(approved=True)

    if request.user.role not in ['journalist', 'editor']:
        return render(
            request,
            'news/access_denied.html',
            status=403
        )

    if request.method == 'POST':
        form = NewsletterForm(request.POST)

        if form.is_valid():
            newsletter = form.save(commit=False)
            newsletter.author = request.user
            newsletter.save()
            form.save_m2m()

            return redirect(
                'newsletter_detail',
                newsletter_id=newsletter.id
            )
    else:
        form = NewsletterForm()

    return render(
        request,
        'news/newsletter_form.html',
        {'form': form,
         'articles': articles, }
    )


@login_required
def newsletter_update(request, newsletter_id):
    '''Allow journalists and editors to update newsletters.'''

    if request.user.role not in ['journalist', 'editor']:
        return render(
            request,
            'news/access_denied.html',
            status=403
        )

    newsletter = get_object_or_404(
        Newsletter,
        id=newsletter_id
    )

    if request.user.role == 'journalist':
        if newsletter.author != request.user:
            return render(
                request,
                'news/access_denied.html',
                status=403
            )

    if request.user.role == 'editor':
        if not Publisher.objects.filter(
            editors=request.user,
            journalists=newsletter.author
        ).exists():
            return render(
                request,
                'news/access_denied.html',
                status=403
            )

    if request.method == 'POST':
        form = NewsletterForm(
            request.POST,
            instance=newsletter
        )

        if form.is_valid():
            form.save()

            return redirect(
                'newsletter_detail',
                newsletter_id=newsletter.id
            )
    else:
        form = NewsletterForm(instance=newsletter)

    return render(
        request,
        'news/newsletter_update.html',
        {
            'form': form,
            'newsletter': newsletter
        }
    )


@login_required
def newsletter_delete(request, newsletter_id):
    '''Allow journalists and editors to delete newsletters.'''

    if request.user.role not in ['journalist', 'editor']:
        return render(
            request,
            'news/access_denied.html',
            status=403
        )

    newsletter = get_object_or_404(
        Newsletter,
        id=newsletter_id
    )

    if request.user.role == 'journalist':
        if newsletter.author != request.user:
            return render(
                request,
                'news/access_denied.html',
                status=403
            )

    if request.user.role == 'editor':
        if newsletter.author != request.user:
            return render(
                request,
                'news/access_denied.html',
                status=403
            )

    if request.method == 'POST':
        newsletter.delete()
        if request.user.role not in ['journalist', 'editor']:
            return redirect('newsletter_list')
        else:
            return redirect('my_newsletters')

    return render(
        request,
        'news/newsletter_confirm_delete.html',
        {'newsletter': newsletter}
    )


@login_required
def newsletter_article_detail(request, article_id):
    '''Display an article from a newsletter.'''

    article = get_object_or_404(Article, id=article_id)

    newsletter = article.newsletters.first()

    return render(
        request,
        'news/newsletter_article_detail.html',
        {
            'article': article,
            'newsletter': newsletter
        }
    )


def access_denied(request):
    return render(request, 'news/access_denied.html')


@login_required
def remove_article_from_newsletter(request, newsletter_id, article_id):
    '''Remove an article from a newsletter.'''

    if request.user.role not in ['journalist', 'editor']:
        return render(
            request,
            'news/access_denied.html',
            status=403
        )

    newsletter = get_object_or_404(
        Newsletter,
        id=newsletter_id
    )

    article = get_object_or_404(
        Article,
        id=article_id
    )

    if request.user.role == 'journalist':
        if newsletter.author != request.user:
            return render(
                request,
                'news/access_denied.html',
                status=403
            )

    if request.user.role == 'editor':
        if not Publisher.objects.filter(
            editors=request.user,
            journalists=newsletter.author
        ).exists():
            return render(
                request,
                'news/access_denied.html',
                status=403
            )

    if request.method == 'POST':
        newsletter.articles.remove(article)
        return redirect(
            'newsletter_detail',
            newsletter_id=newsletter.id
        )

    return render(
        request,
        'news/newsletter_article_confirm_remove.html',
        {
            'newsletter': newsletter,
            'article': article
        }
    )


@login_required
def publisher_create(request):
    '''Allows a publisher to create their own publication.'''

    if request.user.role != 'publisher':
        return redirect('home')

    if hasattr(request.user, 'owned_publisher'):
        return redirect('view_publication')

    if request.method == 'POST':
        form = PublisherForm(request.POST)

        if form.is_valid():
            publisher = form.save(commit=False)
            publisher.owner = request.user
            publisher.save()

            form.save_m2m()

            return redirect('publisher_home')

    else:
        form = PublisherForm()

    return render(
        request,
        'news/publisher_create.html',
        {'form': form}
    )


@login_required
def manage_journalists(request):
    '''Allows a publisher to add or remove journalists
    from their publication.
    '''

    if request.user.role != 'publisher':
        return redirect('home')

    try:
        publisher = request.user.owned_publisher
    except Publisher.DoesNotExist:
        return redirect('publisher_create')

    if request.method == 'POST':
        journalist_ids = request.POST.getlist('journalists')

        publisher.journalists.set(
            CustomUser.objects.filter(
                id__in=journalist_ids,
                role='journalist'
            )
        )
        return redirect('view_publication')

    journalists = CustomUser.objects.filter(role='journalist')

    return render(
        request,
        'news/manage_journalists.html',
        {
            'publisher': publisher,
            'journalists': journalists,
        }
    )


@login_required
def manage_editors(request):
    '''Allows a publisher to add or remove editors
    from their publication.
    '''

    if request.user.role != 'publisher':
        return redirect('home')

    try:
        publisher = request.user.owned_publisher
    except Publisher.DoesNotExist:
        return redirect('publisher_create')

    if request.method == 'POST':
        editor_ids = request.POST.getlist('editors')

        publisher.editors.set(
            CustomUser.objects.filter(
                id__in=editor_ids,
                role='editor'
            )
        )
        return redirect('view_publication')

    editors = CustomUser.objects.filter(role='editor')

    return render(
        request,
        'news/manage_editors.html',
        {
            'publisher': publisher,
            'editors': editors,
        }
    )


@login_required
def view_publication(request):
    '''Displays the publication belonging to the logged-in publisher.'''

    if request.user.role != 'publisher':
        return redirect('home')

    try:
        publisher = request.user.owned_publisher
    except Publisher.DoesNotExist:
        return redirect('publisher_create')

    return render(
        request,
        'news/view_publication.html',
        {'publisher': publisher}
    )


@login_required
def publisher_delete(request):
    '''Allows a publisher to delete their own publication.'''

    if request.user.role != 'publisher':
        return redirect('home')

    try:
        publisher = request.user.owned_publisher
    except Publisher.DoesNotExist:
        return redirect('publisher_create')

    if request.method == 'POST':
        publisher.delete()
        return redirect('publisher_home')

    return render(
        request,
        'news/publisher_confirm_delete.html',
        {'publisher': publisher}
    )


@login_required
def publisher_update(request):
    '''Allows a publisher to update the name of their publication.'''

    if request.user.role != 'publisher':
        return redirect('home')

    try:
        publisher = request.user.owned_publisher
    except Publisher.DoesNotExist:
        return redirect('publisher_create')

    if request.method == 'POST':
        form = PublisherNameForm(request.POST, instance=publisher)

        if form.is_valid():
            form.save()

            return redirect('view_publication')

    else:
        form = PublisherNameForm(instance=publisher)

    return render(
        request,
        'news/publisher_update.html',
        {'form': form, 'publisher': publisher}
    )
