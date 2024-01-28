from django.db import models


# TODO: Change this to class Word(models.Model):
class Anagram(models.Model):
    word = models.CharField(max_length=100)
    sorted_word = models.CharField(max_length=100)
    # TODO: Add a bool field is_proper_noun. Also extend fixture creator logic.

    def __str__(self):
        return self.word
