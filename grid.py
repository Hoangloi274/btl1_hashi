from dataclasses import dataclass
from typing import Dict, Iterable, List, Sequence, Tuple
from enum import Enum

class Direction(str, Enum):
    HORIZONTAL="H"
    VERTICAL="V"

@dataclass(frozen=True)
class Island:
    identifier: int
    row: int
    col: int
    target: int
    #identifier đc lưu theo cơ chế của hàm build_islands(từ trên xuống, trái phải)

@dataclass(frozen=True)
class Bridge:
    identifier: int     #được lưu theo cơ chế của hàm build_corridors
    island_a: int
    island_b: int
    direction: Direction
    cells: Tuple[Tuple[int, int], ...] #lưu các ô trên hành lang
    #-> để kiểm tra hành lang có bị cắt bởi hành lang trước đó không
    #-> vẽ cầu trên các ô này sau khi đã có đáp án
    def endpoints(self) -> Tuple[int, int]:
        return (self.island_a, self.island_b)


class Grid:
    def __init__(self, matrix: Sequence[Sequence[int]]):
        self._matrix = tuple(tuple(row) for row in matrix)
        self.rows = len(self._matrix)
        self.cols = len(self._matrix[0]) if self.rows > 0 else 0
        self.islands: Dict[int, Island] = {}
        self.corridors: Dict[int, Bridge] = {}
        self.island_lookup: Dict[Tuple[int, int], int]={}      #tra cứu ngược từ tọa độ ra ID
        self.build_islands()
        self.build_corridors()


    def build_islands(self) -> None:
        identifier = 0
        for r, row in enumerate(self._matrix):
            for c, value in enumerate(row):
                if value>0:
                    island = Island(identifier, r, c, value)
                    self.islands[identifier] = island
                    self.island_lookup[(r, c)] = identifier
                    identifier += 1

    def build_corridors(self) -> None:
        corridors_id = 0
        for island in self.islands.values():
            #chỉ scan sang phải và xuống dưới
            r, c = island.row+1, island.col+1
            cells: List[Tuple[int, int]] = []
            while 0 <= c < self.cols:
                pos=(island.row, c)
                if pos in self.island_lookup:
                    self.corridors[corridors_id] = Bridge(
                        corridors_id,
                        island.identifier,
                        self.island_lookup[pos],
                        Direction.HORIZONTAL,
                        tuple(cells),
                    )
                    corridors_id += 1
                    break
                if self._matrix[island.row][c] > 0:
                    break
                cells.append(pos)
                c+=1
            #scan xuống
            cells=[]
            while 0 <= r < self.rows:
                pos=(r, island.col)
                if pos in self.island_lookup:
                    self.corridors[corridors_id] = Bridge(
                        corridors_id,
                        island.identifier,
                        self.island_lookup[pos],
                        Direction.VERTICAL,
                        tuple(cells),
                    )
                    corridors_id += 1
                    break
                if self._matrix[r][island.col] > 0:
                    break
                cells.append(pos)
                r+=1

    def matrix(self) -> Tuple[Tuple[int, ...], ...]:
        return self._matrix

    def neighbors(self, island_id: int) -> Iterable[int]:
        for corridor in self.corridors.values():
            if corridor.island_a == island_id:
                yield corridor.island_b
            elif corridor.island_b == island_id:
                yield corridor.island_a

    def corridors_incident_to(self, island_id: int) -> List[Bridge]:
        return [
            c
            for c in self.corridors.values()
            if c.island_a == island_id or c.island_b == island_id
        ]

    def corridor_between(self, island_a: int, island_b: int) -> Bridge | None:
        for corridor in self.corridors.values():
            if {corridor.island_a, corridor.island_b} == {island_a, island_b}:
                return corridor
        return None

    def cell_contains_island(self, row: int, col: int) -> bool:
        return (row, col) in self.island_lookup

    def cell_index(self, row: int, col: int) -> int | None:
        return self.island_lookup.get((row, col))

    def cells(self) -> Iterable[Tuple[int, int]]:
        for r in range(self.rows):
            for c in range(self.cols):
                yield r, c