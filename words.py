from typing import Generator


def parse_words_dictionary() -> Generator[str, None, None]:
    with open("./words_dictionary.txt", "r") as file:
        while (line := file.readline()) != "":
            word = line[:-1].upper()
            yield word


def parse_words_wordlebot() -> Generator[str, None, None]:
    """Returns a generator of words in the WorldeBot list in alphabetical order"""
    with open("./words_wordlebot.txt", "r") as file:
        while (line := file.readline()) != "":
            word, _ = line.split("\t")
            yield word

def words_generator() -> Generator[str, None, None]:
    yield from parse_words_dictionary()
    yield from parse_words_wordlebot()

def get_words() -> set[str]:
    return set(words_generator())