import asyncio
from copy import copy
import logging

PLAYING_TIMEOUT = 3
VOTING_TIMEOUT = 5

class AbstractState():
    def __init__(self, name):
        self.name = name

    def voting(self):
        pass

    def playing(self):
        pass

class PlayingState(AbstractState):
    def __init__(self, current = 0, on_change_state = {}, timeout = PLAYING_TIMEOUT):
        super().__init__('playing state')
        self.timeout = timeout
        self.on_change_state = on_change_state
        self.current = 0

    def voting(self):
        if self.current < self.timeout:
            modified = copy(self)
            modified.current += 1
            return modified
        else:
            self.on_change_state.get('voting', lambda: None)()
            return VotingState(on_change_state=self.on_change_state)

    def playing(self):
        return self

class VotingState(AbstractState):
    def __init__(self, current = 0, on_change_state = {}, timeout = VOTING_TIMEOUT):
        super().__init__('voting state')
        self.timeout = timeout
        self.current = 0
        self.on_change_state = on_change_state

    def voting(self):
        return self

    def playing(self):
        if self.current < self.timeout:
            modified = copy(self)
            modified.current += 1
            return modified
        else:
            self.on_change_state.get('playing', lambda: None)()
            return PlayingState(on_change_state=self.on_change_state)

class FSM:

    def __init__(self, initialState: AbstractState = VotingState(), on_change_state = {}):
        self._state = initialState
        self._state.on_change_state = on_change_state

    def step(self, transition: str):
        logging.debug('Transition received: {}'.format(transition))
        if transition == 'voting':
            self._state = self._state.voting()
        elif transition == 'playing':
            self._state = self._state.playing()
        else:
            raise Exception('Illegal state')
        logging.info('Current state: {}'.format(self._state.name))
