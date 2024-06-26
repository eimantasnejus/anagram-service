from django.db import models


class Word(models.Model):
    word = models.CharField(max_length=100)
    sorted_word = models.CharField(max_length=100)
    sorted_lowercase_word = models.CharField(max_length=100)
    is_proper_noun = models.BooleanField(default=False)
    length = models.IntegerField()  # TODO: Could be GeneratedField (Django 5)

    def __str__(self):
        return self.word

    class Meta:
        ordering = ["id"]
