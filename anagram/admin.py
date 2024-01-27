from django.contrib import admin

from anagram.models import Anagram


@admin.register(Anagram)
class AnagramAdmin(admin.ModelAdmin):
    list_display = ("word", "sorted_word")
    search_fields = ("word", "sorted_word")
