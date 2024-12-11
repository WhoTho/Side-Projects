from board import Board
from random import randint


class NodeWord:
    def __init__(self, letter):
        self.letter = letter
        self.children: dict[str, NodeWord] = {}
        self.isEnd = False

    def addWord(self, word):
        if len(word) == 0:
            self.isEnd = True
            return

        if word[0] not in self.children:
            self.children[word[0]] = NodeWord(word[0])

        self.children[word[0]].addWord(word[1:])

    def isWord(self, word):
        if len(word) == 0:
            return self.isEnd

        if word[0] not in self.children:
            return False

        return self.children[word[0]].isWord(word[1:])

    def findWord(self, word):
        if len(word) == 0:
            return self

        if word[0] not in self.children:
            return None

        return self.children[word[0]].findWord(word[1:])

    def getWords(self, prefix=""):
        words = []

        if self.isEnd:
            words.append(prefix)

        for child in self.children.values():
            words += child.getWords(prefix + child.letter)

        return words

    def loadFromFile(self, file):
        letter, isEnd, numOfChildren = file.readline().split()
        self.letter = letter if letter != "None" else ""
        self.isEnd = isEnd == "1"

        for i in range(int(numOfChildren)):
            child = NodeWord("")
            child.loadFromFile(file)
            self.children[child.letter] = child

    def saveToFile(self, file):
        file.write(f"{self.letter or 'None'} {int(self.isEnd)} {len(self.children)}\n")

        for child in self.children.values():
            child.saveToFile(file)


def constructTrie(words):
    root = NodeWord("")

    for word in words:
        word = word.lower()
        if not 3 <= len(word) <= 16:
            continue
        if not any(v in word for v in "aeiouy"):
            continue
        root.addWord(word)

    return root


def loadTrie():
    with open(
        r"C:\Users\alesa\OneDrive\Documents\pythonCode\wordHuntSolver\data\popular-trie.txt",
        "r",
    ) as file:
        root = NodeWord("")
        root.loadFromFile(file)

    return root


def saveTrie(trie):
    with open(
        r"C:\Users\alesa\OneDrive\Documents\pythonCode\wordHuntSolver\data\popular-trie.txt",
        "w",
    ) as file:
        trie.saveToFile(file)

    return trie


# print("Loading trie...")
# words = set()
# with open(
#     r"C:\Users\alesa\OneDrive\Documents\pythonCode\wordHuntSolver\data\popular.txt",
#     "r",
# ) as file:
#     for line in file:
#         words.add(line.strip())
# biggerWords = set()

# with open(
#     r"C:\Users\alesa\OneDrive\Documents\pythonCode\hackMit\words_alpha.txt",
#     "r",
# ) as file:
#     for line in file:
#         biggerWords.add(line.strip())

# # add words in biggest words to words if they are just common suffixes + a word already in words
# COMMON_SUFFIXES = ["s", "ed", "ing", "er", "est", "ly", "y", "es", "ies", "ier", "iest"]

# added = 0
# for suffix in COMMON_SUFFIXES:
#     for word in biggerWords:
#         if word.endswith(suffix) and word[: -len(suffix)] in words:
#             words.add(word)
#             added += 1

# print(f"Added {added} words.")

# trie = constructTrie(words)
# print("Constructed trie.")
# saveTrie(trie)


trie = loadTrie()
print("Loaded trie.")

board = Board()
board.askUserForBoard()
# board.loadBoardString("enumsopdlikeoctw")
board.printBoard()

seenWords = set()


def dfs(x, y, path, node, word):
    results = []
    if node.isEnd:
        if word not in seenWords:
            results.append((word, path))
            seenWords.add(word)

    for nx, ny in board.getAvailableMovesFrom(x, y, path):
        letter = board.getLetterAt(nx, ny)
        if letter in node.children:
            results += dfs(
                nx, ny, path + [(nx, ny)], node.children[letter], word + letter
            )

    return results


WORD_LENGTH_SCORES = [
    0,
    0,
    0,
    100,
    400,
    800,
    1400,
    1800,
    2200,
    2600,
    3000,
    3400,
    3800,
    4200,
    4600,
    5000,
    5400,
    5800,
    6200,
    6600,
]

COMMON_SUFFIXES = ["s", "ed", "ing", "er", "est", "ly", "y", "es", "ies", "ier", "iest"]

score = 0
allPaths = []
allWords = []
for y in range(4):
    for x in range(4):
        letter = board.getLetterAt(x, y)
        if letter in trie.children:
            results = dfs(x, y, [(x, y)], trie.children[letter], letter)
            allowedWords = set()

            for word, path in results:
                if randint(0, 3) <= len(word) - 4:
                    continue
                allowedWords.add(word)

            for word, path in results:
                allWords.append(word)
                for suffix in COMMON_SUFFIXES:
                    if word.endswith(suffix):
                        wordToCheck = word[: -len(suffix)]
                else:
                    wordToCheck = word

                if wordToCheck not in allowedWords:
                    continue

                allPaths.append(path)
                score += WORD_LENGTH_SCORES[len(word)]

lengthCounts = {}
letterCountsNoSuffix = {}
pathLengthCounts = {}

for word in allWords:
    if len(word) not in lengthCounts:
        lengthCounts[len(word)] = 0
    lengthCounts[len(word)] += 1

    for suffix in COMMON_SUFFIXES:
        if word.endswith(suffix):
            word = word[: -len(suffix)]
            break

    if len(word) not in letterCountsNoSuffix:
        letterCountsNoSuffix[len(word)] = 0
    letterCountsNoSuffix[len(word)] += 1

for path in allPaths:
    if len(path) not in pathLengthCounts:
        pathLengthCounts[len(path)] = 0
    pathLengthCounts[len(path)] += 1

print("Length counts:")
for length, count in sorted(lengthCounts.items(), key=lambda x: x[0]):
    print(f"    {length}: {count}")

print("Letter counts (no suffix):")
for length, count in sorted(letterCountsNoSuffix.items(), key=lambda x: x[0]):
    print(f"    {length}: {count}")

print("Path length counts:")
for length, count in sorted(pathLengthCounts.items(), key=lambda x: x[0]):
    print(f"    {length}: {count}")

print()
print("Score:", score)
print("Words found:", len(allWords))
print("Paths found:", len(allPaths))

allWords.sort(key=lambda x: -len(x))
print("Top 20 words (by length):")
for word in allWords[:20]:
    print(word)


board.drawAllPaths(allPaths)
board.start()
