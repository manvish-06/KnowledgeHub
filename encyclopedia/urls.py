from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views


urlpatterns = [
    path("", views.index, name = "index"),
    path("wiki/<str:title>/", views.entry, name = "entry"),
    path("search/", views.search, name="search"),
    path("create/", views.create, name="create"),
    path("edit/<str:title>/", views.edit, name = "edit"),
    path("random/", views.random_page, name="random_page"),
    path("author/<str:username>/", views.author_profile, name = "author_profile"),
    path("comment/<int:comment_id>/edit/", views.edit_comment,name="edit_comment"),
    path("comment/<int:comment_id>/delete/", views.delete_comment,name="delete_comment"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("import-wikipedia/", views.import_wikipedia, name="import_wikipedia"),
    path("wiki/<str:title>/ai/", views.ai_assistant, name="ai_assistant"),
    path("wiki/<str:title>/ai/<str:feature>/", views.ai_feature, name="ai_feature"),
    path("wiki/<str:title>/ai/<str:feature>/bookmark/", views.ai_bookmark, name="ai_bookmark"),
    path("ai/export-pdf/", views.export_ai_pdf, name="export_ai_pdf"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,document_root = settings.MEDIA_ROOT)


