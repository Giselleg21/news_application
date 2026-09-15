# Django News Application

## Overview

This project was developed as a Django capstone application. It demonstrates user authentication, role-based access control, article and newsletter management, subscriptions, editor approval, email notifications, and a RESTful API.

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
* Create and manage newsletters.

Editors are responsible for reviewing articles before they become approved.

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

## Article Approval

The application includes an editor-only article review system.

Editors can access the article review page and select an article to review. They can then approve the article.

When an article is approved:

1. The article's approval status is changed to `True`.
2. Subscribers are identified.
3. Email notifications are sent to relevant subscribers.
4. A POST request is made to the application's `/api/approved/` endpoint.

The email system uses Django's console email backend during development.

## Newsletters

Newsletters contain:

* Title
* Description
* Creation date
* Author
* Associated articles

Journalists and editors can create and manage newsletters.

Multiple articles can be associated with a newsletter. Removing an article from a newsletter does not delete the article itself.

## Subscriptions

Readers can subscribe to:

* Publishers
* Individual journalists

The application uses Django `ManyToManyField` relationships to manage subscriptions.

The subscribed articles API filters approved articles according to the reader's subscriptions.

## API Serializers

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

## Signals

Django signals are used for automatic application behaviour.

The application includes signals for:

* Automatically assigning users to their role-based group when they register.
* Detecting when an article changes from unapproved to approved.
* Sending email notifications after an article is approved.
* Sending approval information to the application's API endpoint.

The signals are loaded through the `NewsConfig.ready()` method.

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
* Journalists
* Editors

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

