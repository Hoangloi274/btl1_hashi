"""Depth-First Search."""

from __future__ import annotations
from dataclasses import dataclass
from time import perf_counter
from typing import List
from checker import ConstraintChecker
from grid import Grid
from state import PuzzleState

@dataclass
class DFSResult:
    state: PuzzleState | None
    elapsed: float
    visited: int
    status: str

class DFSSolver:
    def __init__(self, grid: Grid, checker: ConstraintChecker) -> None:
        self.grid = grid
        self.checker = checker
        self.visited = 0

    def solve(self) -> DFSResult:
        start = perf_counter()
        # Sắp xếp các hành lang theo chiến lược MRV (ưu tiên các đảo ít lựa chọn trước)
        order = self._sort_corridors_by_mrv()
        self.visited = 0

        initial_state = PuzzleState(self.grid)
        solution = self._dfs(0, initial_state, order)

        elapsed = perf_counter() - start
        status = "SOLVED" if solution else "FAILED"
        
        return DFSResult(state=solution, elapsed=elapsed, visited=self.visited, status=status)

    def _dfs(self, index: int, state: PuzzleState, order: List[int]) -> PuzzleState | None:
        # Điều kiện dừng: Đã duyệt qua tất cả các hành lang
        if index == len(order):
            if state.islands_satisfied() and state.is_connected():
                return state.copy()
            return None

        corridor_id = order[index]

        # Thử lần lượt các số lượng cầu: 0, 1, 2
        for value in (0, 1, 2):
            state.set_corridor_value(corridor_id, value)
            self.visited += 1

            # Cắt tỉa nhánh sớm (Pruning): Nếu cấu hình hiện tại vi phạm luật, bỏ qua ngay
            if not self.checker.is_valid_assignment(state):
                continue

            # Đệ quy đi sâu vào hành lang tiếp theo
            solution = self._dfs(index + 1, state, order)
            if solution:
                return solution

        # Quay lui (Backtracking): Hoàn trả trạng thái về 0 nếu các nhánh con không thành công
        state.set_corridor_value(corridor_id, 0)
        return None

    def _sort_corridors_by_mrv(self) -> List[int]:
        """Sắp xếp hành lang dựa trên Minimum Remaining Value (đảo có target nhỏ hơn lên trước)"""
        def corridor_priority(corridor_id: int) -> tuple:
            corridor = self.grid.corridors[corridor_id]
            island_a = self.grid.islands[corridor.island_a]
            island_b = self.grid.islands[corridor.island_b]
            min_target = min(island_a.target, island_b.target)
            sum_target = island_a.target + island_b.target
            return (min_target, sum_target)
            
        return sorted(self.grid.corridors.keys(), key=corridor_priority)