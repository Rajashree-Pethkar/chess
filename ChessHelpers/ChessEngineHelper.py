"""
Contains some utility methods that act as extensions to the chess library
"""

import chess
import random
import pygame # need to process pygame events to prevent game freeze
from ChessHelpers.ChessHeuristics import Heuristics
# import timeit  # using to time some moves


class MoveGenerator:
def init(self):
self.CHECKMATE = 1000
self.STALEMATE = 0
self.DEPTH = 4
self.QUIT = False
self.heuristics = Heuristics()
def random_move(self, board):
    return random.choice(list(board.legal_moves))

def evaluate_move(self, board, move, white):
    turn_multiplier = 1 if board.turn == chess.WHITE else -1
    board.push(move)
    if board.is_checkmate():
        score = self.CHECKMATE
    elif board.is_stalemate():
        score = self.STALEMATE
    else:
        score = turn_multiplier * self.heuristics.heuristic_1(board, white)
    board.pop()
    return score

def greedy_best_next_move(self, board):
    white = board.turn == chess.WHITE
    legal_moves = list(board.legal_moves)
    max_score = -self.CHECKMATE
    best_move = None

    for player_move in legal_moves:
        score = self.evaluate_move(board, player_move, white)
        if score > max_score:
        max_score = score
        best_move = player_move
            return best_move if best_move is not None else self.random_move(board)

def mobility_best_next_move(self, board):
    legal_moves = list(board.legal_moves)
    turn_multiplier = 1 if board.turn == chess.WHITE else -1
    max_score = -self.CHECKMATE
    best_move = None

    for player_move in legal_moves:
        board.push(player_move)
        if board.is_checkmate():
            score = self.CHECKMATE
        elif board.is_stalemate():
            score = self.STALEMATE
        else:
            score = turn_multiplier * self.heuristics.mobility(board)
        if score > max_score:
            max_score = score
            best_move = player_move
        board.pop()

    return best_move if best_move is not None else self.random_move(board)

def mobility_advanced_best_next_move(self, board):
    legal_moves = list(board.legal_moves)
    max_score = -self.CHECKMATE
    best_move = None

    for player_move in legal_moves:
        board.push(player_move)
        if board.is_checkmate():
            score = self.CHECKMATE
        elif board.is_stalemate():
            score = self.STALEMATE
        else:
            score = self.heuristics.mobility_advanced(board, player_move)
        if score > max_score:
            max_score = score
            best_move = player_move
        board.pop()
            return best_move if best_move is not None else self.random_move(board)

def mini_max_easy(self, board):
    legal_moves = list(board.legal_moves)
    turn_multiplier = 1 if board.turn == chess.WHITE else -1
    opponent_min_max_score = self.CHECKMATE
    best_move = None

    for player_move in legal_moves:
        board.push(player_move)
        opponent_moves = list(board.legal_moves)
        opponent_max_score = -self.CHECKMATE

        for opponent_move in opponent_moves:
            board.push(opponent_move)
            score = self.evaluate_move(board, opponent_move, not board.turn == chess.WHITE)
            if score > opponent_max_score:
                opponent_max_score = score
            board.pop()

        if opponent_max_score < opponent_min_max_score:
            opponent_min_max_score = opponent_max_score
            best_move = player_move
            board.pop()
                return best_move if best_move is not None else self.random_move(board)

def mini_max_move(self, board):
    best_move = [None]
    maximize = True
    white = board.turn == chess.WHITE
    self.find_mini_max_move(board, self.DEPTH, maximize, white, -10000, 10000, best_move)

    if self.QUIT is True:
        return False

    if best_move[0] is None:
        print("Warning: no best move found.")
        best_move[0] = self.random_move(board)
    return best_move[0]

def find_mini_max_move(self, board, depth, maximize, white, alpha, beta, best_move):
    try:
        events = pygame.event.get()
        for e in events:
            if e.type == pygame.QUIT:
        self.QUIT = True
        if self.QUIT is True:
        return 0
        except Exception:
        pass     unsorted_legal_moves = list(board.legal_moves)
    legal_moves = sorted(unsorted_legal_moves, key=lambda m: board.piece_at(m.to_square) is not None, reverse=True)

    if depth == 0 or len(legal_moves) == 0:
        score = self.heuristics.heuristic_2(board, white)
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

