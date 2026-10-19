"""Environment model for the Pipes puzzle."""


class PipesEnvironment:
    """Represent a Pipes puzzle loaded from a JSON-compatible dictionary.

    The puzzle uses a rectangular ``grid`` of pipe pieces. Define the state
    representation and transition rules here before implementing the solvers.
    """

    def __init__(self, puzzle: dict) -> None:
        self.puzzle = puzzle
        self.initial_state = puzzle["grid"]

    def is_goal(self, state) -> bool:
        """Return whether ``state`` satisfies the Pipes puzzle goal."""
        raise NotImplementedError

    def successors(self, state):
        """Yield (action, next_state, step_cost) transitions from ``state``."""
        raise NotImplementedError