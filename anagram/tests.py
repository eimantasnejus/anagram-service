import pytest
from django.urls import reverse
from model_bakery.baker import make

from anagram.models import Word


@pytest.mark.django_db
class TestWordBasicCRUDAPI:
    @staticmethod
    def _setup_words(client, words):
        """Helper method to set up words in the database."""
        payload = {"anagrams": words}
        client.post(reverse("words"), payload, content_type="application/json")
        assert Word.objects.count() == len(words)
        return words

    def test_add_words_to_corpus(self, client):
        # Setup.
        payload = {"anagrams": ["foo", "bar", "baz"]}

        # Do.
        url = reverse("words")
        response = client.post(url, payload, content_type="application/json")

        # Check.
        assert response.status_code == 201
        assert response.data is None
        assert Word.objects.count() == 3
        assert Word.objects.filter(word="foo").exists()

    def test_delete_all_words_from_corpus(self, client):
        # Setup.
        make(Word, _quantity=3)
        assert Word.objects.count() == 3

        # Do.
        url = reverse("words")
        response = client.delete(url, content_type="application/json")

        # Check.
        assert response.status_code == 204
        assert response.data is None
        assert Word.objects.count() == 0

    def test_delete_single_word_from_corpus(self, client):
        # Setup.
        make(Word, _quantity=3)
        assert Word.objects.count() == 3
        word = Word.objects.first()

        # Do.
        url = reverse("words-delete-word", kwargs={"word": word.word})
        response = client.delete(url, content_type="application/json")

        # Check.
        assert response.status_code == 204
        assert response.data is None
        assert Word.objects.count() == 2
        assert not Word.objects.filter(word=word.word).exists()

    @pytest.mark.parametrize(
        "word,expected_count",
        [("foo", 2), ("bar", 1), ("baz", 1), ("ofo", 2), ("rab", 1), ("zab", 1), ("Zab", 0), ("zzz", 0)],
    )
    def test_get_anagrams_for_word(self, client, word, expected_count):
        # Setup.
        self._setup_words(client, ["foo", "bar", "baz", "ofo", "rab", "zab", "oof"])

        # Do.
        url = reverse("anagrams-get-anagrams-for-word", kwargs={"word": word})
        response = client.get(url, content_type="application/json")

        # Check.
        assert response.status_code == 200
        assert len(response.data["anagrams"]) == expected_count

    @pytest.mark.parametrize("limit,expected_count", [(1, 1), (2, 2), (5, 2), (0, 0), (None, 2)])
    def test_get_anagrams_for_word_with_limit(self, client, limit, expected_count):
        # Setup.
        self._setup_words(client, ["foo", "bar", "baz", "ofo", "rab", "zab", "oof"])

        # Do.
        url = reverse("anagrams-get-anagrams-for-word", kwargs={"word": "foo"})
        if limit is not None:
            url = f"{url}?limit={limit}"
        response = client.get(f"{url}", content_type="application/json")

        # Check.
        assert response.status_code == 200
        assert len(response.data["anagrams"]) == expected_count


@pytest.mark.django_db
class TestWordAdvancedAPI:
    @staticmethod
    def _setup_words(client, words):
        """Helper method to set up words in the database."""
        payload = {"anagrams": words}
        client.post(reverse("words"), payload, content_type="application/json")
        assert Word.objects.count() == len(words)
        return words

    @pytest.mark.parametrize(
        "test",
        [
            {
                "words": ["fo", "bard", "bazinga", "ofo", "rab", "zab", "oof", "successful"],
                "expected": {
                    "total_words": 8,
                    "min_word_length": 2,
                    "max_word_length": 10,
                    "median_word_length": 3.0,
                    "average_word_length": 4.375,
                },
            },
            {
                "words": ["single"],
                "expected": {
                    "total_words": 1,
                    "min_word_length": 6,
                    "max_word_length": 6,
                    "median_word_length": 6.0,
                    "average_word_length": 6.0,
                },
            },
            {
                "words": ["first", "second"],
                "expected": {
                    "total_words": 2,
                    "min_word_length": 5,
                    "max_word_length": 6,
                    "median_word_length": 5.5,
                    "average_word_length": 5.5,
                },
            },
            {
                "words": [],
                "expected": {
                    "total_words": 0,
                    "min_word_length": None,
                    "max_word_length": None,
                    "median_word_length": None,
                    "average_word_length": None,
                },
            },
        ],
    )
    def test_get_corpus_length_stats(self, client, test):
        # Setup.
        self._setup_words(client, test["words"])

        # Do.
        url = reverse("words-get-word-length-statistics")
        response = client.get(url, content_type="application/json")

        # Check.
        assert response.status_code == 200
        assert response.data["total_words"] == test["expected"]["total_words"]
        assert response.data["min_word_length"] == test["expected"]["min_word_length"]
        assert response.data["max_word_length"] == test["expected"]["max_word_length"]
        assert response.data["median_word_length"] == test["expected"]["median_word_length"]
        assert response.data["average_word_length"] == test["expected"]["average_word_length"]
