from django.contrib import admin
from . import models

class AuthorAdmin(admin.ModelAdmin):
    list_display = (
        "id", "full_name"
    )
    fields = ("full_name","created_at", "updated_at")
    readonly_fields = ("created_at","updated_at")

class BookAdmin(admin.ModelAdmin):
    list_display = (
        "id", "title", "author", "categories", "isbn", "publisheddate"
    )
    fields = ("title", "author", "categories", "isbn", "description", "cover_pic","publisheddate", "created_at", "updated_at")
    readonly_fields = ("created_at","updated_at")

class RecommendationAdmin(admin.ModelAdmin):
    list_display = (
        "id", "user", "book", "note"
    )
    fields = ("user", "book", "note", "created_at", "updated_at")
    readonly_fields = ("created_at","updated_at")

class BookRatingAdmin(admin.ModelAdmin):
    list_display = (
        "id", "user", "book", "rate"
    )
    fields = ("user", "book", "rate","created_at", "updated_at")
    readonly_fields = ("created_at","updated_at")

class CommentAdmin(admin.ModelAdmin):
    list_display = (
        "id", "user", "book", "comment"
    )
    fields = ("user", "book", "comment","created_at", "updated_at")
    readonly_fields = ("created_at","updated_at")

admin.site.register(models.Author, AuthorAdmin)
admin.site.register(models.Book, BookAdmin)
admin.site.register(models.Recommendation, RecommendationAdmin)
admin.site.register(models.BookRating, BookRatingAdmin)
admin.site.register(models.Comment, CommentAdmin)
