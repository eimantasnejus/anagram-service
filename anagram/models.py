from django.db import models


class Anagram(models.Model):
    word = models.CharField(max_length=100)
    sorted_word = models.CharField(max_length=100)

    def __str__(self):
        return self.word
