from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parents[1] / 'src'))
from maze_pathfinding import read_maze, solve


def test_sample_maze_has_solution():
    maze = read_maze(Path(__file__).resolve().parents[1] / 'data' / 'sample_maze.txt')
    path_to_key, path_to_exit, rendered = solve(maze)
    assert len(path_to_key) > 1
    assert len(path_to_exit) > 1
    assert any('K' in row for row in rendered)
    assert any('E' in row for row in rendered)
