import sys
import time
from pathlib import Path

import pygame
from pygame import Cursor, Rect, SurfaceType
from pygame.font import Font

from src.graph import Graph, Node

WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
WINDOW_MARGIN = 25
GRID_WIDTH = 600
GRID_HEIGHT = 500
BUTTON_HEIGHT = 40
BUTTON_WIDTH = 200
BUTTON_GAP = 10
ANIMATION_SPEED = 0.25

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GOLD = (255, 215, 64)
LIGHT_GRAY = (230, 230, 230)
DFS_COLOR = (255, 192, 192)
UCS_DISTANCE_COLOR = (255, 192, 128)
UCS_JUMPS_COLOR = (255, 255, 192)
UCS_VALUE_COLOR = (192, 255, 192)
BFS_COLOR = (192, 255, 255)
DIJKSTRA_COLOR = (128, 192, 255)
A_STAR_COLOR = (255, 192, 255)

ROOT_PATH = Path(__file__).parent.parent.resolve()
FONT_PATH = ROOT_PATH / "resources/fonts/JetBrainsMono-Regular.ttf"


class Algorithm:
    name: str
    path: list[Node] | None
    color: tuple[int, int, int]
    _line_color: tuple[int, int, int]
    _algorithm_text_surface: SurfaceType
    _algorithm_text_position: tuple[int, int]
    _algorithm_color_rect: Rect
    _lines: list[tuple[tuple[int, int], tuple[int, int]]]

    def __init__(
            self,
            name: str,
            path: list[Node] | None,
            font: Font,
            color: tuple[int, int, int],
            cell_size: int
    ) -> None:
        self.name = name
        self.path = path
        self.color = color
        self._line_color = (255 - color[0], 255 - color[1], 255 - color[2])

        self._algorithm_text_surface = font.render(f"Algorithm: {name}", True, BLACK)
        self._algorithm_text_position = (WINDOW_MARGIN, WINDOW_HEIGHT - BUTTON_HEIGHT - WINDOW_MARGIN)

        self._algorithm_color_rect = Rect(
            WINDOW_MARGIN + self._algorithm_text_surface.get_width() + 10,
            WINDOW_HEIGHT - BUTTON_HEIGHT - WINDOW_MARGIN + self._algorithm_text_surface.get_height() // 2 - 10,
            20,
            20
        )

        self._lines = []

        for i in range(1, len(path)):
            previous = path[i - 1].pos
            current = path[i].pos

            start_pos = (
                WINDOW_MARGIN + previous[1] * cell_size + cell_size // 2,
                WINDOW_MARGIN + previous[0] * cell_size + cell_size // 2
            )
            end_pos = (
                WINDOW_MARGIN + current[1] * cell_size + cell_size // 2,
                WINDOW_MARGIN + current[0] * cell_size + cell_size // 2
            )

            self._lines.append((start_pos, end_pos))

    def draw_text(self, screen: SurfaceType) -> None:
        screen.blit(self._algorithm_text_surface, self._algorithm_text_position)
        pygame.draw.rect(screen, self.color, self._algorithm_color_rect)
        pygame.draw.rect(screen, BLACK, self._algorithm_color_rect, 1)

    def draw_lines(self, screen: SurfaceType, up_to: int) -> None:
        for i in range(up_to):
            start_pos, end_pos = self._lines[i]
            pygame.draw.line(screen, self._line_color, start_pos, end_pos, 3)


class Button:
    rect: Rect
    enabled: bool
    _background_color: tuple[int, int, int]
    _border_color: tuple[int, int, int]
    _text_surface: SurfaceType

    def __init__(
            self,
            rect: Rect,
            background_color: tuple[int, int, int],
            border_color: tuple[int, int, int],
            text: str,
            text_font: Font,
            text_color: tuple[int, int, int]
    ) -> None:
        self.rect = rect
        self.enabled = True
        self._background_color = background_color
        self._border_color = border_color
        self._text_surface = text_font.render(text, True, text_color)
        self._text_position = (
            rect.x + rect.width // 2 - self._text_surface.get_width() // 2,
            rect.y + rect.height // 2 - self._text_surface.get_height() // 2
        )
        self._disabled_overlay = pygame.Surface(rect.size)
        self._disabled_overlay.set_alpha(128)
        self._disabled_overlay.fill(BLACK)

    def contains(self, point: tuple[int, int]) -> bool:
        return self.rect.collidepoint(point)

    def draw(self, screen: SurfaceType) -> None:
        pygame.draw.rect(screen, self._background_color, self.rect)
        pygame.draw.rect(screen, self._border_color, self.rect, 2)
        screen.blit(self._text_surface, self._text_position)

        if not self.enabled:
            screen.blit(self._disabled_overlay, self.rect)


class Cell:
    _rect: Rect
    _color: tuple[int, int, int]
    _text_surface: SurfaceType
    _text_position: tuple[int, int]

    def __init__(self, rect: Rect, color: tuple[int, int, int], font: Font, text: str):
        self._rect = rect
        self._color = color

        self._text_surface = font.render(text, True, BLACK)
        self._text_position = (
            rect.x + rect.w // 2 - self._text_surface.get_width() // 2,
            rect.y + rect.h // 2 - self._text_surface.get_height() // 2
        )

    def draw(self, screen: SurfaceType, color: tuple[int, int, int] | None = None) -> None:
        pygame.draw.rect(screen, color or self._color, self._rect)
        pygame.draw.rect(screen, BLACK, self._rect, 1)
        screen.blit(self._text_surface, self._text_position)


class PathfindingVisualizer:
    _graph: Graph | None
    _grid: dict[tuple[int, int], Cell]
    _cell_size: int
    _screen: SurfaceType
    _font: Font
    _cell_font: Font
    _algorithms: list[Algorithm]
    _current_algorithm_index: int
    _path: list[Node] | None
    _animation_in_progress: bool
    _animation_step: int
    _show_path: bool
    _run_algorithm_button: Button
    _next_algorithm_button: Button

    def __init__(self) -> None:
        pygame.init()
        self._screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Pathfinding Algorithms Visualizer")

        self._graph = None
        self._grid = {}
        self._cell_size = 0

        self._font = Font(FONT_PATH, 20)
        self._cell_font = Font(FONT_PATH, 0)

        self._algorithms = []

        self._current_algorithm_index = 0
        self._path = None
        self._animation_in_progress = False
        self._animation_step = 0
        self._show_path = False

        self._arrow_cursor = Cursor(pygame.SYSTEM_CURSOR_ARROW)
        self._hand_cursor = Cursor(pygame.SYSTEM_CURSOR_HAND)

        # TODO add "next graph" button
        self._run_algorithm_button = Button(
            Rect(
                WINDOW_WIDTH - BUTTON_WIDTH - WINDOW_MARGIN,
                WINDOW_HEIGHT - BUTTON_HEIGHT - WINDOW_MARGIN,
                BUTTON_WIDTH,
                BUTTON_HEIGHT
            ),
            LIGHT_GRAY,
            BLACK,
            "Run algorithm",
            self._font,
            BLACK
        )
        self._next_algorithm_button = Button(
            Rect(
                WINDOW_WIDTH - BUTTON_WIDTH - WINDOW_MARGIN,
                WINDOW_HEIGHT - 2 * BUTTON_HEIGHT - 2 * WINDOW_MARGIN + BUTTON_GAP,
                BUTTON_WIDTH,
                BUTTON_HEIGHT
            ),
            LIGHT_GRAY,
            BLACK,
            "Next algorithm",
            self._font,
            BLACK
        )

    def run(self, graph: Graph) -> None:
        self._set_graph(graph)

        while True:
            self._screen.fill(WHITE)

            self._handle_events()

            # grid
            for cell in self._grid.values():
                cell.draw(self._screen)

            # buttons
            self._run_algorithm_button.draw(self._screen)
            self._next_algorithm_button.draw(self._screen)

            # algorithm text
            current_algorithm = self._algorithms[self._current_algorithm_index]
            current_algorithm.draw_text(self._screen)

            self._draw_path()
            self._update_animation()

            pygame.display.flip()

    @staticmethod
    def quit() -> None:
        pygame.quit()

    def _set_graph(self, graph: Graph) -> None:
        self._graph = graph
        self._cell_size = min(GRID_WIDTH // len(graph.matrix[0]), GRID_HEIGHT // len(graph.matrix))
        self._cell_font = Font(FONT_PATH, self._cell_size // 3)

        self._grid = {
            node.pos: Cell(
                Rect(
                    WINDOW_MARGIN + node.pos[1] * self._cell_size,
                    WINDOW_MARGIN + node.pos[0] * self._cell_size,
                    self._cell_size,
                    self._cell_size
                ),
                GOLD if node.pos == self._graph.start or node.is_goal else WHITE,
                self._cell_font,
                "S" if node.pos == self._graph.start else "G" if node.is_goal else str(node.value)
            ) for node in graph.nodes.values()
        }

        self._algorithms = [
            Algorithm("DFS", self._graph.dfs(), self._font, DFS_COLOR, self._cell_size),
            Algorithm("UCS (distance)", self._graph.ucs_by_distance(), self._font, UCS_DISTANCE_COLOR, self._cell_size),
            Algorithm("UCS (jumps)", self._graph.ucs_by_jumps(), self._font, UCS_JUMPS_COLOR, self._cell_size),
            Algorithm("UCS (value)", self._graph.ucs_by_value(), self._font, UCS_VALUE_COLOR, self._cell_size),
            Algorithm("BFS", self._graph.bfs(), self._font, BFS_COLOR, self._cell_size),
            Algorithm("Dijkstra", self._graph.dijkstra(), self._font, DIJKSTRA_COLOR, self._cell_size),
            Algorithm("A*", self._graph.a_star(), self._font, A_STAR_COLOR, self._cell_size)
        ]

        self._current_algorithm_index = -1
        self._update_algorithm()

    def _draw_path(self) -> None:
        if not self._show_path:
            return

        # TODO add arrow tip
        current_algorithm = self._algorithms[self._current_algorithm_index]
        range_end = (self._animation_step + 1 if self._animation_in_progress and self._animation_step < len(self._path)
                     else len(self._path))

        for i in range(range_end):
            self._grid[self._path[i].pos].draw(self._screen, current_algorithm.color)

        current_algorithm.draw_lines(self._screen, range_end - 1)

    def _handle_events(self) -> None:
        for event in pygame.event.get():
            match event.type:
                case pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                case pygame.MOUSEBUTTONDOWN:
                    mouse_pos = pygame.mouse.get_pos()

                    if self._run_algorithm_button.contains(mouse_pos) and self._run_algorithm_button.enabled:
                        self._start_animation()
                        continue

                    if self._next_algorithm_button.contains(mouse_pos) and self._next_algorithm_button.enabled:
                        self._update_algorithm()
                        continue

                case pygame.MOUSEMOTION:
                    mouse_pos = pygame.mouse.get_pos()
                    is_hover = (
                            (self._run_algorithm_button.contains(mouse_pos) and self._run_algorithm_button.enabled)
                            or (self._next_algorithm_button.contains(mouse_pos) and self._next_algorithm_button.enabled)
                    )

                    pygame.mouse.set_cursor(self._hand_cursor if is_hover else self._arrow_cursor)

    def _start_animation(self) -> None:
        if self._animation_in_progress or self._path is None:
            return

        self._show_path = True
        self._animation_in_progress = True
        self._animation_step = 0

    def _update_algorithm(self) -> None:
        self._show_path = False
        self._animation_in_progress = False
        self._animation_step = 0
        self._current_algorithm_index = (self._current_algorithm_index + 1) % len(self._algorithms)

        current_algorithm = self._algorithms[self._current_algorithm_index]
        self._path = current_algorithm.path
        self._run_algorithm_button.enabled = self._path is not None

        # TODO display this instead
        if self._path is None:
            print(f"No path found with {current_algorithm.name}")

    def _update_animation(self) -> None:
        if not self._animation_in_progress or self._path is None:
            return

        if self._animation_step < len(self._path):
            time.sleep(ANIMATION_SPEED)
            self._animation_step += 1
        else:
            self._animation_in_progress = False
