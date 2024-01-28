import pytest
from django.urls import reverse
from model_bakery.baker import make

from anagram.models import Word


@pytest.mark.django_db
class TestWordBasicCRUDAPI:
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
        words = ["foo", "bar", "baz", "ofo", "rab", "zab", "oof"]
        payload = {"anagrams": words}
        client.post(reverse("words"), payload, content_type="application/json")
        assert Word.objects.count() == 7

        # Do.
        url = reverse("anagrams-get-anagrams-for-word", kwargs={"word": word})
        response = client.get(url, content_type="application/json")

        # Check.
        assert response.status_code == 200
        assert len(response.data["anagrams"]) == expected_count

    @pytest.mark.parametrize("limit,expected_count", [(1, 1), (2, 2), (5, 2), (0, 0), (None, 2)])
    def test_get_anagrams_for_word_with_limit(self, client, limit, expected_count):
        # Setup.
        words = ["foo", "bar", "baz", "ofo", "rab", "zab", "oof"]
        payload = {"anagrams": words}
        client.post(reverse("words"), payload, content_type="application/json")
        assert Word.objects.count() == 7

        # Do.
        url = reverse("anagrams-get-anagrams-for-word", kwargs={"word": "foo"})
        if limit is not None:
            url = f"{url}?limit={limit}"
        response = client.get(f"{url}", content_type="application/json")

        # Check.
        assert response.status_code == 200
        assert len(response.data["anagrams"]) == expected_count
