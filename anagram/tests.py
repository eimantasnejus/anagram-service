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
        [("foo", 2), ("bar", 1), ("baz", 1), ("ofo", 2), ("rab", 1), ("zab", 1), ("Zab", 2), ("zzz", 0)],
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

    @pytest.mark.parametrize(
        "exclude_proper_nouns,expected_count",
        [(True, 1), ("true", 1), ("True", 1), (False, 3), ("false", 3), ("False", 3)],
    )
    def test_get_anagrams_for_word_with_proper_noun_toggle(self, client, exclude_proper_nouns, expected_count):
        # Setup.
        self._setup_words(client, ["food", "Food", "Doof", "doof", "rab", "zab", "oof"])

        # Do.
        url = reverse("anagrams-get-anagrams-for-word", kwargs={"word": "food"})
        if exclude_proper_nouns is not None:
            url = f"{url}?exclude_proper_nouns={exclude_proper_nouns}"
        response = client.get(f"{url}", content_type="application/json")

        # Check.
        assert response.status_code == 200, response.data
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

    @pytest.mark.parametrize(
        "test",
        [
            {
                "words": ["foo", "bar", "baz", "ofo", "rab", "zab", "oof", "Foo"],
                "expected_count": 4,
                "expected_anagrams": ["foo", "ofo", "oof", "Foo"],
            },
            {
                "words": ["foo", "bar"],
                "expected_count": 1,
                "expected_anagrams": ["bar"],  # Secondary sorting kicks in here.
            },
            {
                "words": [],
                "expected_count": 0,
                "expected_anagrams": [],
            },
        ],
    )
    def test_get_biggest_anagram_group(self, client, test):
        # Setup.
        self._setup_words(client, test["words"])

        # Do.
        url = reverse("words-get-biggest-anagram-group")
        response = client.get(url, content_type="application/json")

        # Check.
        assert response.status_code == 200
        assert response.data["count"] == test["expected_count"]
        assert sorted(test["expected_anagrams"]) == sorted(response.data["words"])

    @pytest.mark.parametrize(
        "test",
        [
            {
                "words": ["foo", "bar", "baz", "ofo", "rab", "zab", "oof", "Foo"],
                "min_group_size": 2,
                "expected_response_status": 200,
                "expected_total_count": 3,
                "expected_groups": {
                    0: {"count": 4, "words": ["foo", "ofo", "oof", "Foo"]},
                    1: {"count": 2, "words": ["bar", "rab"]},
                    2: {"count": 2, "words": ["baz", "zab"]},
                },
            },
            {
                "words": ["foo", "bar", "baz", "ofo", "rab", "zab", "oof", "Foo"],
                "min_group_size": 2,
                "page": 1,
                "expected_response_status": 200,
                "expected_total_count": 3,
                "expected_groups": {
                    0: {"count": 4, "words": ["foo", "ofo", "oof", "Foo"]},
                    1: {"count": 2, "words": ["bar", "rab"]},
                    2: {"count": 2, "words": ["baz", "zab"]},
                },
            },
            {
                "words": [
                    "ab",
                    "ba",
                    "bc",
                    "cb",
                    "cd",
                    "dc",
                    "de",
                    "ed",
                    "ef",
                    "fe",
                    "fg",
                    "gf",
                    "gh",
                    "hg",
                    "hi",
                    "ih",
                    "ij",
                    "ji",
                    "jk",
                    "kj",
                    "kl",
                    "lk",
                ],
                "min_group_size": 2,
                "page": 1,
                "expected_response_status": 200,
                "expected_total_count": 11,
                "expected_groups": {
                    0: {"count": 2, "words": ["ab", "ba"]},
                    1: {"count": 2, "words": ["bc", "cb"]},
                    2: {"count": 2, "words": ["cd", "dc"]},
                    3: {"count": 2, "words": ["de", "ed"]},
                    4: {"count": 2, "words": ["ef", "fe"]},
                    5: {"count": 2, "words": ["fg", "gf"]},
                    6: {"count": 2, "words": ["gh", "hg"]},
                    7: {"count": 2, "words": ["hi", "ih"]},
                    8: {"count": 2, "words": ["ij", "ji"]},
                    9: {"count": 2, "words": ["jk", "kj"]},
                },
            },
            {
                "words": [
                    "ab",
                    "ba",
                    "bc",
                    "cb",
                    "cd",
                    "dc",
                    "de",
                    "ed",
                    "ef",
                    "fe",
                    "fg",
                    "gf",
                    "gh",
                    "hg",
                    "hi",
                    "ih",
                    "ij",
                    "ji",
                    "jk",
                    "kj",
                    "kl",
                    "lk",
                ],
                "min_group_size": 2,
                "page": 2,
                "expected_response_status": 200,
                "expected_total_count": 11,
                "expected_groups": {
                    0: {"count": 2, "words": ["kl", "lk"]},
                },
            },
            {
                "words": [
                    "ab",
                    "ba",
                    "bc",
                    "cb",
                    "cd",
                    "dc",
                    "de",
                    "ed",
                    "ef",
                    "fe",
                    "fg",
                    "gf",
                    "gh",
                    "hg",
                    "hi",
                    "ih",
                    "ij",
                    "ji",
                    "jk",
                    "kj",
                    "kl",
                    "lk",
                ],
                "min_group_size": 2,
                "page": 3,
                "expected_response_status": 404,  # Page out of range.
            },
            {
                "words": ["foo", "bar", "baz", "ofo", "rab", "zab", "oof", "Foo"],
                "min_group_size": 3,
                "expected_response_status": 200,
                "expected_total_count": 1,
                "expected_groups": {
                    0: {"count": 4, "words": ["foo", "ofo", "oof", "Foo"]},
                },
            },
            {
                "words": ["foo", "bar", "baz", "ofo", "rab", "zab", "oof", "Foo"],
                "min_group_size": 5,
                "expected_response_status": 200,
                "expected_total_count": 0,
                "expected_groups": {},
            },
            {
                "words": [],
                "min_group_size": 2,
                "expected_response_status": 200,
                "expected_total_count": 0,
                "expected_groups": {},
            },
            {
                "words": ["foo", "bar", "baz", "ofo", "rab", "zab", "oof", "Foo"],
                "min_group_size": 1,
                "expected_response_status": 400,  # Minimum group size must be at least 2.
            },
        ],
    )
    def test_get_anagram_groups_above_x(self, client, test):
        # Setup.
        self._setup_words(client, test["words"])

        # Do.
        url = f'{reverse("words-get-anagram-groups-of-at-least-size-x")}?min_group_size={test["min_group_size"]}'
        if "page" in test:
            url = f"{url}&page={test['page']}"
        response = client.get(url, content_type="application/json")

        # Check.
        assert response.status_code == test["expected_response_status"], response.data
        if test["expected_response_status"] == 200:
            assert response.data["count"] == test["expected_total_count"]
            for index, group in enumerate(response.data["results"]):
                assert group["count"] == test["expected_groups"][index]["count"]
                assert sorted(group["words"]) == sorted(test["expected_groups"][index]["words"])

    @pytest.mark.parametrize(
        "test",
        [
            {
                "words": ["foo", "bar", "baz"],
                "expected_response_status": 200,
                "expected_is_anagram": False,
            },
            {
                "words": ["foo", "Foo", "oof"],
                "expected_response_status": 200,
                "expected_is_anagram": True,
            },
            {
                "words": ["foo"],
                "expected_response_status": 400,  # At least two words are required.
            },
            {
                "words": [],
                "expected_response_status": 400,  # At least two words are required.
            },
        ],
    )
    def test_check_if_words_are_anagrams(self, client, test):
        # Do.
        url = reverse("words-check-if-words-are-anagrams")
        payload = {"words": test["words"]}
        response = client.post(url, payload, content_type="application/json")

        # Check.
        assert response.status_code == test["expected_response_status"], response.data
        if test["expected_response_status"] == 200:
            assert response.data["is_anagram"] == test["expected_is_anagram"]

    def test_delete_words_and_its_anagrams(self, client):
        # Setup.
        self._setup_words(client, ["foo", "bar", "ofo", "zab", "oof", "Foo"])

        # Do.
        url = reverse("anagrams-delete-word-and-anagrams", kwargs={"word": "oof"})
        response = client.delete(url, content_type="application/json")

        # Check.
        assert response.status_code == 204
        assert response.data is None
        assert Word.objects.count() == 2
        assert not Word.objects.filter(word="foo").exists()
        assert not Word.objects.filter(word="ofo").exists()
        assert not Word.objects.filter(word="oof").exists()
        assert not Word.objects.filter(word="Foo").exists()
        assert Word.objects.filter(word="bar").exists()
        assert Word.objects.filter(word="zab").exists()
