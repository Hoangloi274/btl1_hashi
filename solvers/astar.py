"""A* Search and heuristic functions."""


def a_star_search(problem, heuristic=None):
    """Find a minimum-cost solution using A*.

    Expected interface: ``initial_state``, ``is_goal(state)``, and
    ``successors(state)`` yielding ``(action, next_state, step_cost)``.
    The result is ``(path, nodes_expanded)``; ``path`` is ``None`` when no
    solution exists.
    """
    raise NotImplementedError


def heuristic(state, problem) -> float:
    """Estimate the remaining cost to a goal state."""
    raise NotImplementedError