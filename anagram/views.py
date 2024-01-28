from django.shortcuts import get_object_or_404
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet, ViewSet

from anagram.models import Word
from anagram.serializers import AnagramsListSerializer, WordInputSerializer


class WordsAPIView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(request=AnagramsListSerializer, responses={status.HTTP_201_CREATED: None})
    def post(self, request):
        """Add a list of words to the database."""
        serializer = AnagramsListSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        words = serializer.validated_data["anagrams"]
        for word in words:
            Word.objects.get_or_create(word=word, sorted_word="".join(sorted(word)))
        return Response(status=status.HTTP_201_CREATED)

    @extend_schema(responses={status.HTTP_200_OK: None})
    def delete(self, request):
        """Delete all words from the database."""
        Word.objects.all().delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class WordViewSet(ViewSet):
    permission_classes = [AllowAny]
    serializer_class = WordInputSerializer

    @action(detail=False, methods=["delete"], url_path=r"<(?P<word>\w+)>.json")
    def delete_word(self, request, word):
        """Delete a word from the database."""
        word_instance = get_object_or_404(Word, word=word)
        word_instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


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
            )
        ],
    )
    @action(detail=False, methods=["get"], url_path=r"<(?P<word>\w+)>.json")
    def get_anagrams_for_word(self, request, word):
        """Get anagrams for a word."""
        sorted_word = "".join(sorted(word))
        anagram_qs = Word.objects.filter(sorted_word=sorted_word).exclude(word=word)
        limit = request.query_params.get("limit")
        if limit is not None:
            anagram_qs = anagram_qs[: int(limit)]
        anagrams_list = list(anagram_qs.values_list("word", flat=True))
        serializer = self.get_serializer({"anagrams": anagrams_list})
        return Response(data=serializer.data, status=status.HTTP_200_OK)
