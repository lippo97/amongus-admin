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
        def chat_arrow_message():
            return self._find_template('voting', 'chat-arrow-message')

        def chat_arrow_open():
            return self._find_template('voting', 'chat-arrow-open')

        def chat_arrow():
            return self._find_template('voting', 'chat-arrow')

        return chat_arrow() or chat_arrow_open() or chat_arrow_message()


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
