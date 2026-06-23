from __future__ import annotations

import argparse
import heapq
from collections import deque
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Optional

Coordinate = tuple[int, int]
WALL = '#'


@dataclass(frozen=True)
class Maze:
    grid: list[list[str]]
    start: Coordinate
    key: Coordinate
    exit: Coordinate

    @property
    def height(self) -> int:
        return len(self.grid)

    @property
    def width(self) -> int:
        return len(self.grid[0]) if self.grid else 0

    def in_bounds(self, cell: Coordinate) -> bool:
        row, col = cell
        return 0 <= row < self.height and 0 <= col < self.width

    def passable(self, cell: Coordinate) -> bool:
        row, col = cell
        return self.grid[row][col] != WALL

    def neighbors(self, cell: Coordinate) -> Iterable[Coordinate]:
        row, col = cell
        for candidate in ((row - 1, col), (row + 1, col), (row, col - 1), (row, col + 1)):
            if self.in_bounds(candidate) and self.passable(candidate):
                yield candidate


def read_maze(path: Path, start: Optional[Coordinate] = None, key: Optional[Coordinate] = None,
              exit_cell: Optional[Coordinate] = None) -> Maze:
    grid = [list(line.rstrip('\n')) for line in path.read_text(encoding='utf-8').splitlines() if line]
    if not grid:
        raise ValueError('Maze file is empty')
    width = len(grid[0])
    if any(len(row) != width for row in grid):
        raise ValueError('Maze must be rectangular')

    found: dict[str, Coordinate] = {}
    for r, row in enumerate(grid):
        for c, value in enumerate(row):
            if value in {'A', 'K', 'E'}:
                found[value] = (r, c)
                grid[r][c] = '.'

    start = start or found.get('A')
    key = key or found.get('K')
    exit_cell = exit_cell or found.get('E')
    if start is None or key is None or exit_cell is None:
        raise ValueError('Set start, key and exit coordinates or mark them as A, K, E in the file')
    return Maze(grid=grid, start=start, key=key, exit=exit_cell)


def reconstruct_path(parents: dict[Coordinate, Coordinate | None], target: Coordinate) -> list[Coordinate]:
    if target not in parents:
        return []
    path: list[Coordinate] = []
    current: Coordinate | None = target
    while current is not None:
        path.append(current)
        current = parents[current]
    path.reverse()
    return path


def bfs(maze: Maze, source: Coordinate, target: Coordinate) -> list[Coordinate]:
    queue: deque[Coordinate] = deque([source])
    parents: dict[Coordinate, Coordinate | None] = {source: None}
    while queue:
        current = queue.popleft()
        if current == target:
            break
        for nxt in maze.neighbors(current):
            if nxt not in parents:
                parents[nxt] = current
                queue.append(nxt)
    return reconstruct_path(parents, target)


def manhattan(a: Coordinate, b: Coordinate) -> int:
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def astar(maze: Maze, source: Coordinate, target: Coordinate) -> list[Coordinate]:
    queue: list[tuple[int, int, Coordinate]] = [(0, 0, source)]
    parents: dict[Coordinate, Coordinate | None] = {source: None}
    distance: dict[Coordinate, int] = {source: 0}
    counter = 0

    while queue:
        _, _, current = heapq.heappop(queue)
        if current == target:
            break
        for nxt in maze.neighbors(current):
            new_cost = distance[current] + 1
            if nxt not in distance or new_cost < distance[nxt]:
                distance[nxt] = new_cost
                counter += 1
                priority = new_cost + manhattan(nxt, target)
                heapq.heappush(queue, (priority, counter, nxt))
                parents[nxt] = current
    return reconstruct_path(parents, target)


def draw_path(maze: Maze, path_to_key: list[Coordinate], path_to_exit: list[Coordinate]) -> list[str]:
    rendered = [row.copy() for row in maze.grid]
    for r, c in path_to_key:
        if (r, c) not in {maze.start, maze.key, maze.exit}:
            rendered[r][c] = '*'
    for r, c in path_to_exit:
        if (r, c) not in {maze.start, maze.key, maze.exit}:
            rendered[r][c] = ','
    sr, sc = maze.start
    kr, kc = maze.key
    er, ec = maze.exit
    rendered[sr][sc] = 'A'
    rendered[kr][kc] = 'K'
    rendered[er][ec] = 'E'
    return [''.join(row) for row in rendered]


def solve(maze: Maze) -> tuple[list[Coordinate], list[Coordinate], list[str]]:
    path_to_key = bfs(maze, maze.start, maze.key)
    if not path_to_key:
        raise ValueError('Path from start to key was not found')
    path_to_exit = astar(maze, maze.key, maze.exit)
    if not path_to_exit:
        raise ValueError('Path from key to exit was not found')
    return path_to_key, path_to_exit, draw_path(maze, path_to_key, path_to_exit)


def parse_coord(value: str) -> Coordinate:
    row, col = value.split(',')
    return int(row), int(col)


def main() -> None:
    parser = argparse.ArgumentParser(description='Solve a maze: BFS to key and A* to exit')
    parser.add_argument('--maze', type=Path, default=Path('data/sample_maze.txt'))
    parser.add_argument('--start', type=parse_coord, default=None, help='row,col; optional if A exists in file')
    parser.add_argument('--key', type=parse_coord, default=None, help='row,col; optional if K exists in file')
    parser.add_argument('--exit', type=parse_coord, default=None, help='row,col; optional if E exists in file')
    parser.add_argument('--output', type=Path, default=Path('outputs/maze-solved.txt'))
    args = parser.parse_args()

    maze = read_maze(args.maze, args.start, args.key, args.exit)
    path_to_key, path_to_exit, rendered = solve(maze)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text('\n'.join(rendered), encoding='utf-8')
    print(f'Path to key: {len(path_to_key)} cells')
    print(f'Path to exit: {len(path_to_exit)} cells')
    print(f'Result written to {args.output}')


if __name__ == '__main__':
    main()
