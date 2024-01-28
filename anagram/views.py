from django.db.models import Avg, Count, Max, Min
from django.shortcuts import get_object_or_404
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet, ViewSet

from anagram.helpers import calculate_median, to_python_bool
from anagram.models import Word
from anagram.serializers import (
    AnagramsListSerializer,
    IsAnagramSerializer,
    MostAnagramsSerializer,
    SimpleWordSerializer,
    WordLengthStatsSerializer,
    WordListSerializer,
)


class WordAPIView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(request=AnagramsListSerializer, responses={status.HTTP_201_CREATED: None})
    def post(self, request):
        """Add a list of words to the database."""
        serializer = AnagramsListSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        words = serializer.validated_data["anagrams"]
        for word in words:
            Word.objects.get_or_create(
                word=word,
                sorted_word="".join(sorted(word)),
                sorted_lowercase_word="".join(sorted(word.lower())),
                is_proper_noun=word.istitle(),
                length=len(word),
            )
        return Response(status=status.HTTP_201_CREATED)

    @extend_schema(responses={status.HTTP_200_OK: None})
    def delete(self, request):
        """Delete all words from the database."""
        Word.objects.all().delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class WordViewSet(ViewSet):
    permission_classes = [AllowAny]
    serializer_class = SimpleWordSerializer

    @action(detail=False, methods=["delete"], url_path=r"<(?P<word>\w+)>.json")
    def delete_word(self, request, word):
        """Delete a word from the database."""
        word_instance = get_object_or_404(Word, word=word)
        word_instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=["get"], url_path=r"length-stats", serializer_class=WordLengthStatsSerializer)
    def get_word_length_statistics(self, request):
        """Collect statistics about length of words in database."""
        stats = Word.objects.aggregate(
            words_count=Count("id"),
            min_word_length=Min("length"),
            max_word_length=Max("length"),
            average_word_length=Avg("length"),
        )
        median = calculate_median(list(Word.objects.values_list("length", flat=True).order_by("length")))
        average = stats["average_word_length"]

        serializer = WordLengthStatsSerializer(
            {
                "total_words": stats["words_count"],
                "min_word_length": stats["min_word_length"],
                "max_word_length": stats["max_word_length"],
                "median_word_length": float(f"{median:.4f}") if median is not None else None,
                "average_word_length": float(f"{average:.4f}") if average is not None else None,
            }
        )
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=["get"], url_path=r"biggest-anagram-group", serializer_class=MostAnagramsSerializer)
    def get_biggest_anagram_group(self, request):
        """Get the biggest group of words that are anagrams of each other."""
        anagram_groups = Word.objects.values("sorted_lowercase_word").annotate(count=Count("id"))
        biggest_group = anagram_groups.order_by("-count", "sorted_lowercase_word").first()
        if biggest_group is None:
            return Response(MostAnagramsSerializer({"count": 0, "words": []}).data)
        words_in_biggest_group = Word.objects.filter(sorted_lowercase_word=biggest_group["sorted_lowercase_word"])
        serializer = MostAnagramsSerializer({"count": len(words_in_biggest_group), "words": words_in_biggest_group})
        return Response(serializer.data)

    @extend_schema(request=WordListSerializer, responses=IsAnagramSerializer)
    @action(detail=False, methods=["post"], url_path=r"anagram-check")
    def check_if_words_are_anagrams(self, request):
        """Check if a list of words are anagrams of each other."""
        serializer = WordListSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        words = serializer.validated_data["words"]

        sorted_lowercase_words = ["".join(sorted(word.lower())) for word in words]
        is_anagram = len(set(sorted_lowercase_words)) == 1

        return Response(IsAnagramSerializer({"is_anagram": is_anagram}).data)


class AnagramViewSet(GenericViewSet):
    permission_classes = [AllowAny]
    serializer_class = AnagramsListSerializer

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="limit",
                description="Limit the number of results returned.",
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
            ),
            OpenApiParameter(
                name="exclude_proper_nouns",
                description="Exclude proper nouns from the results.",
                type=OpenApiTypes.BOOL,
                location=OpenApiParameter.QUERY,
            ),
        ],
    )
    @action(detail=False, methods=["get"], url_path=r"<(?P<word>\w+)>.json")
    def get_anagrams_for_word(self, request, word):
        """Get anagrams for a word."""
        sorted_lowercase_word = "".join(sorted(word.lower()))
        anagram_qs = Word.objects.filter(sorted_lowercase_word=sorted_lowercase_word).exclude(word=word)
        limit = request.query_params.get("limit")
        if limit is not None:
            anagram_qs = anagram_qs[: int(limit)]
        exclude_proper_nouns = request.query_params.get("exclude_proper_nouns")
        if exclude_proper_nouns and to_python_bool(exclude_proper_nouns):
            anagram_qs = anagram_qs.exclude(is_proper_noun=True)
        anagrams_list = list(anagram_qs.values_list("word", flat=True))
        serializer = self.get_serializer({"anagrams": anagrams_list})
        return Response(data=serializer.data, status=status.HTTP_200_OK)
