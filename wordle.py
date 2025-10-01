from dataclasses import dataclass
from enum import Enum
import random
import re
from words import get_words
from matplotlib import pyplot as plt
import numpy as np

class colors:
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    WHITE = "\033[37m"
    CYAN = "\033[36m"
    DEFAULT = "\033[90m"


class Correctness(Enum):
    CORRECT = 0
    WRONG_LOCATION = 1
    MISSING = 2


@dataclass
class CharResult:
    char: str
    correctness: Correctness

RATIO = 2.5

WordResult = tuple[CharResult, ...]  # tehcnically always len 5, but cannot be typed properly elsewhere

def play():
    words = list(get_words())
    word = random.choice(words)
    guess = None
    results: list[WordResult] = []
    while guess is None or guess.upper() != word:
        guess = input(colors.DEFAULT + "guess: " + colors.WHITE).upper()
        if len(guess) != 5:
            print(guess)
            if guess == "":
                print(f"\trecommendation:", recommend(words, results))
            else:
                print("learn to count")
            continue
        
        result = evaluate(word, guess)
        results.append(result)
        for r in results:
            print(repr_result(r))


def solve():
    print("when giving input, type each character followed by !, ?, or x (for correct, wrong spot, incorrect) (e.g. t! a? rx e! sx)")
    words = list(get_words())
    results: list[WordResult] = []
    while True:
        if not results:
            recommendation = "TARES"
        else:
            recommendation = recommend(words, results)
        print("\trecommendation:", recommendation)
        print(colors.DEFAULT + "how'd it do?" + colors.CYAN)
        result = input()
        if result.lower() == "back":
            results = results[:-1]
        else:
            results.append(interpret_evaluation(result))
        for r in results:
            print(repr_result(r))
        


def find_best():
    words = list(get_words())
    avg_scores = dict()

    for word in words:
        # print(f"{colors.WHITE}[{colors.GREEN}{str(i+1).rjust(4, '0')}{colors.WHITE}] {colors.CYAN}{word} ", end="")
        avg_scores[word] = get_average_score(word, words)
        # print(f"{colors.WHITE}[{colors.DEFAULT}{avg_score:.3f}{colors.WHITE}]")

    scores_array = np.array(list(avg_scores.values()))

    n_bins = 50
    bins = np.linspace(scores_array.min(), scores_array.max(), n_bins)

    plt.hist(scores_array, bins)
    plt.show()

    sorted_scores = sorted(avg_scores.items(), key=lambda t: t[1], reverse=True)
    print(sorted_scores[:20], sorted_scores[-20:])


def recommend(words: list[str], results: list[WordResult]):
    regex_statements = []
    for result in results:
        conditions = []
        # this regex approach does not consider stacking of WRONG_LOCATION 
        # (e.g. two T's in the wrong location would be solved by a single T in another position)
        for i, char_result in enumerate(result):
            match char_result.correctness:
                case Correctness.CORRECT:
                    conditions.append(f"(?=.{{{i}}}{char_result.char})")  # ensure specific char at this pos
                case Correctness.WRONG_LOCATION:
                    conditions.append(f"(?=.*{char_result.char})") # ensure char exists somewhere
                    conditions.append(f"(?!.{{{i}}}{char_result.char})") # forbin char at this pos (opposite of CORRECT condition)
                case Correctness.MISSING:
                    conditions.append(f"(?!.*{char_result.char})") # forbid char from existing anywhere
        
        regex_statements.append("".join(conditions))

    regex = re.compile("^" + "".join(regex_statements) + ".....$")
    filtered_words = filter(
        lambda word: regex.match(word),
        words
    )
    try:
        choice_word, _ = max({word: get_average_score(word, words) for word in filtered_words}.items(), key=lambda t: t[1])
    except ValueError:
        return None
    return choice_word



def get_all_scores(word: str, words: list[str]):
    return {other: score(evaluate(word, other)) for other in words}


def get_average_score(word: str, words: list[str]):
    n_words = len(words)
    return (sum(get_all_scores(word, words).values()) - len(word)*RATIO) / (n_words - 1)


def score(result: WordResult):
    score = 0.0
    wrong_location_pts = 1
    correct_pts = RATIO
    for char_result in result:
        match char_result.correctness:
            case Correctness.CORRECT:
                score += correct_pts
            case Correctness.WRONG_LOCATION:
                score += wrong_location_pts
            case Correctness.MISSING | _:
                pass
    return score


def interpret_evaluation(string: str) -> WordResult:
    string = string.replace(" ", "").upper()
    char_results = []
    for i, char in enumerate(string[::2]):
        indicator = string[2*i+1]
        char_results.append(
            CharResult(
                char,
                {
                    "!": Correctness.CORRECT,
                    "?": Correctness.WRONG_LOCATION,
                    "X": Correctness.MISSING,
                }[indicator]
            )
        )
    return tuple(char_results)

def evaluate(word: str, guess: str) -> WordResult:
    result: list[CharResult] = []
    hinted_count: dict[str, int] = {}
    # pre-fill spaces which will be correct
    for i, char in enumerate(guess):
        hinted_count.setdefault(char, 0)
        if char == word[i]:
            hinted_count[char] += 1
    
    for i, char in enumerate(guess):
        if char == word[i]:
            result.append(CharResult(char, Correctness.CORRECT))
        elif char in word:
            if hinted_count[char] < word.count(char):
                c = Correctness.WRONG_LOCATION
            else:
                c = Correctness.MISSING
            result.append(CharResult(char, c))
            hinted_count[char] += 1
        else:
            result.append(CharResult(char, Correctness.MISSING))
    
    return tuple(result)

def repr_result(result: WordResult) -> str:
    string = ""
    for char_result in result:
        match char_result.correctness:
            case Correctness.CORRECT:
                color = colors.GREEN
            case Correctness.WRONG_LOCATION:
                color = colors.YELLOW
            case Correctness.MISSING | _:
                color = colors.DEFAULT
        string += f"{color}{char_result.char} "
    return string + colors.WHITE


if __name__ == "__main__":  
    play()