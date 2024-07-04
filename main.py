import os
import random
import itertools

from terminaltables import SingleTable
from termcolor import colored


class Bot:

    def __init__(self, game, goes_first):
        self.game = game
        self.symbol = 'X' if goes_first else 'O'

    def move(self):
        raise NotImplementedError


class RandomBot(Bot):

    def __init__(self, game, goes_first):
        super().__init__(game, goes_first)

    def move(self):
        empty_boxes = Game.get_empty_box_positions(self.game.board)
        return Game.get_box_number(*random.choice(empty_boxes))


class MinimaxBot(Bot):

    def __init__(self, game, goes_first):
        super().__init__(game, goes_first)

    def move(self):
        board = [row[:] for row in self.game.board]

        scores = {}
        empty_boxes = Game.get_empty_box_positions(self.game.board)

        for i, j in empty_boxes:
            box = Game.get_box_number(i, j)
            board[i][j] = self.symbol
            scores[box] = self._minimax(board, 'X' if self.symbol == 'O' else 'O')
            board[i][j] = str(box)

        box = None
        max_score = -float('inf')
        for key, value in scores.items():
            if value > max_score:
                box = key
                max_score = value

        return box

    def _evaluate(self, board):
        for i in range(3):
            if board[i][0] == board[i][1] == board[i][2]:
                return 10 if board[i][0] == self.symbol else -10
            elif board[0][i] == board[1][i] == board[2][i]:
                return 10 if board[0][i] == self.symbol else -10

        if board[0][0] == board[1][1] == board[2][2]:
            return 10 if board[0][0] == self.symbol else -10

        if board[0][2] == board[1][1] == board[2][0]:
            return 10 if board[0][2] == self.symbol else -10

        return 0 if all(cell in ['X', 'O'] for row in board for cell in row) else None

    def _minimax(self, board, symbol):
        score = self._evaluate(board)
        if score is not None:
            return score

        scores = []
        empty_boxes = Game.get_empty_box_positions(board)

        for i, j in empty_boxes:
            box = Game.get_box_number(i, j)
            board[i][j] = symbol
            scores.append(self._minimax(board, 'X' if symbol == 'O' else 'O'))
            board[i][j] = str(box)

        return max(scores) if symbol == self.symbol else min(scores)


class Game:

    def __init__(self):
        self.board = [[f'{Game.get_box_number(i, j)}' for j in range(3)] for i in range(3)]
        self.turn = 0
        
    @staticmethod
    def get_box_number(row, col):
        return row * 3 + col + 1

    @staticmethod
    def get_empty_box_positions(board):
        return [
            (i, j)
            for i in range(3)
            for j in range(3)
            if board[i][j] not in ['X', 'O']
        ]

    def move(self, box):
        if box < 1 or box > 9:
            raise ValueError("Box must be between 1 and 9")

        row, col = (box - 1) // 3, (box - 1) % 3
        if self.board[row][col] in ['X', 'O']:
            raise ValueError("Box is already filled")

        self.board[row][col] = 'X' if self.turn % 2 == 0 else 'O'
        self.turn += 1

        winner = self.get_winner()

        if winner is not None:
            return winner
        elif self.turn == 9:
            return 'Tie'
        else:
            return None

    def get_winner(self):
        for i in range(3):
            if self.board[i][0] == self.board[i][1] == self.board[i][2]:
                return self.board[i][0]
            elif self.board[0][i] == self.board[1][i] == self.board[2][i]:
                return self.board[0][i]

        if self.board[0][0] == self.board[1][1] == self.board[2][2]:
            return self.board[0][0]

        elif self.board[0][2] == self.board[1][1] == self.board[2][0]:
            return self.board[0][2]

        else:
            return None

    def display_board(self):
        colored_board = [row[:] for row in self.board]

        for i, j in itertools.product(range(3), range(3)):
            if self.board[i][j] == 'X':
                colored_board[i][j] = colored('X', 'blue')
            elif self.board[i][j] == 'O':
                colored_board[i][j] = colored('O', 'red')
            else:
                colored_board[i][j] = colored(self.board[i][j], 'dark_grey')

        table = SingleTable(colored_board)
        table.inner_row_border = True

        os.system('cls' if os.name == 'nt' else 'clear')
        print("\n")
        print(table.table)


def game_loop(game: Game, human_goes_first: bool):
    human_first_mod = 0 if human_goes_first else 1

    bot_type = input("Should the bot be smart? (y/n): ")
    if bot_type.lower().startswith('y'):
        bot = MinimaxBot(game, not human_goes_first)
    else:
        bot = RandomBot(game, not human_goes_first)

    while True:
        game.display_board()

        if game.turn % 2 == human_first_mod:
            player = 'You'
            try:
                box = int(input("Box: ".rjust(12)))
            except ValueError as e:
                print(f"[Invalid input]{str(e)}")
                continue
        else:
            player = 'Bot'
            box = bot.move()

        winner = game.move(box)
        if winner is not None:
            game.display_board()
            if winner == 'Tie':
                print(" Tied! ".center(13, '='))
            else:
                print(f" {player} Won ".center(13, '*'))
            break


def main():
    print(" Tic-Tac-Toe ".center(32, '='))

    wanna_play = True
    while wanna_play:
        answer = input("Would you like to go first? (y/n): ")
        human_goes_first = answer.lower().startswith('y')

        game_loop(Game(), human_goes_first)

        answer = input("Would you like to play again? (y/n): ")
        wanna_play = answer.lower().startswith('y')


if __name__ == '__main__':
    main()
