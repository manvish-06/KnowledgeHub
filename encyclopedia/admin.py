from django.contrib import admin
from .models import Entry, Category, Tag, Comments


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    search_fields = ("name",)
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    search_fields = ("name",)
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Entry)
class EntryAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "author",
        "featured",
        "views",
        "created_at",
    )

    search_fields = (
        "title",
        "summary",
        "content",
    )

    list_filter = (
        "featured",
        "categories",
        "tags",
        "created_at",
    )

    filter_horizontal = (
        "categories",
        "tags",
    )

    prepopulated_fields = {
        "slug": ("title",)
    }


@admin.register(Comments)
class CommentsAdmin(admin.ModelAdmin):
    list_display = (
        "author",
        "entry",
        "created_at",
    )

    search_fields = (
        "author__username",
        "content",
    )

