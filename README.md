@'
# KnowledgeHub

KnowledgeHub is a full-stack knowledge and learning platform built with Django. It combines a community-driven encyclopedia with Wikipedia integration and an AI-powered learning workspace.

The platform allows users to discover, create, edit, and discuss knowledge while using AI tools to understand and study topics more effectively.

## Features

### Knowledge & Articles

- Browse knowledge articles
- Create new articles
- Edit existing articles
- Delete articles
- Categories and tags
- Featured articles
- Latest articles
- Article view tracking
- Author profiles
- Comments and discussions

### Search

- Search KnowledgeHub articles
- Search and explore Wikipedia
- Retrieve Wikipedia article information
- Import useful Wikipedia content into the knowledge platform

### AI Learning Workspace

KnowledgeHub includes an AI-powered workspace with multiple learning tools:

- AI Summary
- Explain Like I'm 10
- Study Notes
- Quiz Generator
- Flashcards
- Concept Mind Maps
- Related Topics
- Chat with Article
- Difficulty-based explanations
- AI bookmarks

### Authentication

- User registration
- Login and logout
- Password reset
- User profiles
- Authentication-protected actions

### Community Features

- Add comments to articles
- Edit comments
- Delete comments
- Author information
- Article discussions

### Additional Features

- PDF generation
- Markdown-based content rendering
- Responsive interface
- Static file handling with WhiteNoise
- Production deployment support

## Technology Stack

### Backend

- Python
- Django
- Django ORM

### Frontend

- HTML
- CSS
- JavaScript
- Bootstrap
- Bootstrap Icons

### Database

- SQLite for local development
- PostgreSQL with Neon for production

### APIs & Services

- Wikipedia integration
- Google Gemini AI
- Neon PostgreSQL

### Deployment

- Git
- GitHub
- Render
- Gunicorn
- Uvicorn
- WhiteNoise

## Project Structure

```text
KnowledgeHub/
|
+-- accounts/
|   +-- migrations/
|   +-- templates/
|   +-- forms.py
|   +-- models.py
|   +-- signals.py
|   +-- urls.py
|   +-- views.py
|
+-- encyclopedia/
|   +-- migrations/
|   +-- static/
|   +-- templates/
|   +-- ai.py
|   +-- forms.py
|   +-- models.py
|   +-- views.py
|   +-- wikipedia.py
|   +-- urls.py
|
+-- wiki_project/
|   +-- settings.py
|   +-- urls.py
|   +-- middleware.py
|   +-- asgi.py
|   +-- wsgi.py
|
+-- manage.py
+-- requirements.txt
+-- .gitignore
+-- README.md




