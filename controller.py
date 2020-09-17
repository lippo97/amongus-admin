from fsm import FSM
from vision import Vision
import numpy as np
import time

class Controller:
    def __init__(self, fsm: FSM, vision: Vision, period = 1):
        self.fsm = fsm
        self.vision = vision
        self.period = period

    def _find_template(self, name):
        matches = self.vision.find_template(name)
        return np.shape(matches)[1] >= 1

    def _is_vote_phase(self):
        def is_vote_phase_title1():
            return self._find_template('vote-title1')

        def is_vote_phase_title2():
            return self._find_template('vote-title2')

        def is_vote_phase_arrow():
            return self._find_template('vote-arrow')

        return is_vote_phase_title1() or is_vote_phase_title2() or is_vote_phase_arrow()

    def _is_playing_phase(self):
        return not self._is_vote_phase()

    def step(self):
        self.vision.refresh_frame()
        if self._is_vote_phase():
            self.fsm.step('voting')
        elif self._is_playing_phase():
            self.fsm.step('playing')
        else:
            raise Exception('Illegal State')
