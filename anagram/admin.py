from django.contrib import admin

from anagram.models import Word


@admin.register(Word)
class WordAdmin(admin.ModelAdmin):
    list_display = ("id", "word", "sorted_word", "sorted_lowercase_word", "is_proper_noun")
    search_fields = ("word", "sorted_word")
    readonly_fields = ("word", "sorted_word", "sorted_lowercase_word", "is_proper_noun")
