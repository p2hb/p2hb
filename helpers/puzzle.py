import random
from enum import Enum

import discord

from .helper import scramble, hintify

class PuzzleType(Enum):
    Scramble, HardScramble, Hint, Description = range(1,5)

class Puzzle:
    def __init__(self, bot, types: tuple[PuzzleType]):
        self.bot = bot
        self.types = types

        self.question = discord.Embed()
        self.answers = []
        self.primary_answer = ""

    def generate_question(self):
        species = self.bot.data.random_spawn()
        question_type = random.choice(self.types)
        if question_type == PuzzleType.Scramble:
            question.set_description = scramble(species.name)
        elif question_type == PuzzleType.HardScramble:
            question.set_description = scramble(species.name.lower())
        elif question_type == PuzzleType.Hint:
            question.set_description = hintify(species.name)
        elif question_type == PuzzleType.Description:
            question.set_description = scramble(species.description)
        answers = species.correct_guesses

    def check_answer(self, response):
        return response in answers