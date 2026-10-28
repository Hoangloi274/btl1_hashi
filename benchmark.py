"""Benchmark runner for comparing solver performance."""

from __future__ import annotations

import time
import tracemalloc
from dataclasses import dataclass
from typing import Any, Dict, List

from checker import ConstraintChecker
from grid import Grid
from solvers.astar import AStarSolver
from solvers.dfs import DFSSolver
from state import PuzzleState
from solvers.astar import Heuristic

@dataclass
class BenchmarkResult:
    algorithm: str
    status: str
    time_seconds: float
    memory_peak_mb: float
    metrics: Dict[str, Any]
    solution: PuzzleState | None


class BenchmarkRunner:
    def __init__(self, grid: Grid):
        self.grid = grid
        self.checker = ConstraintChecker(grid)

    def run_all(self) -> List[BenchmarkResult]:
        results = []
        
        # Run A* variants
        results.append(self.run_astar_variant("A* (Composite)", Heuristic.composite))
        results.append(self.run_astar_variant("A* (Deficit)", Heuristic.deficit))
        results.append(self.run_astar_variant("A* (MinConn)", Heuristic.min_conn))
        results.append(self.run_astar_variant("A* (Bottleneck)", Heuristic.bottleneck_corrected))

        results.append(self.run_dfs("DFS"))

        return results

    def _run_with_profiling(self, name: str, func) -> BenchmarkResult:
        tracemalloc.start()
        start_time = time.perf_counter()
        try:
            result_obj = func()
            elapsed = time.perf_counter() - start_time
            _, peak = tracemalloc.get_traced_memory()
            tracemalloc.stop()
            
            peak_mb = peak / (1024 * 1024)
            
            # Extract common fields from result object (assuming they all have status, etc.)
            # But the solvers return different result objects.
            # We need to adapt based on the solver return type.
            
            # Actually, the original code called specific methods that returned BenchmarkResult.
            # I should refactor those methods to use this helper or just add profiling inside them.
            # Adding inside them is safer to avoid changing too much logic at once.
            pass
        except Exception:
            tracemalloc.stop()
            raise

    def run_astar_variant(self, name: str, heuristic_func) -> BenchmarkResult:
        if self.grid.rows > 13:
                     return BenchmarkResult(
                        algorithm=name,
                        status="SKIPPED",
                        time_seconds=0.0,
                        memory_peak_mb=0.0,
                        metrics={"reason": " N > 13"},
                        solution=None,
                    )
        solver = AStarSolver(self.checker, heuristic=heuristic_func)
        initial_state = PuzzleState(self.grid)
        tracemalloc.start()
        try:
            result = solver.solve(initial_state)
            _, peak = tracemalloc.get_traced_memory()
            tracemalloc.stop()

            return BenchmarkResult(
                algorithm=name,
                status=result.status,
                time_seconds=result.elapsed,
                memory_peak_mb=peak / (1024 * 1024),
                metrics={"expanded_nodes": result.expanded},
                solution=result.state,
            )
        except Exception as e:
            tracemalloc.stop()
            return BenchmarkResult(name, "ERROR", 0.0, 0.0, {"error": str(e)}, None)


    def run_dfs(self, name: str = "DFS") -> BenchmarkResult:
        if self.grid.rows > 7:
             return BenchmarkResult(
                algorithm=name,
                status="SKIPPED",
                time_seconds=0.0,
                memory_peak_mb=0.0,
                metrics={"reason": " N > 7"},
                solution=None,
            )
        solver = DFSSolver(self.grid, self.checker)
        tracemalloc.start()
        try:
            result = solver.solve()
            _, peak = tracemalloc.get_traced_memory()
            tracemalloc.stop()

            return BenchmarkResult(
                algorithm=name,
                status=result.status,
                time_seconds=result.elapsed,
                memory_peak_mb=peak / (1024 * 1024),
                metrics={"visited_states": result.visited},
                solution=result.state,
            )
        except Exception as e:
            tracemalloc.stop()
            return BenchmarkResult("DFS", "ERROR", 0.0, 0.0, {"error": str(e)}, None)

    