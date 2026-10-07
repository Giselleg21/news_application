# Django News Application

## Overview

This project was developed as a Django capstone application. It demonstrates user authentication, role-based access control, article and newsletter management, subscriptions, editor approval, email notifications, and a RESTful API.

The application uses **MariaDB/MySQL** as its database.

---

## Features

### User Authentication

Users can:

* Register for an account.

* Log in and log out.

* Select a role during registration.

* Be automatically assigned to the appropriate Django group.

* Access functionality based on their assigned role.

The application uses a custom `CustomUser` model based on Django's `AbstractUser`.

### Role-Based Permissions

The application uses Django groups and permissions for the different user roles.

#### Reader

Readers can:

* View approved articles.

* View newsletters.

* Subscribe to publishers.

* Subscribe to journalists.

* View articles from their subscriptions.

Readers cannot create, edit, delete, or approve articles.

#### Journalist

Journalists can:

* Create articles.

* View articles.

* Update articles.

* Delete articles.

* Create newsletters.

* Update newsletters.

* Delete newsletters.

* Add articles to newsletters.

* Remove articles from newsletters.

New articles created by journalists require editor approval before being publicly available.

#### Editor

Editors can:

* View articles awaiting approval.

* Approve articles.

* Update articles.

* Delete articles.

* View, update, and delete newsletters associated with their publication.

Editors are responsible for reviewing articles before they become approved.

#### Publisher

Publishers can:

* Create a publication.

* Update their publication.

* Delete their publication.

* Manage the journalists assigned to their publication.

* Manage the editors assigned to their publication.

* View the articles associated with their publication.

* View newsletters created by journalists assigned to their publication.

Publishers are responsible for managing the journalists and editors associated with their publication.

---

## Articles

Articles contain:

* Title

* Content

* Author

* Creation date

* Approval status

* Publisher

Articles are initially created with `approved=False`.

An editor can review an article and approve it. Once approved, the article becomes available to readers.

---

## Article Approval

The application includes an editor-only article review system.

Editors can access the article review page and select an article to review. They can then approve the article.

When an article is approved:

1. The article's approval status is changed to `True`.

2. Subscribers are identified.

3. Email notifications are sent to relevant subscribers.

4. A POST request is made to the application's `/api/approved/` endpoint.

The email system uses Django's console email backend during development.

---

## Newsletters

Newsletters contain:

* Title

* Description

* Creation date

* Author

* Associated articles

Journalists can create, update, and delete newsletters.

Editors can view, update, and delete newsletters associated with their publication, but cannot create newsletters.

Multiple articles can be associated with a newsletter. Removing an article from a newsletter does not delete the article itself.

---

## Subscriptions

Readers can subscribe to:

* Publishers

* Individual journalists

The application uses Django `ManyToManyField` relationships to manage subscriptions.

The subscribed articles API filters approved articles according to the reader's subscriptions.

---

## API

The application includes a Django REST Framework API.

### API Serializers

The application includes serializers for:

* Users

* Publishers

* Articles

* Newsletters

The `ArticleSerializer` includes:

* ID

* Title

* Content

* Author

* Creation date

* Approval status

* Publisher

The author, creation date, and approval status are controlled by the application rather than being freely supplied by API users.

### API Endpoints

| Endpoint                    | Method | Purpose                                 |
| --------------------------- | ------ | --------------------------------------- |
| `/api/token/`               | POST   | Obtain an authentication token          |
| `/api/articles/`            | GET    | View approved articles                  |
| `/api/articles/`            | POST   | Create an article as a journalist       |
| `/api/articles/<id>/`       | GET    | View an approved article                |
| `/api/articles/<id>/`       | PUT    | Update an article                       |
| `/api/articles/<id>/`       | DELETE | Delete an article                       |
| `/api/articles/subscribed/` | GET    | View articles from reader subscriptions |
| `/api/approved/`            | POST   | Receive article approval information    |

Authentication is handled using Django REST Framework token authentication.

---

## Signals

Django signals are used for automatic application behaviour.

The application includes signals for:

* Automatically assigning users to their role-based group when they register.

* Detecting when an article changes from unapproved to approved.

* Sending email notifications after an article is approved.

* Sending approval information to the application's API endpoint.

The signals are loaded through the `NewsConfig.ready()` method.

---

## Database Models

The main models are:

### CustomUser

Extends Django's `AbstractUser` and includes:

* Role

* Publisher subscriptions

* Journalist subscriptions

### Publisher

Contains:

* Name

* Owner

* Journalists

* Editors

The Publisher model allows a publisher to manage the journalists and editors associated with their publication.

### Article

Contains:

* Title

* Content

* Author

* Creation date

* Approval status

* Publisher

### Newsletter

Contains:

* Title

* Description

* Creation date

* Author

* Articles

---

# Installation and Setup

The following instructions explain how to install and run the project from a fresh computer.

The instructions below assume macOS and use MariaDB/MySQL.

## 1. Clone the Repository

Open Terminal and clone the GitHub repository:

```bash
git clone https://github.com/Giselleg21/news_application.git
```

Enter the project folder:

```bash
cd news_application
```

The project folder uses the lowercase naming convention `news_application`.

---

## 2. Create a Virtual Environment

Create a Python virtual environment:

```bash
python3 -m venv myenv
```

Activate the virtual environment:

```bash
source myenv/bin/activate
```

The terminal should now show `(myenv)` before the command prompt.

---

## 3. Install the Required Python Packages

The project includes a `requirements.txt` file containing the Python packages and versions required by the application.

Install all required dependencies using:

```bash
pip install -r requirements.txt
```

The `requirements.txt` file should contain the versions that are known to work with this project. For example:

```text
Django==4.2.30
djangorestframework==3.16.1
mysqlclient==2.2.7
requests==2.32.5
```

Using specific package versions ensures that the same compatible versions are installed rather than automatically installing the newest available versions, which could introduce compatibility problems.

---

## 4. Install MariaDB

If MariaDB is not already installed, install it using Homebrew:

```bash
brew install mariadb
```

The `pkg-config` package may also be required when installing `mysqlclient`:

```bash
brew install pkg-config
```

Check that MariaDB is available:

```bash
mariadb --version
```

Check whether the MariaDB server is running:

```bash
mariadb-admin ping
```

The expected response is similar to:

```text
mysqld is alive
```

If MariaDB is not running, start it with:

```bash
brew services start mariadb
```

---

## 5. Create the MariaDB Database

Open the MariaDB command line:

```bash
sudo mariadb
```

Create the database:

```sql
CREATE DATABASE news_database;
```

Create a database user:

```sql
CREATE USER 'news_user'@'localhost' IDENTIFIED BY 'news_password';
```

Give the user access to the project database:

```sql
GRANT ALL PRIVILEGES ON news_database.* TO 'news_user'@'localhost';
```

Apply the privileges:

```sql
FLUSH PRIVILEGES;
```

Exit MariaDB:

```sql
EXIT;
```

---

## 6. Configure the Database in Django

Open:

```text
News_application/settings.py
```

The database configuration should point to the MariaDB database:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'news_database',
        'USER': 'news_user',
        'PASSWORD': 'news_password',
        'HOST': 'localhost',
        'PORT': '3306',
    }
}
```

The database credentials should be changed if different credentials are used on another computer.

For a production deployment, database passwords should be stored securely using environment variables rather than being committed directly to source control.

---

## 7. Apply the Database Migrations

Make sure the virtual environment is activated:

```bash
source myenv/bin/activate
```

Run the migrations:

```bash
python manage.py migrate
```

This creates the required database tables in MariaDB.

---

## 8. Create the Application Groups

The application uses Django groups for its role-based permissions.

Run:

```bash
python manage.py create_groups
```

This creates the required:

* Reader group

* Journalist group

* Editor group

* Publisher group

and assigns the appropriate permissions.

---

## 9. Create an Administrator Account

Create a Django superuser:

```bash
python manage.py createsuperuser
```

Follow the prompts to enter:

* Username

* Email address

* Password

The superuser can then access the Django administration site.

---

## 10. Check the Project

Run Django's system check:

```bash
python manage.py check
```

The expected result is:

```text
System check identified no issues (0 silenced).
```

---

## 11. Run the Tests

Run the automated tests:

```bash
python manage.py test
```

The tests should complete successfully before using the application.

The project currently has 30 automated tests, all of which pass successfully.

---

## 12. Start the Development Server

Start Django's development server:

```bash
python manage.py runserver
```

The application will normally be available at:

```text
http://127.0.0.1:8000/
```

Open this address in a web browser.

# Main Application URLs

The main pages include:

```text
/
```

Home page.

```text
/register/
```

Register a new Reader, Journalist, Editor, or Publisher.

```text
/login/
```

Log into an existing account.

```text
/articles/
```

View articles.

```text
/articles/create/
```

Create an article.

```text
/newsletters/
```

View newsletters.

```text
/newsletters/create/
```

Create a newsletter.

```text
/editor/articles/
```

Editor article review page.

```text
/publisher/create/
```

Create a publication as a Publisher.

```text
/publisher/journalists/
```

Manage journalists assigned to a publication.

```text
/publisher/editors/
```

Manage editors assigned to a publication.

```text
/publisher/view/
```

View the Publisher's publication.

```text
/publisher/update/
```

Update the Publisher's publication.

```text
/publisher/delete/
```

Delete the Publisher's publication.

```text
/admin/
```

Django administration site.

---

# Project Structure

The project follows Django's standard project and application structure.

Important directories include:

```text
news_application/

│

├── News/

│   ├── migrations/

│   ├── static/

│   │   └── News/

│   ├── templates/

│   │   └── News/

│   ├── admin.py

│   ├── apps.py

│   ├── forms.py

│   ├── models.py

│   ├── serializers.py

│   ├── signals.py

│   ├── urls.py

│   └── views.py

│

├── News_application/

│   ├── settings.py

│   ├── urls.py

│   ├── asgi.py

│   └── wsgi.py

│

├── manage.py

├── README.md

└── .gitignore
```

The repository/project folder uses lowercase naming (`news_application`) to follow common Python and Django naming conventions.

Python files, classes, functions, and variables follow standard Python naming conventions where applicable.

---

# Email Notifications

During development, the application uses Django's console email backend:

```python
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
```

This means emails are displayed in the terminal rather than being sent through an external email service.

The default sender address is:

```text
news@example.com
```

---

# Technologies Used

* Python

* Django

* Django REST Framework

* MariaDB/MySQL

* HTML

* CSS

* Bootstrap

* Requests

* Git

* GitHub

---

# Version Control

The project is maintained using Git and hosted on GitHub.

The repository contains the Django source code, migrations, templates, static files, tests, and documentation.

Sensitive files such as virtual environments, local SQLite databases, environment files, Python cache files, and operating-system files are excluded using `.gitignore`.
