from fsm import FSM
from vision import Vision
import numpy as np
import time

class Controller:
    def __init__(self, fsm: FSM, vision: Vision, period = 1):
        self.fsm = fsm
        self.vision = vision
        self.period = period

    def _find_template(self, state, name):
        matches = self.vision.find_template(state, name)
        return np.shape(matches)[1] >= 1

    def _is_vote_phase(self):

        def vote_title1():
            return self._find_template('voting', 'vote-title1')

        def vote_title2():
            return self._find_template('voting', 'vote-title2')

        def vote_title_dead1():
            return self._find_template('voting', 'vote-title-dead1')

        def vote_title_dead2():
            return self._find_template('voting', 'vote-title-dead2')

        # def play_again():
        #     return self._find_template('post_game', 'play-again')

        def win_title():
            return self._find_template('post_game', 'win-title')

        def lose_title():
            return self._find_template('post_game', 'lose-title')

        def public_label():
            return self._find_template('post_game', 'public-label')

        def private_label():
            return self._find_template('post_game', 'private-label')

        return vote_title1() or vote_title2() or vote_title_dead1() or vote_title_dead2() or win_title() or lose_title() or private_label() or public_label()
        # return chat_arrow() or chat_arrow_open() or chat_arrow_message() or play_again()


    def _is_playing_phase(self):
        return not self._is_vote_phase()

    def step(self):
        self.vision.refresh_frame()
        if self._is_vote_phase():
            self.fsm.step('voting')
        else:
            self.fsm.step('playing')
        # TODO: Temporary workaround because we have just two states currently.
        #
        # elif self._is_playing_phase():
        #     self.fsm.step('playing')
        # else:
        #     raise Exception('Illegal State')
