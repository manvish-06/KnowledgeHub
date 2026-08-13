# KnowledgeHub 🚀

> A modern, production-grade learning and knowledge-sharing platform built with Django. KnowledgeHub seamlessly merges community-driven articles with live Wikipedia search and an intelligent, AI-powered study workspace driven by Google's Gemini API.

---

## 🌟 Overview

**KnowledgeHub** is designed for students, developers, and lifelong learners. It transforms static reading into an interactive study experience. Beyond standard CRUD operations for knowledge articles, KnowledgeHub allows users to fetch and import content directly from Wikipedia and interact with articles using automated summarization, flashcard generation, quiz creation, and dynamic AI Q&A chat.

---

## ✨ Key Features

### 📚 Knowledge & Article Engine
* **Full Article Lifecycle**: Create, read, update, and delete markdown-formatted articles.
* **Organization**: Categorize articles with dynamic tags and category pills.
* **Curated Content**: Highlighted sections for *Featured Articles* and *Latest Content*.
* **Analytics**: Live view counters and reading metrics for every published post.

### 🌐 Live Wikipedia Integration
* **Live Query Engine**: Search Wikipedia articles directly from KnowledgeHub.
* **Content Import**: Seamlessly import Wikipedia content into the local database for editing or AI processing.

### 🤖 AI-Powered Workspace (Google Gemini)
* **Smart Summarization**: Generate concise, executive summaries of long articles.
* **Explain Like I'm 10 (ELI10)**: Simplify complex technical concepts into beginner-friendly explanations.
* **Quiz & Flashcard Generator**: Automatically extract key takeaways into self-assessment quizzes and revision cards.
* **Interactive Mind Maps**: Output visual/structural concept trees for quick mental mapping.
* **Chat with Article**: An inline AI assistant trained specifically on the context of the active article to answer user questions on demand.
* **AI Bookmarks**: Save AI-generated outputs for future study sessions.

### 👤 User Management & Community
* **Secure Authentication**: Registration, login/logout, profile management, and password reset flows.
* **Interactive Discussions**: Threaded comment section with edit/delete capabilities for original authors.
* **Author Profiles**: Dedicated user profile pages displaying dynamic timelines and published contributions.

---

## 🛠️ Technology Stack

### Backend
* **Language**: Python 3.12+
* **Framework**: Django 5.x
* **ORM**: Django ORM
* **WSGI/ASGI**: Gunicorn / Uvicorn

### Frontend
* **Core**: HTML5, CSS3 (Custom Variables, Flexbox, Grid), JavaScript (ES6+)
* **Styling Framework**: Bootstrap 5 & Bootstrap Icons
* **UI Themes**: Obsidian Slate & Deep Teal / Custom Dark Palette

### Database
* **Development**: SQLite3
* **Production**: PostgreSQL (Hosted via Neon DB)

### APIs & Deployment
* **AI Engine**: Google Gemini API (`google-genai` / `google-generativeai`)
* **External Data**: Wikipedia REST API
* **Static Asset Hosting**: WhiteNoise
* **Hosting Platform**: Render

---

## 📁 Project Structure

```text
KnowledgeHub/
│
├── accounts/                  # User Management & Authentication App
│   ├── migrations/
│   ├── templates/accounts/    # Login, Registration, Profile Templates
│   ├── forms.py               # Custom Auth Forms
│   ├── models.py              # User Profiles & Custom User Models
│   ├── signals.py             # Profile Auto-creation Signals
│   ├── urls.py
│   └── views.py
│
├── encyclopedia/              # Core Content & AI Workspace App
│   ├── migrations/
│   ├── static/encyclopedia/
│   │   ├── css/               # Modular CSS (style.css, ai_workspace.css)
│   │   └── js/                # Client Engine (ai_workspace.js, script.js)
│   ├── templates/encyclopedia/
│   ├── ai.py                  # Gemini API Service Layer & Prompt Engineering
│   ├── forms.py               # Article Creation & Comment Forms
│   ├── models.py              # Entry, Category, Comment & Bookmark Models
│   ├── views.py               # Article CRUD & Async AI Endpoints
│   ├── wikipedia.py           # Wikipedia API Integration Utilities
│   └── urls.py
│
├── wiki_project/              # Root Configuration Directory
│   ├── settings.py            # Global Settings & Production Configs
│   ├── urls.py                # Global Route Resolver
│   ├── middleware.py          # Custom Project Middleware
│   ├── asgi.py
│   └── wsgi.py
│
├── manage.py
├── requirements.txt
├── .gitignore
└── README.md






