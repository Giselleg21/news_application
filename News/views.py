from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.views import LoginView
from django.contrib.auth import logout

from .models import (Article,
                     Newsletter,
                     CustomUser,
                     Publisher)
from .forms import (RegistrationForm,
                    NewsletterForm,
                    ArticleForm,
                    PublisherForm,
                    PublisherNameForm)


def home(request):
    '''Display the home page.'''
    return render(request, 'home.html')


def register(request):
    '''Register a new Reader, Journalist, or Editor.'''

    if request.method == "POST":
        form = RegistrationForm(request.POST)

        if form.is_valid():
            user = form.save()

            role = form.cleaned_data['role']
            group, created = Group.objects.get_or_create(name=role)
            user.groups.add(group)

            return redirect('login')

    else:
        form = RegistrationForm()

    return render(request, 'News/register.html', {
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
        'News/logout_confirm.html'
    )


@login_required
def review_articles(request):
    '''Allow editors to review articles.'''
    if not (
        request.user.role == 'editor'
        or request.user.groups.filter(name='Editor').exists()
    ):
        return render(request, 'News/access_denied.html', status=403)

    articles = Article.objects.filter(approved=False).order_by('-created_at')

    return render(
        request,
        'News/review_articles.html',
        {'articles': articles}
    )


@login_required
def review_article_detail(request, article_id):
    '''Display an article to be reviewd.'''

    article = get_object_or_404(Article, id=article_id)

    return render(
        request,
        'News/review_article_detail.html',
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
        'News/my_articles.html',
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
        'News/my_newsletters.html',
        {'newsletters': newsletters}
    )


@login_required
def approve_article(request, article_id):
    '''Allow editors to approve an article.'''
    if not (
        request.user.role == 'editor'
        or request.user.groups.filter(name='Editor').exists()
    ):
        return render(request, 'News/access_denied.html', status=403)

    article = get_object_or_404(Article, id=article_id)

    if request.method == 'POST':
        article.approved = True
        article.save()

        return redirect('review_articles')

    return render(
        request,
        'News/approve_article.html',
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
        publisher_ids = Publisher.objects.filter(
            editors=request.user
        ).values_list('id', flat=True)

        articles = Article.objects.filter(
            publisher_id__in=publisher_ids
        )

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
            'News/access_denied.html',
            status=403
        )

    return render(
        request,
        'News/article_list.html',
        {
            'articles': articles
        }
    )


def article_detail(request, article_id):
    '''Display the details of a single article.'''
    article = get_object_or_404(Article, id=article_id)
    return render(request, 'News/article_detail.html', {
                  'article': article})


@login_required
def article_create(request):
    '''Allows journalists to create articles.'''

    if request.user.role != 'journalist':
        return redirect('home')

    publisher = Publisher.objects.filter(
        journalists=request.user
    ).first()

    if request.method == 'POST':
        form = ArticleForm(request.POST)

        if form.is_valid():
            article = form.save(commit=False)
            article.author = request.user
            article.publisher = publisher
            article.save()

            return redirect(
                'article_detail',
                article_id=article.id
            )

    else:
        form = ArticleForm()

    return render(
        request,
        'News/article_form.html',
        {
            'form': form,
            'publisher': publisher,
        }
    )


@login_required
def article_update(request, article_id):
    '''Allow specific users to update articles.'''

    if request.user.role not in ['journalist', 'editor']:
        return render(
            request,
            'News/access_denied.html',
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
                'News/access_denied.html',
                status=403
            )

    if request.user.role == 'editor':
        if not Publisher.objects.filter(
            editors=request.user,
            id=article.publisher_id
        ).exists():
            return render(
                request,
                'News/access_denied.html',
                status=403
            )

    if request.method == 'POST':
        form = ArticleForm(
            request.POST,
            instance=article
        )

        if form.is_valid():
            form.save()

            return redirect(
                'article_detail',
                article_id=article.id
            )

    else:
        form = ArticleForm(instance=article)

    return render(
        request,
        'News/article_update.html',
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
            'News/access_denied.html',
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
                'News/access_denied.html',
                status=403
            )

    if request.user.role == 'editor':
        if not Publisher.objects.filter(
            editors=request.user,
            id=article.publisher_id
        ).exists():
            return render(
                request,
                'News/access_denied.html',
                status=403
            )

    if request.method == 'POST':
        article.delete()
        return redirect('article_list')

    return render(
        request,
        'News/article_confirm_delete.html',
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
        publisher_ids = Publisher.objects.filter(
            editors=request.user
        ).values_list('id', flat=True)

        journalist_ids = Publisher.objects.filter(
            id__in=publisher_ids
        ).values_list('journalists', flat=True)

        newsletters = Newsletter.objects.filter(
            author_id__in=journalist_ids
        )

    elif request.user.role == 'publisher':
        try:
            publisher = request.user.owned_publisher

            journalist_ids = publisher.journalists.values_list(
                'id',
                flat=True
            )

            newsletters = Newsletter.objects.filter(
                author_id__in=journalist_ids
            )

        except Publisher.DoesNotExist:
            newsletters = Newsletter.objects.none()

    elif request.user.role == 'reader':
        newsletters = Newsletter.objects.all()

    else:
        return render(
            request,
            'News/access_denied.html',
            status=403
        )

    newsletters = newsletters.order_by('-created_at')

    return render(
        request,
        'News/newsletter_list.html',
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
        'News/newsletter_detail.html',
        {'newsletter': newsletter}
    )


@login_required
def newsletter_create(request):
    '''Allow journalists and editors to create newsletters.'''

    if request.user.role not in ['journalist']:
        return render(
            request,
            'News/access_denied.html',
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
        'News/newsletter_form.html',
        {'form': form}
    )


@login_required
def newsletter_update(request, newsletter_id):
    '''Allow journalists and editors to update newsletters.'''

    if request.user.role not in ['journalist', 'editor']:
        return render(
            request,
            'News/access_denied.html',
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
                'News/access_denied.html',
                status=403
            )

    if request.user.role == 'editor':
        if not Publisher.objects.filter(
            editors=request.user,
            journalists=newsletter.author
        ).exists():
            return render(
                request,
                'News/access_denied.html',
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
        'News/newsletter_update.html',
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
            'News/access_denied.html',
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
                'News/access_denied.html',
                status=403
            )

    if request.user.role == 'editor':
        if not Publisher.objects.filter(
            editors=request.user,
            journalists=newsletter.author
        ).exists():
            return render(
                request,
                'News/access_denied.html',
                status=403
            )

    if request.method == 'POST':
        newsletter.delete()
        return redirect('newsletter_list')

    return render(
        request,
        'News/newsletter_confirm_delete.html',
        {'newsletter': newsletter}
    )


@login_required
def newsletter_article_detail(request, article_id):
    '''Display an article from a newsletter.'''

    article = get_object_or_404(Article, id=article_id)

    newsletter = article.newsletters.first()

    return render(
        request,
        'News/newsletter_article_detail.html',
        {
            'article': article,
            'newsletter': newsletter
        }
    )


def access_denied(request):
    return render(request, 'News/access_denied.html')


@login_required
def remove_article_from_newsletter(request, newsletter_id, article_id):
    '''Remove an article from a newsletter.'''

    if request.user.role not in ['journalist', 'editor']:
        return render(
            request,
            'News/access_denied.html',
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
                'News/access_denied.html',
                status=403
            )

    if request.user.role == 'editor':
        if not Publisher.objects.filter(
            editors=request.user,
            journalists=newsletter.author
        ).exists():
            return render(
                request,
                'News/access_denied.html',
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
        'News/newsletter_article_confirm_remove.html',
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
        'News/publisher_create.html',
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
        return redirect('create_publisher')

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
        'News/manage_journalists.html',
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
        return redirect('create_publisher')

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
        'News/manage_editors.html',
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
        'News/view_publication.html',
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
        return redirect('create_publisher')

    if request.method == 'POST':
        publisher.delete()
        return redirect('publisher_home')

    return render(
        request,
        'News/publisher_confirm_delete.html',
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
        return redirect('create_publisher')

    if request.method == 'POST':
        form = PublisherNameForm(request.POST, instance=publisher)

        if form.is_valid():
            form.save()

            return redirect('view_publication')

    else:
        form = PublisherNameForm(instance=publisher)

    return render(
        request,
        'News/publisher_update.html',
        {'form': form, 'publisher': publisher}
    )
