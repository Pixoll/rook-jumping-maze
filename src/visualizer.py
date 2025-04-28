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

    def __init__(self, name: str, path: list[Node] | None, color: tuple[int, int, int]) -> None:
        self.name = name
        self.path = path
        self.color = color


class Button:
    rect: Rect
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
        self._background_color = background_color
        self._border_color = border_color
        self._text_surface = text_font.render(text, True, text_color)
        self._text_position = (
            self.rect.x + self.rect.width // 2 - self._text_surface.get_width() // 2,
            self.rect.y + self.rect.height // 2 - self._text_surface.get_height() // 2
        )

    def draw(self, screen: SurfaceType) -> None:
        pygame.draw.rect(screen, self._background_color, self.rect)
        pygame.draw.rect(screen, self._border_color, self.rect, 2)
        screen.blit(self._text_surface, self._text_position)


class PathfindingVisualizer:
    _graph: Graph | None
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
    _algorithm_text_surface: SurfaceType
    _algorithm_text_position: tuple[int, int]
    _algorithm_color_rect: Rect

    def __init__(self) -> None:
        pygame.init()
        self._screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Pathfinding Algorithms Visualizer")

        self._graph = None
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

        self._algorithm_text_surface = self._font.render("_", True, BLACK)
        self._algorithm_text_position = (0, 0)
        self._algorithm_color_rect = Rect(0, 0, 0, 0)

    def run(self, graph: Graph) -> None:
        self._set_graph(graph)

        while True:
            self._screen.fill(WHITE)

            self._handle_events()
            self._draw_grid()
            self._draw_path()
            self._draw_buttons()
            self._update_animation()

            pygame.display.flip()

    @staticmethod
    def quit() -> None:
        pygame.quit()

    def _set_graph(self, graph: Graph) -> None:
        self._graph = graph
        self._cell_size = min(GRID_WIDTH // len(graph.matrix[0]), GRID_HEIGHT // len(graph.matrix))
        self._cell_font = Font(FONT_PATH, self._cell_size // 3)

        self._algorithms = [
            Algorithm("DFS", self._graph.dfs(), DFS_COLOR),
            Algorithm("UCS (distance)", self._graph.ucs_by_distance(), UCS_DISTANCE_COLOR),
            Algorithm("UCS (jumps)", self._graph.ucs_by_jumps(), UCS_JUMPS_COLOR),
            Algorithm("UCS (value)", self._graph.ucs_by_value(), UCS_VALUE_COLOR),
            Algorithm("BFS", self._graph.bfs(), BFS_COLOR),
            Algorithm("Dijkstra", self._graph.dijkstra(), DIJKSTRA_COLOR),
            Algorithm("A*", self._graph.a_star(), A_STAR_COLOR)
        ]

        self._current_algorithm_index = -1
        self._update_algorithm()

    def _draw_grid(self) -> None:
        for node in self._graph.nodes.values():
            self._draw_node(node, WHITE)

    def _draw_node(self, node: Node, color: tuple[int, int, int]) -> None:
        # TODO precalculate all this
        cell_color = GOLD if node.pos == self._graph.start or node.is_goal else color

        rect = Rect(
            WINDOW_MARGIN + node.pos[1] * self._cell_size,
            WINDOW_MARGIN + node.pos[0] * self._cell_size,
            self._cell_size,
            self._cell_size
        )

        pygame.draw.rect(self._screen, cell_color, rect)
        pygame.draw.rect(self._screen, BLACK, rect, 1)

        value = "S" if node.pos == self._graph.start else "G" if node.is_goal else str(node.value)
        value_text = self._cell_font.render(value, True, BLACK)
        self._screen.blit(value_text, (
            rect.x + self._cell_size // 2 - value_text.get_width() // 2,
            rect.y + self._cell_size // 2 - value_text.get_height() // 2
        ))

    def _draw_path(self) -> None:
        if not self._show_path:
            return

        # TODO precalculate all this
        # TODO ensure they're drawn on top of everything else
        # TODO add arrow tip
        cell_color = self._algorithms[self._current_algorithm_index].color
        path_color = (255 - cell_color[0], 255 - cell_color[1], 255 - cell_color[2])
        range_end = (self._animation_step + 1 if self._animation_in_progress and self._animation_step < len(self._path)
                     else len(self._path))

        for i in range(range_end):
            if i > 0:
                prev_x, prev_y = self._path[i - 1].pos
                curr_x, curr_y = self._path[i].pos

                start_pos = (
                    WINDOW_MARGIN + prev_y * self._cell_size + self._cell_size // 2,
                    WINDOW_MARGIN + prev_x * self._cell_size + self._cell_size // 2
                )
                end_pos = (
                    WINDOW_MARGIN + curr_y * self._cell_size + self._cell_size // 2,
                    WINDOW_MARGIN + curr_x * self._cell_size + self._cell_size // 2
                )

                pygame.draw.line(self._screen, path_color, start_pos, end_pos, 3)

            self._draw_node(self._path[i], cell_color)

    def _draw_buttons(self) -> None:
        self._run_algorithm_button.draw(self._screen)
        self._next_algorithm_button.draw(self._screen)

        current_algorithm = self._algorithms[self._current_algorithm_index]

        self._screen.blit(self._algorithm_text_surface, self._algorithm_text_position)
        pygame.draw.rect(self._screen, current_algorithm.color, self._algorithm_color_rect)
        pygame.draw.rect(self._screen, BLACK, self._algorithm_color_rect, 1)

    def _handle_events(self) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()

                if self._run_algorithm_button.rect.collidepoint(mouse_pos):
                    self._start_animation()
                    continue

                if self._next_algorithm_button.rect.collidepoint(mouse_pos):
                    self._update_algorithm()
                    continue

            if event.type == pygame.MOUSEMOTION:
                mouse_pos = pygame.mouse.get_pos()

                if self._run_algorithm_button.rect.collidepoint(mouse_pos):
                    pygame.mouse.set_cursor(self._hand_cursor)
                elif self._next_algorithm_button.rect.collidepoint(mouse_pos):
                    pygame.mouse.set_cursor(self._hand_cursor)
                else:
                    pygame.mouse.set_cursor(self._arrow_cursor)

    def _start_animation(self) -> None:
        if self._animation_in_progress:
            return

        if self._path:
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

        self._algorithm_text_surface = self._font.render(f"Algorithm: {current_algorithm.name}", True, BLACK)
        self._algorithm_text_position = (WINDOW_MARGIN, WINDOW_HEIGHT - BUTTON_HEIGHT - WINDOW_MARGIN)

        self._algorithm_color_rect = Rect(
            WINDOW_MARGIN + self._algorithm_text_surface.get_width() + 10,
            WINDOW_HEIGHT - BUTTON_HEIGHT - WINDOW_MARGIN + self._algorithm_text_surface.get_height() // 2 - 10,
            20,
            20
        )

        # TODO display this instead
        if self._path is None:
            print(f"No path found with {self._algorithms[self._current_algorithm_index].name}")

    def _update_animation(self) -> None:
        if not self._animation_in_progress or self._path is None:
            return

        if self._animation_step < len(self._path) - 1:
            time.sleep(ANIMATION_SPEED)
            self._animation_step += 1
        else:
            self._animation_in_progress = False
