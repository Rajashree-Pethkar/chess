"""
Contains some utility methods that act as extensions to the chess library
"""

import chess
import random
import pygame  # need to process pygame events to prevent game freeze
from ChessHelpers.ChessHeuristics import Heuristics
# import timeit  # using to time some moves


class MoveGenerator:
    def __init__(self):
        self.CHECKMATE = 1000
        self.STALEMATE = 0
        # depth:
        #   in case it's counter-intuitive: these are individual moves, not pairs
        self.DEPTH = 4  # for now, 4-5 seems like a good trade-off between looking ahead and taking forever
        self.QUIT = False
        self.heuristics = Heuristics()

    '''
    Returns a random move from the list of all possible legal moves
    '''

    def random_move(self, board):
        moves = list(board.legal_moves)
        return random.choice(moves)

    '''
    Evaluate all moves from the list of all possible next, legal moves and decide which maximizes your score the most.
    We make the move in order to evaluate it and later undo it.
    '''

    def greedy_best_next_move(self, board):
        white = board.turn == chess.WHITE
        legal_moves = list(board.legal_moves)
        turn_multiplier = 1 if board.turn == chess.WHITE else -1
        max_score = -self.CHECKMATE
        best_move = None

        for player_move in legal_moves:
            board.push(player_move)  # make move
            if board.is_checkmate():
                score = self.CHECKMATE
            elif board.is_stalemate():
                score = self.STALEMATE
            else:
                score = turn_multiplier * self.heuristics.checkmate_stalemate_heuristic(board, white)
            if score > max_score:
                max_score = score
                best_move = player_move
            board.pop()  # undo the move

        if best_move is None:
            return self.random_move(board)

        return best_move

    '''
        Evaluate all moves from the list of all possible next, legal moves and decide which maximizes your score 
        based on the total number of legal moves available at the next turn.
        We make the move in order to evaluate it and later undo it.
    '''

    def mobility_best_next_move(self, board):
        legal_moves = list(board.legal_moves)
        turn_multiplier = 1 if board.turn == chess.WHITE else -1
        max_score = -self.CHECKMATE
        best_move = None

        for player_move in legal_moves:
            board.push(player_move)  # make move
            if board.is_checkmate():
                score = self.CHECKMATE
            elif board.is_stalemate():
                score = self.STALEMATE
            else:
                score = turn_multiplier * self.heuristics.mobility(board)
            if score > max_score:
                max_score = score
                best_move = player_move
            board.pop()  # undo the move

        if best_move is None:
            return self.random_move(board)

        return best_move

    def mobility_advanced_best_next_move(self, board):
        legal_moves = list(board.legal_moves)
        max_score = -self.CHECKMATE
        best_move = None

        for player_move in legal_moves:
            board.push(player_move)  # make move
            if board.is_checkmate():
                score = self.CHECKMATE
            elif board.is_stalemate():
                score = self.STALEMATE
            else:
                score = self.heuristics.mobility_advanced(board, player_move)
            if score > max_score:
                max_score = score
                best_move = player_move
            board.pop()  # undo the move

        if best_move is None:
            return self.random_move(board)

        return best_move

    '''
    To maximize your score and make the best move, you need to look into the opponent's future best move
    Only looks at the next opponent move
    '''

    def mini_max_easy(self, board):
        legal_moves = list(board.legal_moves)
        turn_multiplier = 1 if board.turn == chess.WHITE else -1
        opponent_min_max_score = self.CHECKMATE
        best_move = None
        for player_move in legal_moves:
            board.push(player_move)  # make move
            opponent_moves = list(board.legal_moves)
            opponent_max_score = self.CHECKMATE
            if board.is_checkmate():
                opponent_max_score = -self.CHECKMATE
            elif board.is_stalemate():
                opponent_max_score = self.STALEMATE
            else:
                opponent_max_score = -self.CHECKMATE
                for opponent_move in opponent_moves:
                    board.push(opponent_move)  # make opponent's move
                    if board.is_checkmate():
                        score = self.CHECKMATE
                    elif board.is_stalemate():
                        score = self.STALEMATE
                    else:
                        score = -turn_multiplier * self.heuristics.checkmate_stalemate_heuristic(board)
                    if score > opponent_max_score:
                        opponent_max_score = score
                    board.pop()  # undo the opponent's move
            if opponent_max_score < opponent_min_max_score:
                opponent_min_max_score = opponent_max_score
                best_move = player_move
            board.pop()  # undo the player's move

        if best_move is None:
            return self.random_move(board)

        return best_move

    '''
    Mini Max Recursive Algo
    '''

    def mini_max_move(self, board):
        # uncomment start/stop and import to time moves
        # start = timeit.default_timer()

        best_move = [None]
        # changed 'white_to_move' to 'maximize'
        # it doesn't matter whose turn it is, as long as
        # we get the max of whichever colors turn it is
        #
        #   (made for some funny games when I was playing white,
        #    before I realized that the AI was trying to maximize
        #    my score instead of its own)
        maximize = True
        # need to know if white or black is playing for max/min
        white = board.turn == chess.WHITE

        # alpha-beta pruning
        # (https://en.wikipedia.org/wiki/Alpha%E2%80%93beta_pruning#Pseudocode)
        # Initialize array to hold hold dummy highest and lowest values for pruning
        #
        # alpha = "minimum score that the maximizing player is assured of"
        # beta = "maximum score that the minimizing player is assured of"

        self.find_mini_max_move(board, self.DEPTH, maximize, white, -10000, 10000, best_move)
        if self.QUIT is True:
            return False

        if best_move[0] is None:
            print("Warning: no best move found.")
            best_move[0] = self.random_move(board)

        # stop = timeit.default_timer()
        # print('Time: ', stop - start)
        return best_move[0]

    def find_mini_max_move(self, board, depth, maximize, white, alpha, beta, best_move):
        # keep processing events while the mini max search is going
        # and allow the user to close the game if a move is in progress
        try:
            events = pygame.event.get()
            for e in events:
                if e.type == pygame.QUIT:
                    self.QUIT = True
            if self.QUIT is True:
                return 0
        except Exception:
            # (if game is being run in terminal, there is no pygame)
            pass


        # I also read that you can increase the efficiency of the pruning by ordering the moves
        #
        # here I make a new list of legal moves where moves that capture pieces are ordered first
        unsorted_legal_moves = list(board.legal_moves)
        legal_moves = []
        # list the moves that capture a piece first
        for m in unsorted_legal_moves:
            if board.piece_at(m.to_square):
                legal_moves.append(m)
        for m in unsorted_legal_moves:
            if not board.piece_at(m.to_square):
                legal_moves.append(m)

        if depth == 0 or len(legal_moves) == 0:  # check for 'terminal node' as well as max depth
            score = self.heuristics.diagonal_center_control_heuristic(board, white)
            return score

        if maximize:
            max_score = -10000
            for move in legal_moves:
                board.push(move)
                score = self.find_mini_max_move(board, depth - 1, False, white, alpha, beta, best_move)

                if score > max_score:
                    max_score = score

                    # set the best move (I put it in an argument instead of a global var)
                    if depth == self.DEPTH:
                        best_move[0] = move

                # pruning
                # update "minimum guaranteed score"
                if max_score > alpha:
                    alpha = max_score

                # pruning
                # skip if move is better than best move opponent will allow
                if max_score >= beta:
                    board.pop()
                    break

                board.pop()
            return max_score

        else:
            min_score = 10000
            for move in legal_moves:
                board.push(move)
                score = self.find_mini_max_move(board, depth - 1, True, white, alpha, beta, best_move)

                if score < min_score:
                    min_score = score
                    # hehe your best move can't be one of your opponent's moves
                    # if depth == self.DEPTH:
                    #    best_move[0] = move

                # pruning: update beta value
                if min_score < beta:
                    beta = min_score

                # pruning
                # skip if worse than the worst score we can be forced to accept
                if min_score <= alpha:
                    board.pop()
                    break

                board.pop()
            return min_score

