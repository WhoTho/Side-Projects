# Word Hunt Solver

This project is a Word Hunt Solver that uses a Trie data structure to find all possible words on a given 4x4 board. The project consists of two main components: `Board` and `Trie`.

The solver currently only includes popular/common words from [this dictionary](https://github.com/dolph/dictionary).

The solver only takes a portion of found words (the longer the word the less likely it is to be "found") and displays them on the board.

## Files

### `board.py`

This file contains the `Board` class which is responsible for:

-   Initializing a 4x4 board using Tkinter for GUI representation.
-   Asking the user for board input.
-   Loading a board from a string.
-   Displaying the board.
-   Finding available moves from a given position.
-   Drawing paths on the board.

### `trie.py`

This file contains the `NodeWord` class and functions to manage the Trie data structure. It includes:

-   Adding words to the Trie.
-   Checking if a word exists in the Trie.
-   Finding words in the Trie.
-   Loading and saving the Trie from/to a file.
-   Constructing a Trie from a list of words.
-   Depth-first search (DFS) to find all possible words on the board.

## Usage

1. Ensure you have the required dependencies installed:

    ```sh
    pip install tkinter
    ```

2. Run the `trie.py` file:
    ```sh
    python trie.py
    ```
