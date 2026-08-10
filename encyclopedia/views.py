from django.shortcuts import render,redirect,get_object_or_404
from django.http import HttpResponse,Http404,HttpResponseForbidden,JsonResponse
from pathlib import Path 
import markdown2
import random,time,json
from .forms import ProfileForm,EntryForm,CommentForm
from .models import Entry,Comments,Category,Tag,AIBookmark
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.decorators import login_required
from django.db.models import F,Count,Sum,Q
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.contrib import messages
from django.contrib.auth.views import PasswordResetConfirmView
from django.template.loader import render_to_string
from .wikipedia import search_wikipedia,get_full_wikipedia_article,generate_summary,clean_heading,clean_lists,clean_sections,get_article_html,get_article_summary
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.enums import TA_LEFT
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.units import inch
from django.http import FileResponse
from . import wikipedia
from . import ai


# ============================================
# CENTRALIZED AI STUDIO REGISTRY
# ============================================
AI_FEATURES = {
    "summary": {
        "handler": ai.generate_summary, 
        "title": "AI Summary", 
        "icon": "bi-card-text", 
        "supports_difficulty": False
    },
    "explain": {
        "handler": ai.explain_article, 
        "title": "Explain Like I'm 10", 
        "icon": "bi-mortarboard", 
        "supports_difficulty": True
    },
    "notes": {
        "handler": ai.generate_notes, 
        "title": "Study Notes", 
        "icon": "bi-journal-check", 
        "supports_difficulty": True
    },
    "quiz": {
        "handler": ai.generate_quiz, 
        "title": "Quiz Generator", 
        "icon": "bi-patch-question", 
        "supports_difficulty": True
    },
    "flashcards": {
        "handler": ai.generate_flashcards, 
        "title": "Flashcards", 
        "icon": "bi-collection", 
        "supports_difficulty": True
    },
    "mindmap": {
        "handler": ai.generate_mindmap, 
        "title": "Concept Mind Map", 
        "icon": "bi-diagram-3", 
        "supports_difficulty": False
    },
    "related": {
        "handler": ai.related_articles, 
        "title": "Related Topics", 
        "icon": "bi-link-45deg", 
        "supports_difficulty": False
    },
    "chat": {
        "handler": ai.chat_with_article, 
        "title": "Chat with Article", 
        "icon": "bi-chat-dots", 
        "supports_difficulty": False
    },
}



def index(request):

    latest_articles = (
        Entry.objects
        .select_related("author")
        .prefetch_related("categories", "tags")
        .order_by("-created_at")[:6]
    )

    featured_articles = (
        Entry.objects
        .filter(featured=True)
        .select_related("author")
        .prefetch_related("categories")
        .order_by("-created_at")[:3]
    )

    categories = (
        Category.objects.all()[:8]
    )

    total_articles = Entry.objects.count()

    total_comments = Comments.objects.count()

    total_views = (
        Entry.objects.aggregate(
            total=Sum("views")
        )["total"] or 0
    )

    return render(
        request,
        "encyclopedia/index.html",
        {
            "articles": latest_articles,
            "featured_articles": featured_articles,
            "categories": categories,
            "total_articles": total_articles,
            "total_comments": total_comments,
            "total_views": total_views,
        }
    )


def entry(request, title):

    try:
        entry = (
            Entry.objects
            .select_related("author")
            .prefetch_related("comments__author")
            .get(title=title)
        )

        Entry.objects.filter(pk=entry.pk).update(
            views=F("views") + 1
        )

        entry.refresh_from_db()

    except Entry.DoesNotExist:
        return render(
            request,
            "encyclopedia/error.html",
            {
                "message": "Entry not found."
            }
        )

    comments = entry.comments.select_related("author").order_by("-created_at")
    paginator = Paginator(
                comments,
                5
            )
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)


    if request.method == "POST":

        if not request.user.is_authenticated:
            return redirect("login")

        form = CommentForm(request.POST)

        if form.is_valid():

            comment = form.save(commit=False)

            comment.entry = entry

            comment.author = request.user

            comment.save()

            return redirect("entry", title=title)

    else:

        form = CommentForm()

    return render(
        request,
        "encyclopedia/entry.html",
        {
            "title": entry.title,
            "content": markdown2.markdown(entry.content),
            "entry": entry,
            "form": form,
            "page_obj": page_obj
        }
    )


def search(request):

    query = request.GET.get("q", "").strip()

    if not query:
        return redirect("index")

    results = (

        Entry.objects.select_related("author").prefetch_related(
            "categories",
            "tags"
        )

        .filter(

            Q(title__icontains=query)

            |

            Q(summary__icontains=query)

            |

            Q(content__icontains=query)

        )

    )

    wikipedia_results = search_wikipedia(query)


    return render(

        request,

        "encyclopedia/search.html",

        {

            "query": query,

            "results": results,

            "wikipedia_results": wikipedia_results

        }

    )



@login_required
def edit(request, title):

    entry = get_object_or_404(
        Entry.objects.select_related("author")
        .prefetch_related("categories", "tags"),
        title=title
    )


    if request.user != entry.author and not request.user.is_superuser:
        messages.error(
            request,
            "You do not have permission to edit this article."
        )
        return redirect("entry", title=entry.title)

    if request.method == "POST":

        form = EntryForm(
            request.POST,
            instance=entry
        )

        updated_entry = form.save(commit=False)

        updated_entry.author = entry.author

        updated_entry.save()

        form.save_m2m()

        # Handle newly created categories and tags
        form.save_categories_and_tags(updated_entry)

        messages.success(
            request,
            "Article updated successfully!"
        )

        return redirect(
            "entry",
            title=updated_entry.title
        )

    else:

        form = EntryForm(instance=entry)

    return render(
        request,
        "encyclopedia/edit.html",
        {
            "form": form,
            "entry": entry
        }
    )


def random_page(request):

    entries = Entry.objects.all()

    if not entries.exists():
        return render(
            request,
            "encyclopedia/search.html",
            {
                "query": "",
                "results": []
            }
        )

    random_entry = random.choice(entries)

    return redirect(
        "entry",
        title=random_entry.title
    )


@login_required
def create(request):

    if request.method == "GET":

        form = EntryForm()

        return render(
            request,
            "encyclopedia/create.html",
            {
                "form": form
            }
        )

    form = EntryForm(request.POST)

    if form.is_valid():

        entry = form.save(commit=False)

        entry.author = request.user

        entry.save()

        form.save_m2m()

        form.save_categories_and_tags(entry)

        messages.success(
            request,
            "Article created successfully!"
        )

        return redirect(
            "entry",
            title=entry.title
        )

    return render(
        request,
        "encyclopedia/create.html",
        {
            "form": form
        }
    )


def author_profile(request, username):

    author = get_object_or_404(User.objects.annotate(
        total_entries = Count("entries"),
        total_views = Sum("entries__views")
    ).prefetch_related("entries"),
    username=username
    )

    articles = author.entries.all()

    return render(request,"encyclopedia/author_profile.html",
                  {
                      "author": author,
                      "articles": articles,
                  }
            )


@login_required
def edit_comment(request, comment_id):

    comment = get_object_or_404(Comments, pk=comment_id)

    if request.user != comment.author and not request.user.is_superuser:
        return HttpResponseForbidden("You cannot edit this comment.")

    if request.method == "POST":

        form = CommentForm(request.POST, instance=comment)

        if form.is_valid():
            form.save()
            return redirect("entry", title=comment.entry.title)

    else:
        form = CommentForm(instance=comment)

    return render(
        request,
        "encyclopedia/edit_comment.html",
        {
            "form": form,
            "comment": comment,
        }
    )


@login_required
def delete_comment(request, comment_id):

    comment = get_object_or_404(Comments, pk=comment_id)

    if request.user != comment.author and not request.user.is_superuser:
        return HttpResponseForbidden(
            "You cannot delete this comment."
        )

    entry_title = comment.entry.title

    if request.method == "POST":
        comment.delete()
        return redirect("entry", title=entry_title)

    return render(
        request,
        "encyclopedia/delete_comment.html",
        {
            "comment": comment
        }
    )



@login_required
def dashboard(request):

    user = request.user

    articles = (
        Entry.objects
        .filter(author=user)
        .order_by("-created_at")
    )

    recent_articles = articles[:5]

    top_articles = (
        Entry.objects
        .filter(author=user)
        .order_by("-views")[:5]
    )

    recent_comments = (
        Comments.objects
        .filter(author=user)
        .select_related("entry")
        .order_by("-created_at")[:5]
    )

    total_articles = articles.count()

    total_comments = Comments.objects.filter(
        author=user
    ).count()

    total_views = (
        articles.aggregate(
            total=Sum("views")
        )["total"] or 0
    )

    most_viewed = (
        articles.order_by("-views").first()
    )

    return render(
        request,
        "encyclopedia/dashboard.html",
        {
            "articles": articles,
            "recent_articles": recent_articles,
            "top_articles": top_articles,
            "recent_comments": recent_comments,
            "total_articles": total_articles,
            "total_comments": total_comments,
            "total_views": total_views,
            "most_viewed": most_viewed,
        }
    )


class KnowledgeHubPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = "registration/password_reset_confirm.html"

    def get_form(self, form_class=None):
        form = super().get_form(form_class)

        form.fields["new_password1"].widget.attrs.update({
            "class": "form-control",
            "placeholder": "Enter your new password"
        })

        form.fields["new_password2"].widget.attrs.update({
            "class": "form-control",
            "placeholder": "Confirm your new password"
        })

        return form


@login_required
def import_wikipedia(request):

    if request.method != "POST":
        return redirect("index")

    title = request.POST.get("title", "").strip()

    if not title:
        messages.error(
            request,
            "Wikipedia article could not be imported."
        )
        return redirect("index")

    existing_article = Entry.objects.filter(
        title__iexact=title
    ).first()

    if existing_article:
        messages.warning(
            request,
            "This article already exists."
        )
        return redirect(
            "entry",
            title=existing_article.title
        )


    content = get_full_wikipedia_article(title)

    if not content:
        messages.error(
            request,
            "Unable to download the Wikipedia article."
        )
        return redirect("search")


    context = ai.ArticleContext(
    title=title,
    content=content,
    source="wikipedia",
)

    summary = ai.generate_summary(context)


    if not summary or summary.startswith("⚠"):
        summary = ""

    entry = Entry.objects.create(
        title=title,
        summary=summary,
        content=content,
        author=request.user
    )
    messages.success(
        request,
        "Wikipedia article imported successfully."
    )

    return redirect(
        "entry",
        title=entry.title
    )


@login_required
def ai_assistant(request, title):

    article = Entry.objects.filter(
        title__iexact=title
    ).first()

    if article is None:

        class TempArticle:
            pass

        article = TempArticle()
        article.title = title

    return render(
        request,
        "encyclopedia/ai_assistant.html",
        {
            "article": article,
            "features": AI_FEATURES,
            "model_name": ai.MODEL_NAME,
        }
    )


@login_required
def ai_feature(request, title, feature):


    if feature not in ai.FEATURE_FUNCTIONS:

        return JsonResponse(
            {
                "success": False,
                "message": "Unknown AI feature."
            },
            status=404
        )

    difficulty = "standard"

    query = ""

    if request.method == "POST":

        try:
            payload = json.loads(request.body)

            print("PAYLOAD =", payload)

            difficulty = payload.get("difficulty", "standard")
            query = payload.get("query", "")

        except json.JSONDecodeError:
            print("JSON FAILED")

            difficulty = "standard"
            query = ""


    article = Entry.objects.filter(
        title__iexact=title
    ).first()

    cached = False

    result = None


    if article:

        context = ai.ArticleContext(
        title=article.title,
        content=article.content,
        source="database",
        entry=article,
    )

    else:

        wiki_text = wikipedia.get_full_wikipedia_article(title)

        if not wiki_text:

            return JsonResponse(
            {
                "success": False,
                "message": "Unable to fetch article from Wikipedia."
            },
            status=404
        )

        context = ai.ArticleContext(
            title=title,
            content=wiki_text,
            source="wikipedia",
        )

    handler = ai.FEATURE_FUNCTIONS[feature]


    start = time.time()


    result = handler(
        context=context,
        difficulty=difficulty,
        question=query,
    )

    elapsed = round(time.time() - start, 2)

    cached = (
        article is not None and
        getattr(context, "source", "") == "database"
    )

    if result is None:

        return JsonResponse(
            {
                "success": False,
                "message": "Gemini failed to generate a response."
            },
            status=500
        )

    html = render_to_string(
        "encyclopedia/partials/ai_result.html",
        {
            "title": AI_FEATURES[feature]["title"],
            "feature": feature,
            "result": result,
        },
        request=request,
    )

    return JsonResponse(
        {
            "success": True,
            "html": html,
            "raw_markdown": result,
            "cached": cached,
            "time": elapsed,
            "model": ai.MODEL_NAME,
            "tokens": max(1, int(len(result.split()) * 1.3)),
        }
    )


@login_required
def ai_bookmark(request, title, feature):

    if request.method != "POST":
        return JsonResponse(
            {
                "success": False,
                "message": "Only POST requests are allowed."
            },
            status=405
        )

    if feature not in ai.FEATURE_FUNCTIONS:
        return JsonResponse(
            {
                "success": False,
                "message": "Unknown AI feature."
            },
            status=404
        )

    try:
        payload = json.loads(request.body)

    except json.JSONDecodeError:
        return JsonResponse(
            {
                "success": False,
                "message": "Invalid request data."
            },
            status=400
        )

    article = Entry.objects.filter(
        title__iexact=title
    ).first()

    if not article:
        return JsonResponse(
            {
                "success": False,
                "message": "Article not found."
            },
            status=404
        )

    prompt = payload.get("prompt", "")
    response = payload.get("response", "")

    if not response:
        return JsonResponse(
            {
                "success": False,
                "message": "There is no AI response to bookmark."
            },
            status=400
        )

    bookmark, created = AIBookmark.objects.get_or_create(
        user=request.user,
        article=article,
        feature=feature,
        prompt=prompt,
        defaults={
            "response": response
        }
    )

    if not created:
        bookmark.delete()

        return JsonResponse(
            {
                "success": True,
                "bookmarked": False,
                "message": "Bookmark removed."
            }
        )

    return JsonResponse(
        {
            "success": True,
            "bookmarked": True,
            "message": "AI response bookmarked."
        }
    )


@login_required
def export_ai_pdf(request):

    if request.method != "POST":
        return JsonResponse(
            {
                "success": False,
                "message": "Invalid request method."
            },
            status=405
        )

    try:
        payload = json.loads(request.body)

        title = payload.get("title", "AI Result")
        feature = payload.get("feature", "AI Feature")
        content = payload.get("content", "").strip()

    except json.JSONDecodeError:
        return JsonResponse(
            {
                "success": False,
                "message": "Invalid request data."
            },
            status=400
        )

    if not content:
        return JsonResponse(
            {
                "success": False,
                "message": "There is no AI result to export."
            },
            status=400
        )

    buffer = BytesIO()

    document = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=50,
        leftMargin=50,
        topMargin=50,
        bottomMargin=50,
    )

    styles = getSampleStyleSheet()

    title_style = styles["Title"]
    title_style.alignment = TA_LEFT
    title_style.spaceAfter = 12

    feature_style = styles["Heading2"]
    feature_style.spaceAfter = 20

    body_style = styles["BodyText"]
    body_style.leading = 16
    body_style.spaceAfter = 10

    story = []

    story.append(
        Paragraph(
            f"KnowledgeHub — {title}",
            title_style
        )
    )

    story.append(
        Paragraph(
            feature.replace("_", " ").title(),
            feature_style
        )
    )

    paragraphs = content.split("\n")

    for paragraph in paragraphs:

        paragraph = paragraph.strip()

        if not paragraph:
            story.append(Spacer(1, 8))
            continue

        paragraph = paragraph.replace("**", "")
        paragraph = paragraph.replace("__", "")

        story.append(
            Paragraph(
                paragraph,
                body_style
            )
        )

    document.build(story)

    buffer.seek(0)

    safe_title = "".join(
        character
        for character in title
        if character.isalnum() or character in (" ", "-", "_")
    ).strip()

    filename = f"{safe_title or 'AI_Result'}.pdf"

    return FileResponse(
        buffer,
        as_attachment=True,
        filename=filename,
        content_type="application/pdf"
    )

