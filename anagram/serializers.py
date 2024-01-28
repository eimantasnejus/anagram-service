from rest_framework import serializers

from anagram.models import Anagram


class WordSerializer(serializers.ModelSerializer):
    class Meta:
        model = Anagram
        fields = ["id", "word", "sorted_word"]


class AnagramsListSerializer(serializers.Serializer):
    anagrams = serializers.ListField(child=serializers.CharField(max_length=100))


class WordInputSerializer(serializers.Serializer):
    word = serializers.CharField(max_length=100)
