from re import match
from words import FULL_WORD_LIST, possibleAnswers, possibleWords


def reset():
    """
    Resets all the variables
    """

    global NUMBER_OF_DISPLAYED_WORDS, LETTER_FREQ_WEIGHT, LETTER_POS_WEIGHT, LETTER_APPEARANCE_WEIGHT, includedLetters, notIncludedLetters, matchSetup
    NUMBER_OF_DISPLAYED_WORDS = 5
    LETTER_FREQ_WEIGHT = 1
    LETTER_POS_WEIGHT = 1.2
    LETTER_APPEARANCE_WEIGHT = 0.8
    includedLetters = set()
    notIncludedLetters = set()
    matchSetup = ["", "", "", "", ""]


def updateLetterFilters(guessFunc, resultPatternFunc):
    """
    Updates the letter filters
    """

    global notIncludedLetters, includedLetters, matchSetup

    for position in (0, 1, 2, 3, 4):
        letter, result = guessFunc[position], resultPatternFunc[position]

        if result in "by":
            if len(matchSetup[position]) == 0:
                matchSetup[position] = "^" + letter
            elif matchSetup[position][0] == "^":
                matchSetup[position] += letter
            if result == "b":
                notIncludedLetters.add(letter)
            else:
                includedLetters.add(letter)
        elif result == "g":
            includedLetters.add(letter)
            matchSetup[position] = letter
        else:
            print("Error updating letter filters")
            exit()
    notIncludedLetters -= includedLetters


def createRegexMatcher(setupFunc):
    """
    Creates a regex matcher using a setup list
    """
    matchPattern = ""
    for slot in setupFunc:
        if slot == "":
            matchPattern += "."
        elif slot[0] == "^":
            matchPattern += f"[{slot}]"
        else:
            matchPattern += slot
    return matchPattern


def filterWords(
    regexMatcherFunc, possibleWordsFunc, includedLettersFunc, notIncludedLettersFunc
):
    """
    Filters words
    """

    return {
        word
        for word in possibleWordsFunc
        if match(regexMatcherFunc, word)
        and all(x in word for x in includedLettersFunc)
        and all(x not in word for x in notIncludedLettersFunc)
    }


def sortCommonCharacters(wordsFunc):
    """
    Gets a percent score for each character and how often it appears in a word
    """
    letterFreq = {}
    for word in wordsFunc:
        for let in {*word}:
            letterFreq[let] = letterFreq.get(let, 0) + 1
    for key in letterFreq.keys():
        letterFreq[key] /= len(wordsFunc)
    return letterFreq


def sortPositionCharacters(wordsFunc):
    """
    Gets a score for each letter position and how often each letter appears at that position
    """
    positionFreq = [{}, {}, {}, {}, {}]
    for word in wordsFunc:
        for pos, let in enumerate(word):
            positionFreq[pos][let] = positionFreq[pos].get(let, 0) + 1
    for row in (0, 1, 2, 3, 4):
        for key in positionFreq[row]:
            positionFreq[row][key] /= len(wordsFunc)
    return positionFreq


def valueOrBlank(array, index):
    """
    Reutnrs '     ' (5 spaces) if there is no value
    """
    if index >= len(array):
        return "     "
    return array[index]


def printSuggestions(wordsFunc):
    """
    Sorts all the scores and prints everything
    """
    answerFunc = possibleAnswers & wordsFunc
    letterPositionFreq = [
        "scbptamdgrflhwkneovjuyizqx",
        "aoeiurlhnytpmcwksdbgxvzfqj",
        "arionelutsmcdpgbwkvyfzxhjq",
        "eatinlroskdgpcmubhfvwzyjxq",
        "seydtarnlohikmpgcfxuwbzqvj",
    ]
    characterScore = sortCommonCharacters(wordsFunc)
    positionScore = sortPositionCharacters(wordsFunc)

    wordLetterFreq = sorted(
        wordsFunc, key=lambda word: -sum(characterScore[let] for let in {*word}) / 5
    )
    wordLetterPosition = sorted(
        wordsFunc,
        key=lambda word: -sum(positionScore[at][let] for at, let in enumerate(word))
        / 5,
    )
    wordLetterAppearance = sorted(
        wordsFunc,
        key=lambda word: sum(
            letterPositionFreq[at].find(let) for at, let in enumerate(word)
        ),
    )

    wordCombination = sorted(
        wordsFunc,
        key=lambda word: wordLetterFreq.index(word) * LETTER_FREQ_WEIGHT
        + wordLetterAppearance.index(word) * LETTER_APPEARANCE_WEIGHT
        + wordLetterPosition.index(word) * LETTER_POS_WEIGHT,
    )

    possibleAnswersSorted = sorted(
        answerFunc, key=lambda word: wordCombination.index(word)
    )

    numberOfWords = max(
        map(
            len,
            [wordLetterFreq, wordLetterPosition, wordLetterAppearance, wordCombination],
        )
    )
    restrictNumberOfWords = min(numberOfWords, NUMBER_OF_DISPLAYED_WORDS)

    displayList = [
        "\t\t".join(
            map(
                lambda words: valueOrBlank(words, x),
                [
                    wordLetterFreq,
                    wordLetterPosition,
                    wordLetterAppearance,
                    wordCombination,
                    possibleAnswersSorted,
                ],
            )
        )
        for x in range(restrictNumberOfWords)
    ]
    # displayList = ["\t\t".join([valueOrBlank(wordLetterFreq, x), valueOrBlank(wordLetterPosition, x), valueOrBlank(wordLetterAppearance, x), valueOrBlank(wordCombination, x), valueOrBlank(possibleAnswersSorted, x)])for x in range(min(numberOfWords, NUMBER_OF_DISPLAYED_WORDS))]

    print("Suggested words:")
    print(f"{len(wordsFunc)} possible words || {len(answerFunc)} possible answers")
    print("Frequency\tPosition\tAppearance\tBest Guess\tAnswers")
    print(*displayList, sep="\n")

    print("-" * 71 + "\n")


def customSearch(regexSetupFunc, includedLettersFunc, notIncludedLettersFunc):
    regexMatcher = createRegexMatcher(regexSetupFunc)
    possibleWordsFunc = filterWords(
        regexMatcher, FULL_WORD_LIST, includedLettersFunc, notIncludedLettersFunc
    )
    printSuggestions(possibleWordsFunc)


def findBestWordToEliminateLetters(possibleWordsFunc, notIncludedLettersFunc):
    global matchSetup

    alphabet = "abcdefghijklmnopqrstuvwxyz"
    answerFunc = possibleAnswers & {*possibleWordsFunc}
    characterScore = sortCommonCharacters(answerFunc)
    foundWords = set(
        sorted(
            FULL_WORD_LIST,
            key=lambda word: -sum(characterScore.get(let, 0) for let in {*word}) / 5,
        )[:NUMBER_OF_DISPLAYED_WORDS]
    )
    # includedLettersFunc = {letter for letter in "".join(answerFunc) if all(letter not in part for part in matchSetup)}
    # print(includedLettersFunc)
    # for letter in matchSetup:
    #     if len(letter)==1: notIncludedLettersFunc.add(letter)
    # foundWords = filterWords(".....", FULL_WORD_LIST, includedLettersFunc, "")
    printSuggestions(foundWords)


while True:
    reset()
    print("Restarting...")
    while True:
        # set input vars
        guess = ""
        resultPattern = ""
        inGame = True
        # gets guess input
        # has to match 5 letters and has to be a possible word
        while inGame and (
            (not match(r"[a-z]{5}", guess)) or (guess not in FULL_WORD_LIST)
        ):
            guess = input("Input guess >>> ")
            guess = guess.lower()
            if guess == "answer":
                findBestWordToEliminateLetters(possibleWords, notIncludedLetters)
            # if the player types 'restart' then reset everything
            if guess == "restart":
                inGame = False
        if not inGame:
            break

        # get the result
        # has to be 5 chars and can use 'b', 'y', or 'g'
        while not match(r"[byg]{5}", resultPattern):
            resultPattern = input(
                "Result pattern [(b)lank (y)ellow (g)reen] >>> "
            ).lower()

        # update the letter filters used for filtering the possible answers
        updateLetterFilters(guess, resultPattern)

        # creates the list regex matcher
        regexMatcher = createRegexMatcher(matchSetup)

        # filters the words
        possibleWords = filterWords(
            regexMatcher, possibleWords, includedLetters, notIncludedLetters
        )

        # prints everything
        printSuggestions(possibleWords)
