from django import forms
from django.core.exceptions import ValidationError
from .models import (
    Entry,
    Comments,
    Category,
    Tag
)


# ==========================================================
# PROFILE FORM
# ==========================================================

class ProfileForm(forms.Form):

    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Username"
            }
        )
    )

    profile_picture = forms.ImageField(
        required=False
    )


# ==========================================================
# ENTRY FORM
# ==========================================================

class EntryForm(forms.ModelForm):

    categories = forms.ModelMultipleChoiceField(

        queryset=Category.objects.all(),

        required=False,

        widget=forms.CheckboxSelectMultiple

    )

    tags = forms.ModelMultipleChoiceField(

        queryset=Tag.objects.all(),

        required=False,

        widget=forms.CheckboxSelectMultiple

    )

    new_categories = forms.CharField(

        required=False,

        label="Create New Categories",

        help_text="Separate multiple categories using commas.",

        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Example: Data Science, Cyber Security"
            }
        )

    )

    new_tags = forms.CharField(

        required=False,

        label="Create New Tags",

        help_text="Separate multiple tags using commas.",

        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Example: machine-learning, deep-learning"
            }
        )

    )

    class Meta:

        model = Entry

        fields = [

            "title",

            "summary",

            "content",

            "categories",

            "tags",

            "featured"

        ]

        widgets = {

            "title": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter a descriptive title..."
                }
            ),

            "summary": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": "Write a short summary..."
                }
            ),

            "content": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 18,
                    "placeholder": "Write your article using Markdown..."
                }
            ),

            "featured": forms.CheckboxInput(
                attrs={
                    "class": "form-check-input"
                }
            )

        }

        labels = {

            "title": "Article Title",

            "summary": "Summary",

            "content": "Article Content",

            "categories": "Categories",

            "tags": "Tags",

            "featured": "Featured Article"

        }

        help_texts = {

            "title":
                "Choose a clear and descriptive title.",

            "summary":
                "A short summary shown on the homepage and search results.",

            "content":
                "Markdown formatting is supported.",

            "categories":
                "Choose one or more categories.",

            "tags":
                "Choose all relevant tags.",

            "featured":
                "Featured articles appear first on the homepage."

        }

    # ======================================================
    # VALIDATION
    # ======================================================

    def clean_title(self):

        title = self.cleaned_data["title"].strip()

        if len(title) < 5:

            raise ValidationError(
                "Title must contain at least 5 characters."
            )

        return title

    def clean_summary(self):

        summary = self.cleaned_data["summary"].strip()

        if len(summary) < 20:

            raise ValidationError(
                "Summary should contain at least 20 characters."
            )

        return summary

    def clean_content(self):

        content = self.cleaned_data["content"].strip()

        if len(content) < 100:

            raise ValidationError(
                "Article content should contain at least 100 characters."
            )

        return content

    # ======================================================
    # SAVE EXTRA CATEGORIES & TAGS
    # ======================================================

    def save_categories_and_tags(self, entry):

        """
        Saves any new categories and tags entered by the user.
        Existing ones are reused (case-insensitive).
        """

        # -------------------------
        # Categories
        # -------------------------

        new_categories = self.cleaned_data.get(
            "new_categories",
            ""
        )

        if new_categories:

            for name in new_categories.split(","):

                name = name.strip().title()
                name = " ".join(name.strip().split()).title()

                if not name:

                    continue

                category = Category.objects.filter(
                    name__iexact=name
                ).first()

                if category is None:

                    category = Category.objects.create(
                        name=name
                    )

                entry.categories.add(category)

        # -------------------------
        # Tags
        # -------------------------

        new_tags = self.cleaned_data.get(
            "new_tags",
            ""
        )

        if new_tags:

            for name in new_tags.split(","):

                name = name.strip().lower()
                name = "-".join(name.strip().lower().split())

                if not name:

                    continue

                tag = Tag.objects.filter(
                    name__iexact=name
                ).first()

                if tag is None:

                    tag = Tag.objects.create(
                        name=name
                    )

                entry.tags.add(tag)

        return entry


# ==========================================================
# COMMENT FORM
# ==========================================================

class CommentForm(forms.ModelForm):

    class Meta:

        model = Comments

        fields = [
            "content"
        ]

        widgets = {

            "content": forms.Textarea(

                attrs={

                    "class": "form-control",

                    "rows": 5,

                    "placeholder": "Share your thoughts about this article..."

                }

            )

        }

        labels = {

            "content": ""

        }

        help_texts = {

            "content":
                "Keep the discussion respectful and constructive."

        }

    def clean_content(self):

        content = self.cleaned_data["content"].strip()

        if len(content) < 3:

            raise ValidationError(
                "Comment is too short."
            )

        return content

    