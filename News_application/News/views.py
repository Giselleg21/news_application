from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.views import LoginView
from django.contrib.auth import logout

from .models import Article, Newsletter
from .forms import RegistrationForm, NewsletterForm, ArticleForm


def home(request):
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
    if not (
        request.user.role == 'editor'
        or request.user.groups.filter(name='Editor').exists()
    ):
        return render(request, 'News/access_denied.html', status=403)

    articles = Article.objects.all().order_by('-created_at')

    return render(
        request,
        'News/review_articles.html',
        {'articles': articles}
    )


@login_required
def review_article_detail(request, article_id):
    '''Display an article from a newsletter.'''

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


def article_list(request):
    '''Display list of all articles.'''
    articles = Article.objects.all()

    return render(request, 'News/article_list.html', {
        'articles': articles
    })


def article_detail(request, article_id):
    '''Display the details of a single article.'''
    article = get_object_or_404(Article, id=article_id)
    return render(request, 'News/article_detail.html', {
                  'article': article})


@login_required
def article_create(request):
    '''Allow Journalists to create new articles.'''

    if request.user.role not in ['journalist']:
        return render(request, 'News/access_denied.html', status=403)

    if request.method == 'POST':
        form = ArticleForm(request.POST)

        if form.is_valid():
            article = form.save(commit=False)
            article.author = request.user
            article.save()
            form.save_m2m()

            return redirect(
                'article_detail',
                article_id=article.id
            )
    else:
        form = ArticleForm()

    return render(
        request,
        'News/article_form.html',
        {'form': form}
    )


@login_required
def article_update(request, article_id):
    '''Allow specific users to update articles.'''

    if request.user.role not in ['journalist', 'editor']:
        return render(request, 'News/access_denied.html', status=403)

    article = get_object_or_404(Article, id=article_id)

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
            status=403)

    article = get_object_or_404(Article, id=article_id)

    if request.method == 'POST':
        article.delete()
        return redirect('article_list')

    return render(
        request,
        'News/article_confirm_delete.html',
        {'article': article}
    )


def newsletter_list(request):
    '''Display a list of all newsletters.'''
    newsletters = Newsletter.objects.all().order_by('-created_at')

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

    if request.user.role not in ['journalist', 'editor']:
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
    """Remove an article from a newsletter."""

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
