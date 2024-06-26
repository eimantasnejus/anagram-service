from rest_framework import serializers

from anagram.models import Word


class WordSerializer(serializers.ModelSerializer):
    class Meta:
        model = Word
        fields = ["id", "word", "sorted_word"]


class AnagramsListSerializer(serializers.Serializer):
    anagrams = serializers.ListField(child=serializers.CharField(max_length=100))


class SimpleWordSerializer(serializers.Serializer):
    word = serializers.CharField(max_length=100)


class WordLengthStatsSerializer(serializers.Serializer):
    total_words = serializers.IntegerField()
    min_word_length = serializers.IntegerField()
    max_word_length = serializers.IntegerField()
    average_word_length = serializers.FloatField()
    median_word_length = serializers.FloatField()


class WordListSerializer(serializers.Serializer):
    words = serializers.ListField(child=serializers.CharField(max_length=100))

    def validate_words(self, value):
        if len(value) < 2:
            raise serializers.ValidationError("At least two words are required.")
        return value


class MostAnagramsSerializer(serializers.Serializer):
    count = serializers.IntegerField()
    words = serializers.ListField(child=serializers.CharField(max_length=100))


class WordAnagramCountSerializer(serializers.Serializer):
    word = serializers.CharField(max_length=100)
    anagrams_count = serializers.IntegerField()


class IsAnagramSerializer(serializers.Serializer):
    is_anagram = serializers.BooleanField()


class PaginatedAnagramGroupSerializer(serializers.Serializer):
    count = serializers.IntegerField()
    next = serializers.URLField(allow_null=True)
    previous = serializers.URLField(allow_null=True)
    results = MostAnagramsSerializer(many=True)
