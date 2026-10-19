"""Environment model for the Hashi (Bridges) puzzle."""


class HashiEnvironment:
    """Represent a Hashi puzzle loaded from a JSON-compatible dictionary.

    The puzzle uses an ``islands`` list containing coordinates and required
    bridge counts. Define the state representation and transition rules here.
    """

    def __init__(self, puzzle: dict) -> None:
        self.puzzle = puzzle
        self.islands = puzzle["islands"]
        self.initial_state = puzzle["islands"]

    def is_goal(self, state) -> bool:
        """Return whether ``state`` satisfies the Hashi puzzle goal."""
        raise NotImplementedError

    def successors(self, state):
        """Yield (action, next_state, step_cost) transitions from ``state``."""
        raise NotImplementedError