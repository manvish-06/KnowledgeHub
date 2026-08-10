from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify


class Category(models.Model):
    name = models.CharField(
        max_length=100,
        unique=True
    )

    slug = models.SlugField(
        unique=True,
        blank=True
    )

    description = models.TextField(
        blank=True
    )

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)

        super().save(*args, **kwargs)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Tag(models.Model):
    name = models.CharField(
        max_length=50,
        unique=True
    )

    slug = models.SlugField(
        unique=True,
        blank=True
    )

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)

        super().save(*args, **kwargs)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Entry(models.Model):

    title = models.CharField(
        max_length=150,
        unique=True
    )

    slug = models.SlugField(
        unique=True,
        blank=True
    )

    summary = models.TextField(
        blank=True
    )

    content = models.TextField()

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="entries"
    )

    categories = models.ManyToManyField(
        Category,
        related_name="entries",
        blank=True
    )

    tags = models.ManyToManyField(
        Tag,
        related_name="entries",
        blank=True
    )

    views = models.PositiveIntegerField(
        default=0
    )

    featured = models.BooleanField(
        default=False
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    def save(self, *args, **kwargs):

        # if not self.slug:
        #     self.slug = slugify(self.title)

        base_slug = slugify(self.title)

        slug = base_slug

        counter = 1

        while Entry.objects.filter(slug=slug).exclude(pk=self.pk).exists():

            slug = f"{base_slug}-{counter}"

            counter += 1

        self.slug = slug

        super().save(*args, **kwargs)

    @property
    def word_count(self):
        return len(self.content.split())

    @property
    def reading_time(self):
        return max(1, (self.word_count + 199) // 200)

    @property
    def short_summary(self):

        if self.summary:
            return self.summary

        return self.content[:180] + "..."

    @property
    def is_recent(self):
        from django.utils import timezone
        from datetime import timedelta

        return self.created_at >= timezone.now() - timedelta(days=7)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Article"
        verbose_name_plural = "Articles"

    def __str__(self):
        return self.title


class Comments(models.Model):

    entry = models.ForeignKey(
        Entry,
        on_delete=models.CASCADE,
        related_name="comments"
    )

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="comments"
    )

    content = models.TextField()

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        # return f"{self.author.username} - {self.entry.title}"
        return f"{self.author.username} on {self.entry.title}"



class AIResponse(models.Model):

    FEATURE_CHOICES = [

        ("summary", "Summary"),
        ("explain", "Explain"),
        ("notes", "Study Notes"),
        ("quiz", "Quiz"),
        ("chat", "Chat"),
    ]

    article = models.ForeignKey(
        Entry,
        on_delete=models.CASCADE,
        related_name="ai_responses"
    )

    feature = models.CharField(
        max_length=20,
        choices=FEATURE_CHOICES
    )

    prompt_hash = models.CharField(
        max_length=64
    )

    response = models.TextField()

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:

        unique_together = (
            "article",
            "feature",
            "prompt_hash"
        )

        ordering = ["-updated_at"]

    def __str__(self):

        return f"{self.article.title} - {self.feature}"


class AIBookmark(models.Model):

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="ai_bookmarks"
    )

    article = models.ForeignKey(
        Entry,
        on_delete=models.CASCADE,
        related_name="ai_bookmarks"
    )

    feature = models.CharField(
        max_length=20
    )

    prompt = models.TextField(
        blank=True
    )

    response = models.TextField()

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        ordering = ["-created_at"]

        constraints = [
            models.UniqueConstraint(
                fields=["user", "article", "feature", "prompt"],
                name="unique_ai_bookmark"
            )
        ]

    def __str__(self):
        return f"{self.user.username} - {self.article.title} - {self.feature}"

    
