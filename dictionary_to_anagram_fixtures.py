# TODO: This could be converted to a Django management command.
import json

INPUT_FILE = "dictionary.txt"
OUTPUT_FILE = "anagram/fixtures/word.json"
MODEL = "anagram.Word"

words = []

# Read TXT file and create a list of dicts representing words.
with open(INPUT_FILE) as f:
    for i, line in enumerate(f, start=1):
        word = line.strip()
        words.append(
            {
                "model": MODEL,
                "pk": i,
                "fields": {
                    "word": word,
                    "sorted_word": "".join(sorted(word)),
                    "sorted_lowercase_word": "".join(sorted(word.lower())),
                    "is_proper_noun": word.istitle(),
                    "length": len(word),
                },
            }
        )

# Write the list of dicts to a JSON file so that it can be loaded into the database as a fixture.
with open(OUTPUT_FILE, "w") as f:
    json.dump(words, f)
