import sys
from math import atan2, ceil, cos, radians, sin
from pathlib import Path
from time import time

import pygame
from pygame import Cursor, gfxdraw, Rect, SurfaceType
# noinspection PyProtectedMember
from pygame._sdl2 import Window
from pygame.font import Font

from graph import Graph, Node

WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 720
WINDOW_MARGIN = 25
GRID_WIDTH = 900
GRID_HEIGHT = 620
BUTTON_HEIGHT = 40
BUTTON_WIDTH = 200
BUTTON_GAP = 10
HOVER_TUPLE_STEP = 6
HOVER_TEXT_GAP = 5
HOVER_TEXT_PADDING = 10
ANIMATION_SPEED = 0.25
PI_6_RADIANS = radians(30)
PI_2_RADIANS = radians(90)

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GOLD = (255, 215, 64)
GRAY = (128, 128, 128)
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


class Arrow:
    _start: tuple[int, int]
    _end: tuple[int, int]
    _color: tuple[int, int, int]
    _width: int
    _tip: list[tuple[int, int]]

    def __init__(
            self,
            start: tuple[int, int],
            end: tuple[int, int],
            color: tuple[int, int, int],
            width: int,
            tip_size: int
    ) -> None:
        self._start = start
        self._end = end
        self._color = color
        self._width = width

        p1 = (0, -1)
        p2 = (cos(PI_6_RADIANS), sin(PI_6_RADIANS))
        p3 = (cos(PI_6_RADIANS) * -1, sin(PI_6_RADIANS))

        ra = atan2(start[1] - end[1], start[0] - end[0]) - PI_2_RADIANS
        rp1x = p1[0] * cos(ra) - p1[1] * sin(ra)
        rp1y = p1[0] * sin(ra) + p1[1] * cos(ra)
        rp2x = p2[0] * cos(ra) - p2[1] * sin(ra)
        rp2y = p2[0] * sin(ra) + p2[1] * cos(ra)
        rp3x = p3[0] * cos(ra) - p3[1] * sin(ra)
        rp3y = p3[0] * sin(ra) + p3[1] * cos(ra)
        rp1 = (rp1x, rp1y)
        rp2 = (rp2x, rp2y)
        rp3 = (rp3x, rp3y)

        self._tip = [
            (int(end[0] + rp1[0] * tip_size), int(end[1] + rp1[1] * tip_size)),
            (int(end[0] + rp2[0] * tip_size), int(end[1] + rp2[1] * tip_size)),
            (int(end[0] + rp3[0] * tip_size), int(end[1] + rp3[1] * tip_size)),
        ]

    def draw(self, screen: SurfaceType, color: tuple[int, int, int] | None = None) -> None:
        pygame.draw.line(screen, color or self._color, self._start, self._end, self._width)
        gfxdraw.filled_polygon(screen, self._tip, color or self._color)
        gfxdraw.aapolygon(screen, self._tip, color or self._color)


class Algorithm:
    name: str
    path: list[Node] | None
    color: tuple[int, int, int]
    _algorithm_text_surface: SurfaceType
    _algorithm_text_position: tuple[int, int]
    _algorithm_color_rect: Rect
    _solution_text_surface: SurfaceType
    _hover_text_surface: SurfaceType | None
    _solution_text_position: tuple[int, int]
    _hover_text_position: tuple[int, int] | None
    _hover_area: Rect | None
    _popup_text_surfaces: list[SurfaceType]
    _popup_text_positions: list[tuple[int, int]]
    _popup_color_rect: Rect | None
    _arrows: list[Arrow]

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

        self._algorithm_text_surface = font.render(name, True, BLACK)
        self._algorithm_text_position = (
            WINDOW_MARGIN,
            WINDOW_HEIGHT - WINDOW_MARGIN - self._algorithm_text_surface.get_height()
        )

        self._algorithm_color_rect = Rect(
            WINDOW_MARGIN + self._algorithm_text_surface.get_width() + 10,
            WINDOW_HEIGHT - WINDOW_MARGIN - self._algorithm_text_surface.get_height() // 2 - 10,
            20,
            20
        )

        self._solution_text_surface = font.render(
            "No solution found" if path is None else f"Found solution with {len(path) - 1} jumps",
            True,
            BLACK
        )
        self._hover_text_surface = font.render("(hover for path)", True, GRAY) if path is not None else None

        self._solution_text_position = (
            (WINDOW_WIDTH
             - self._solution_text_surface.get_width()
             - (self._hover_text_surface.get_width() if path is not None else 0)
             ) // 2,
            WINDOW_HEIGHT - WINDOW_MARGIN - self._solution_text_surface.get_height()
        )

        self._hover_text_position = (
            self._solution_text_position[0] + self._solution_text_surface.get_width() + 10,
            WINDOW_HEIGHT - WINDOW_MARGIN - self._hover_text_surface.get_height()
        ) if path is not None else None

        self._hover_area = Rect(
            *self._solution_text_position,
            self._solution_text_surface.get_width() + self._hover_text_surface.get_width(),
            self._solution_text_surface.get_height()
        ) if path is not None else None

        self._popup_text_surfaces = []
        self._popup_text_positions = []

        if path is not None:
            left_most = WINDOW_WIDTH
            top_most = WINDOW_HEIGHT
            max_width = 0
            box_height = -HOVER_TEXT_GAP

            for i in range(0, len(path), HOVER_TUPLE_STEP):
                string = ("-> " if i > 0 else "") + " -> ".join(map(str, path[i:i + HOVER_TUPLE_STEP]))
                text_surface = font.render(string, True, BLACK)
                text_position = (
                    (WINDOW_WIDTH - text_surface.get_width()) // 2,
                    self._solution_text_position[1]
                    - HOVER_TEXT_PADDING * 2
                    - (text_surface.get_height() + HOVER_TEXT_GAP) * ceil((len(path) - i) / HOVER_TUPLE_STEP)
                )

                left_most = min(left_most, text_position[0])
                top_most = min(top_most, text_position[1])
                max_width = max(max_width, text_surface.get_width())
                box_height += HOVER_TEXT_GAP + text_surface.get_height()

                self._popup_text_surfaces.append(text_surface)
                self._popup_text_positions.append(text_position)

            self._popup_background_rect = Rect(
                left_most - HOVER_TEXT_PADDING,
                top_most - HOVER_TEXT_PADDING,
                max_width + HOVER_TEXT_PADDING * 2,
                box_height + HOVER_TEXT_PADDING * 2
            )
        else:
            self._popup_background_rect = None

        self._draw_popup = False

        arrow_color = (255 - color[0], 255 - color[1], 255 - color[2])
        self._arrows = []

        if path is not None:
            for i in range(1, len(path)):
                previous = path[i - 1].pos
                current = path[i].pos

                arrow = Arrow(
                    (
                        WINDOW_MARGIN + previous[1] * cell_size + cell_size // 2,
                        WINDOW_MARGIN + previous[0] * cell_size + cell_size // 2
                    ),
                    (
                        WINDOW_MARGIN + current[1] * cell_size + cell_size // 2,
                        WINDOW_MARGIN + current[0] * cell_size + cell_size // 2
                    ),
                    arrow_color,
                    3,
                    cell_size // 10,
                )

                self._arrows.append(arrow)

    def on_mouse_motion(self, mouse_pos: tuple[int, int]) -> None:
        if self.path is not None:
            self._draw_popup = self._hover_area.collidepoint(mouse_pos)

    def draw_text(self, screen: SurfaceType) -> None:
        screen.blit(self._solution_text_surface, self._solution_text_position)
        screen.blit(self._algorithm_text_surface, self._algorithm_text_position)
        pygame.draw.rect(screen, self.color, self._algorithm_color_rect)
        pygame.draw.rect(screen, BLACK, self._algorithm_color_rect, 1)

        if self._hover_text_surface is not None:
            screen.blit(self._hover_text_surface, self._hover_text_position)

        if self._draw_popup:
            pygame.draw.rect(screen, self.color, self._popup_background_rect)

            for i, text_surface in enumerate(self._popup_text_surfaces):
                screen.blit(text_surface, self._popup_text_positions[i])

    def draw_arrows(self, screen: SurfaceType, until: int) -> None:
        for i in range(until):
            self._arrows[i].draw(screen, GOLD if i == until - 1 else None)


class Button:
    rect: Rect
    enabled: bool
    _background_color: tuple[int, int, int]
    _border_color: tuple[int, int, int]
    _text_surface: SurfaceType

    def __init__(
            self,
            position: tuple[int, int],
            text: str,
            text_font: Font,
            size: tuple[int, int] | None = None,
            background_color: tuple[int, int, int] | None = None,
            border_color: tuple[int, int, int] | None = None,
            text_color: tuple[int, int, int] | None = None,
    ) -> None:
        self.rect = Rect(position, size or (BUTTON_WIDTH, BUTTON_HEIGHT))
        self.enabled = True
        self._background_color = background_color or LIGHT_GRAY
        self._border_color = border_color or BLACK
        self._text_surface = text_font.render(text, True, text_color or BLACK)
        self._text_position = (
            self.rect.x + self.rect.width // 2 - self._text_surface.get_width() // 2,
            self.rect.y + self.rect.height // 2 - self._text_surface.get_height() // 2
        )
        self._disabled_overlay = pygame.Surface(self.rect.size)
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
    _last_animation_update: float
    _animation_step: int
    _show_path: bool
    _run_algorithm_button: Button
    _next_algorithm_button: Button

    def __init__(self) -> None:
        global WINDOW_WIDTH, WINDOW_HEIGHT, GRID_WIDTH, GRID_HEIGHT

        pygame.init()
        self._screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), flags=pygame.RESIZABLE)
        Window.from_display_module().maximize()
        pygame.display.set_caption("Pathfinding Algorithms Visualizer")

        WINDOW_WIDTH, WINDOW_HEIGHT = self._screen.get_size()
        GRID_WIDTH = WINDOW_WIDTH - 300
        GRID_HEIGHT = WINDOW_HEIGHT - 120

        self._graph = None
        self._grid = {}
        self._cell_size = 0

        self._font = Font(FONT_PATH, 20)
        self._cell_font = Font(FONT_PATH, 0)

        self._algorithms = []

        self._current_algorithm_index = 0
        self._path = None
        self._animation_in_progress = False
        self._last_animation_update = 0
        self._animation_step = 0
        self._show_path = False

        self._arrow_cursor = Cursor(pygame.SYSTEM_CURSOR_ARROW)
        self._hand_cursor = Cursor(pygame.SYSTEM_CURSOR_HAND)

        self._run_algorithm_button = Button(
            (
                WINDOW_WIDTH - BUTTON_WIDTH - WINDOW_MARGIN,
                WINDOW_HEIGHT - BUTTON_HEIGHT - WINDOW_MARGIN,
            ),
            "Run algorithm",
            self._font,
        )
        self._next_algorithm_button = Button(
            (
                WINDOW_WIDTH - BUTTON_WIDTH - WINDOW_MARGIN,
                WINDOW_HEIGHT - 2 * BUTTON_HEIGHT - 2 * WINDOW_MARGIN + BUTTON_GAP,
            ),
            "Next algorithm",
            self._font,
        )
        self._next_graph_button = Button(
            (
                WINDOW_WIDTH - BUTTON_WIDTH - WINDOW_MARGIN,
                WINDOW_HEIGHT - 3 * BUTTON_HEIGHT - 3 * WINDOW_MARGIN + 2 * BUTTON_GAP,
            ),
            "Next graph",
            self._font,
        )

    def run(self, graph: Graph) -> None:
        self._set_graph(graph)

        while True:
            self._screen.fill(WHITE)

            should_exit = self._handle_events()
            if should_exit:
                break

            # grid
            for cell in self._grid.values():
                cell.draw(self._screen)

            # buttons
            self._run_algorithm_button.draw(self._screen)
            self._next_algorithm_button.draw(self._screen)
            self._next_graph_button.draw(self._screen)

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
        self._cell_size = min(min(GRID_WIDTH // len(graph.matrix[0]), GRID_HEIGHT // len(graph.matrix)), 100)
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
                "G" if node.is_goal else str(node.value)
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

        current_algorithm = self._algorithms[self._current_algorithm_index]
        range_end = (self._animation_step + 1 if self._animation_in_progress and self._animation_step < len(self._path)
                     else len(self._path))

        for i in range(range_end):
            self._grid[self._path[i].pos].draw(self._screen, current_algorithm.color)

        current_algorithm.draw_arrows(self._screen, range_end - 1)

    def _handle_events(self) -> bool:
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

                    if self._next_algorithm_button.contains(mouse_pos):
                        self._update_algorithm()
                        continue

                    if self._next_graph_button.contains(mouse_pos):
                        return True

                case pygame.MOUSEMOTION:
                    mouse_pos = pygame.mouse.get_pos()

                    self._algorithms[self._current_algorithm_index].on_mouse_motion(mouse_pos)

                    is_hover = (
                            (self._run_algorithm_button.contains(mouse_pos) and self._run_algorithm_button.enabled)
                            or self._next_algorithm_button.contains(mouse_pos)
                            or self._next_graph_button.contains(mouse_pos)
                    )

                    pygame.mouse.set_cursor(self._hand_cursor if is_hover else self._arrow_cursor)

        return False

    def _start_animation(self) -> None:
        if self._animation_in_progress or self._path is None:
            return

        self._show_path = True
        self._animation_in_progress = True
        self._last_animation_update = 0
        self._animation_step = 0

    def _update_algorithm(self) -> None:
        self._show_path = False
        self._animation_in_progress = False
        self._last_animation_update = 0
        self._animation_step = 0
        self._current_algorithm_index = (self._current_algorithm_index + 1) % len(self._algorithms)

        current_algorithm = self._algorithms[self._current_algorithm_index]
        self._path = current_algorithm.path
        self._run_algorithm_button.enabled = self._path is not None

    def _update_animation(self) -> None:
        if not self._animation_in_progress or self._path is None:
            return

        if self._animation_step >= len(self._path):
            self._animation_in_progress = False
            return

        if (now := time()) - self._last_animation_update > ANIMATION_SPEED:
            self._last_animation_update = now
            self._animation_step += 1
