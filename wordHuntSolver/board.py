import tkinter as tk


class Board:
    def __init__(self):
        self.board = []
        self.root = tk.Tk()
        self.root.title("Board")
        self.labels = [[None for _ in range(4)] for _ in range(4)]
        self.canvas = tk.Canvas(self.root, width=400, height=400)
        self.canvas.grid(row=0, column=0, columnspan=4, rowspan=4)

    def askUserForBoard(self):
        userInput = input("Enter the board: ").lower()

        if len(userInput) != 16:
            print("Invalid board. Please enter 16 letters.")
            raise ValueError("Invalid board.")
            # return self.askUserForBoard()

        self.board = [userInput[i : i + 4] for i in range(0, len(userInput), 4)]
        self.displayBoard()

    def loadBoardString(self, boardString):
        boardString = boardString.lower()
        self.board = [boardString[i : i + 4] for i in range(0, len(boardString), 4)]
        self.displayBoard()

    def getAvailableMovesFrom(self, x, y, path):
        moves = []

        MOVEMENTS = [
            (0, 1),
            (1, 0),
            (0, -1),
            (1, 1),
            (1, -1),
            (-1, 0),
            (-1, 1),
            (-1, -1),
        ]

        for oy, ox in MOVEMENTS:
            if ox == 0 and oy == 0:
                continue

            nx = x + ox
            ny = y + oy

            if nx < 0 or nx > 3 or ny < 0 or ny > 3:
                continue

            moves.append((nx, ny))

        return [(x, y) for x, y in moves if (x, y) not in path]

    def getLetterAt(self, x, y):
        return self.board[y][x]

    def getLettersFrom(self, moves):
        return [self.getLetterAt(x, y) for x, y in moves]

    def printBoard(self):
        print("\n".join(self.board))

    def displayBoard(self):
        for y in range(4):
            for x in range(4):
                label = tk.Label(
                    self.root,
                    text=self.board[y][x].upper(),
                    font=("Helvetica", 32),
                    width=2,
                    height=1,
                    borderwidth=2,
                    relief="solid",
                )
                label.grid(row=y, column=x)
                self.labels[y][x] = label

    def drawPath(self, path):
        self.labels[path[0][1]][path[0][0]].config(bg="green")
        for i in range(1, len(path)):
            x1, y1 = path[i - 1]
            x2, y2 = path[i]

            self.labels[y2][x2].config(bg="yellow")

            self.canvas.create_line(
                x1 * 100 + 50,
                y1 * 100 + 50,
                x2 * 100 + 50,
                y2 * 100 + 50,
                fill="red",
                width=5,
            )

    def undrawAll(self):
        for y in range(4):
            for x in range(4):
                self.labels[y][x].config(bg="white")

        self.canvas.delete("all")

    def drawAllPaths(self, paths, index=0):
        if index >= len(paths):
            return

        self.undrawAll()
        self.drawPath(paths[index])

        self.root.after(
            100 + 350 * len(paths[index]), self.drawAllPaths, paths, index + 1
        )

    def start(self):
        self.root.mainloop()


# Example usage:
# board = Board()
# board.loadBoardString("ABCDEFGHIJKLMNOP")
# paths = [[(0, 0), (1, 1), (2, 2), (3, 3)], [(0, 0), (1, 0), (2, 0), (3, 0)]]
# board.drawAllPaths(paths)
# board.start()

# To draw a path, you can call:
# board.drawPath([(0, 0), (1, 1), (2, 2), (3, 3)])
