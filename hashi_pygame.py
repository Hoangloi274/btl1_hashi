"""
Hashiwokakero - Pygame interactive version

Cách chơi:
  - Click vào HÀNH LANG để đặt / tăng / xóa cầu
  - Không khóa đảo khi đã đủ cầu — vẫn sửa được
  - Phím R: màn mới | Phím S: xem đáp án | Esc: menu

Chạy: python hashi_pygame.py

& D:\python_envs\btl1_ai\Scripts\Activate.ps1
"""

import sys
import time
import math
from pathlib import Path

import pygame

CURRENT_DIR = Path(__file__).parent
sys.path.insert(0, str(CURRENT_DIR))

from grid import Grid
from state import PuzzleState
from checker import ConstraintChecker
from test_generator import TestGenerator, GenerationError
from solvers.astar import AStarSolver, Heuristic


# ====================== CONFIG ======================
WINDOW_W, WINDOW_H = 1000, 750
FPS = 60

BG = (245, 247, 250)
GRID_BG = (255, 255, 255)
ISLAND_COLOR = (41, 128, 185)
ISLAND_DONE = (39, 174, 96)
BRIDGE_COLOR = (192, 57, 43)
BRIDGE_HOVER = (241, 148, 138)
TEXT_WHITE = (255, 255, 255)
TEXT_DARK = (44, 62, 80)
BUTTON_BG = (52, 152, 219)
BUTTON_HOVER = (41, 128, 185)
RED = (231, 76, 60)
GREEN = (39, 174, 96)
HINT_LINE = (180, 200, 220)


class Button:
    def __init__(self, x, y, w, h, text, color=BUTTON_BG):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.color = color
        self.hover = False

    def draw(self, screen, font):
        color = BUTTON_HOVER if self.hover else self.color
        pygame.draw.rect(screen, color, self.rect, border_radius=8)
        pygame.draw.rect(screen, (0, 0, 0), self.rect, 2, border_radius=8)
        label = font.render(self.text, True, TEXT_WHITE)
        screen.blit(label, label.get_rect(center=self.rect.center))

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.hover = self.rect.collidepoint(event.pos)
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                return True
        return False


def point_to_segment_dist(px, py, x1, y1, x2, y2):
    """Khoảng cách từ điểm tới đoạn thẳng"""
    dx, dy = x2 - x1, y2 - y1
    if dx == 0 and dy == 0:
        return math.hypot(px - x1, py - y1)
    t = max(0, min(1, ((px - x1) * dx + (py - y1) * dy) / (dx * dx + dy * dy)))
    return math.hypot(px - (x1 + t * dx), py - (y1 + t * dy))


class HashiGame:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Hashiwokakero - Bridges")
        self.screen = pygame.display.set_mode((WINDOW_W, WINDOW_H))
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("segoeui", 20)
        self.font_large = pygame.font.SysFont("segoeui", 28, bold=True)
        self.font_small = pygame.font.SysFont("segoeui", 16)

        self.phase = "menu"
        self.difficulty = "7x7"
        self.grid = None
        self.state = None
        self.checker = None
        self.start_time = 0
        self.elapsed = 0
        self.message = ""
        self.solution_state = None
        self.cell_size = 40
        self.offset_x = 0
        self.offset_y = 0
        self.island_positions = {}
        self.hover_corridor = None

        self.menu_buttons = []
        diffs = [("7x7", "Dễ 7×7"), ("9x9", "Trung Bình 9×9"), ("11x11", "Khó 11×11"),
                 ("13x13", "Rất khó 13×13")]
        for i, (d, label) in enumerate(diffs):
            btn = Button(300, 180 + i * 70, 400, 55, label)
            btn.difficulty = d
            self.menu_buttons.append(btn)

        self.btn_solution = Button(20, WINDOW_H - 60, 150, 40, "Xem đáp án", RED)
        self.btn_restart = Button(185, WINDOW_H - 60, 130, 40, "Chơi lại")
        self.btn_new = Button(330, WINDOW_H - 60, 130, 40, "Màn mới")
        self.btn_menu = Button(475, WINDOW_H - 60, 110, 40, "Menu")

    def start_game(self, difficulty):
        try:
            gen = TestGenerator(seed=int(time.time()) % 99999)
            puzzle = gen.generate(difficulty=difficulty)
            self.grid = Grid(puzzle.matrix)
            self.state = PuzzleState(self.grid)
            self.checker = ConstraintChecker(self.grid)
            self.difficulty = difficulty
            self.start_time = time.time()
            self.elapsed = 0
            self.message = "Click vào đường giữa 2 đảo để đặt / tăng / xóa cầu"
            self.solution_state = None
            self.hover_corridor = None
            self.phase = "playing"
            self._compute_layout()
        except GenerationError as e:
            self.message = f"Lỗi tạo puzzle: {e}"

    def restart_level(self):
        """Chơi lại màn hiện tại (cùng bàn cờ, xóa hết cầu, reset giờ)"""
        if self.grid is None:
            return
        self.state = PuzzleState(self.grid)
        self.start_time = time.time()
        self.elapsed = 0
        self.message = "Chơi lại màn này — cầu đã được xóa"
        self.solution_state = None
        self.hover_corridor = None
        self.phase = "playing"

    def _compute_layout(self):
        rows, cols = self.grid.rows, self.grid.cols
        max_cell = min((WINDOW_W - 80) // cols, (WINDOW_H - 160) // rows)
        self.cell_size = max(28, min(max_cell, 56))
        board_w = cols * self.cell_size
        self.offset_x = (WINDOW_W - board_w) // 2
        self.offset_y = 80

        self.island_positions = {}
        for iid, island in self.grid.islands.items():
            cx = self.offset_x + island.col * self.cell_size + self.cell_size // 2
            cy = self.offset_y + island.row * self.cell_size + self.cell_size // 2
            self.island_positions[iid] = (cx, cy)

    def get_corridor_at_pos(self, pos, threshold=14):
        """Tìm hành lang gần chuột nhất"""
        mx, my = pos
        best, best_dist = None, threshold
        for corridor in self.grid.corridors.values():
            a = self.island_positions[corridor.island_a]
            b = self.island_positions[corridor.island_b]
            dist = point_to_segment_dist(mx, my, a[0], a[1], b[0], b[1])
            if dist < best_dist:
                best_dist = dist
                best = corridor.identifier
        return best

    def cycle_bridge(self, corridor_id):
        """0 → 1 → 2 → 0
        Chỉ cấm khi cầu BỊ CẮT. Vượt số cầu của đảo vẫn cho phép (hiện màu đỏ).
        """
        current = self.state.corridor_value(corridor_id)
        new_val = (current + 1) % 3

        old = current
        self.state.set_corridor_value(corridor_id, new_val)

        # Chỉ kiểm tra cắt cầu — KHÔNG chặn khi vượt degree
        if new_val > 0 and not self.checker._avoid_crossings(self.state):
            self.state.set_corridor_value(corridor_id, old)
            self.message = "Không hợp lệ — cầu bị cắt nhau"
            return

        if new_val == 0:
            self.message = "Đã xóa cầu"
        else:
            self.message = f"Đặt {new_val} cầu"

        if self.state.is_goal():
            self.phase = "solved"
            self.elapsed = time.time() - self.start_time
            self.message = "BẠN ĐÃ THẮNG!"

    def show_solution(self):
        solver = AStarSolver(self.checker, heuristic=Heuristic.composite)
        result = solver.solve(PuzzleState(self.grid))
        if result.status == "SOLVED" and result.state:
            self.solution_state = result.state
            self.phase = "solution"
            self.elapsed = time.time() - self.start_time
            self.message = "Đáp án từ A*"
        else:
            self.message = "Không tìm thấy lời giải"

    def draw_board(self, state):
        rows, cols = self.grid.rows, self.grid.cols
        board_rect = pygame.Rect(
            self.offset_x - 4, self.offset_y - 4,
            cols * self.cell_size + 8, rows * self.cell_size + 8
        )
        pygame.draw.rect(self.screen, GRID_BG, board_rect, border_radius=6)
        pygame.draw.rect(self.screen, (200, 200, 200), board_rect, 2, border_radius=6)

        # Vẽ mọi hành lang (kể cả chưa có cầu) để dễ click
        for corridor in self.grid.corridors.values():
            a = self.island_positions[corridor.island_a]
            b = self.island_positions[corridor.island_b]
            val = state.corridor_value(corridor.identifier)
            is_hover = corridor.identifier == self.hover_corridor

            if val == 0:
                color = BRIDGE_HOVER if is_hover else HINT_LINE
                width = 7 if is_hover else 2
                pygame.draw.line(self.screen, color, a, b, width)
            elif val == 1:
                color = BRIDGE_HOVER if is_hover else BRIDGE_COLOR
                pygame.draw.line(self.screen, color, a, b, 5)
            else:
                color = BRIDGE_HOVER if is_hover else BRIDGE_COLOR
                dx, dy = b[0] - a[0], b[1] - a[1]
                length = math.hypot(dx, dy) or 1
                ox, oy = -dy / length * 5, dx / length * 5
                pygame.draw.line(self.screen, color, (a[0]+ox, a[1]+oy), (b[0]+ox, b[1]+oy), 4)
                pygame.draw.line(self.screen, color, (a[0]-ox, a[1]-oy), (b[0]-ox, b[1]-oy), 4)

        # Vẽ đảo — KHÔNG khóa, vẫn tương tác được
        radius = int(self.cell_size * 0.38)
        for iid, island in self.grid.islands.items():
            cx, cy = self.island_positions[iid]
            remaining = state.remaining_degree(island)

            if remaining < 0:
                color = RED
            elif remaining == 0:
                color = ISLAND_DONE
            else:
                color = ISLAND_COLOR

            pygame.draw.circle(self.screen, color, (cx, cy), radius)
            pygame.draw.circle(self.screen, (0, 0, 0), (cx, cy), radius, 2)
            label = self.font.render(str(island.target), True, TEXT_WHITE)
            self.screen.blit(label, label.get_rect(center=(cx, cy)))

    def draw_menu(self):
        self.screen.fill(BG)
        title = self.font_large.render("Hashiwokakero (Bridges)", True, TEXT_DARK)
        self.screen.blit(title, title.get_rect(center=(WINDOW_W // 2, 80)))
        sub = self.font.render("Chọn độ khó để bắt đầu", True, TEXT_DARK)
        self.screen.blit(sub, sub.get_rect(center=(WINDOW_W // 2, 120)))
        for btn in self.menu_buttons:
            btn.draw(self.screen, self.font)
        hint = self.font_small.render(
            "Cách chơi: Click vào đường giữa 2 đảo để đặt cầu (1 → 2 → xóa)",
            True, (100, 100, 100)
        )
        self.screen.blit(hint, hint.get_rect(center=(WINDOW_W // 2, WINDOW_H - 40)))

    def draw_playing(self):
        self.screen.fill(BG)
        if self.phase == "playing":
            self.elapsed = time.time() - self.start_time
        mins, secs = divmod(int(self.elapsed), 60)
        header = self.font.render(
            f"Độ khó: {self.difficulty}   |   ⏱️ {mins:02d}:{secs:02d}   |   {self.message}",
            True, TEXT_DARK
        )
        self.screen.blit(header, (20, 25))

        draw_state = self.solution_state if self.phase == "solution" else self.state
        self.draw_board(draw_state)

        self.btn_solution.draw(self.screen, self.font_small)
        self.btn_restart.draw(self.screen, self.font_small)
        self.btn_new.draw(self.screen, self.font_small)
        self.btn_menu.draw(self.screen, self.font_small)

        if self.phase == "solved":
            overlay = self.font_large.render("BẠN ĐÃ THẮNG!", True, GREEN)
            self.screen.blit(overlay, overlay.get_rect(center=(WINDOW_W // 2, WINDOW_H - 100)))

    def run(self):
        running = True
        while running:
            mouse_pos = pygame.mouse.get_pos()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                if self.phase == "menu":
                    for btn in self.menu_buttons:
                        if btn.handle_event(event):
                            self.start_game(btn.difficulty)

                elif self.phase in ("playing", "solved", "solution"):
                    self.btn_solution.handle_event(event)
                    self.btn_restart.handle_event(event)
                    self.btn_new.handle_event(event)
                    self.btn_menu.handle_event(event)

                    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                        if self.btn_solution.rect.collidepoint(event.pos):
                            self.show_solution()
                        elif self.btn_restart.rect.collidepoint(event.pos):
                            self.restart_level()
                        elif self.btn_new.rect.collidepoint(event.pos):
                            self.start_game(self.difficulty)
                        elif self.btn_menu.rect.collidepoint(event.pos):
                            self.phase = "menu"
                        elif self.phase == "playing":
                            cid = self.get_corridor_at_pos(event.pos)
                            if cid is not None:
                                self.cycle_bridge(cid)

                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_ESCAPE:
                            self.phase = "menu"
                        elif event.key == pygame.K_r:
                            self.restart_level()          # R = chơi lại màn này
                        elif event.key == pygame.K_n:
                            self.start_game(self.difficulty)  # N = màn mới
                        elif event.key == pygame.K_s:
                            self.show_solution()

            if self.phase == "playing":
                self.hover_corridor = self.get_corridor_at_pos(mouse_pos)
            else:
                self.hover_corridor = None

            if self.phase == "menu":
                self.draw_menu()
            else:
                self.draw_playing()

            pygame.display.flip()
            self.clock.tick(FPS)

        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    game = HashiGame()
    game.run()