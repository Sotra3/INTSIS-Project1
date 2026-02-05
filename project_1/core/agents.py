from __future__ import annotations

import random
from dataclasses import dataclass
from typing import Callable

from core.grid import Grid
from core.path import Path


@dataclass(slots=True)
class Agent:
    name: str

    def find_path(self, grid: Grid, start: tuple[int, int], goal: tuple[int, int]) -> Path:
        raise NotImplementedError


class ExampleAgent(Agent):


    def __init__(self):
        super().__init__("Example")

    def find_path(self, grid: Grid, start: tuple[int, int], goal: tuple[int, int]) -> Path:
        nodes = [start]
        while nodes[-1] != goal:
            r, c = nodes[-1]
            neighbors = grid.neighbors4(r, c)

            min_dist = min(grid.manhattan(t.pos, goal) for t in neighbors)
            best_tiles = [
                tile for tile in neighbors
                if grid.manhattan(tile.pos, goal) == min_dist
            ]
            best_tile = best_tiles[random.randint(0, len(best_tiles) - 1)]

            nodes.append(best_tile.pos)

        return Path(nodes)


class DFSAgent(Agent):

    def __init__(self):
        super().__init__("DFS")

    def find_path(self, grid: Grid, start: tuple[int, int], goal: tuple[int, int]) -> Path:
        nodes = [start]
        visited = {start}
        directions = {(0, 1): 0, (1, 0): 1, (0, -1): 2, (-1, 0): 3}

        while nodes and nodes[-1] != goal:
            r, c = nodes[-1]
            neighbors = grid.neighbors4(r, c)

            neighbors_sorted = sorted(
                [tile for tile in neighbors if tile.pos not in visited],
                key=lambda t: (t.cost, directions[(t.pos[0] - r, t.pos[1] - c)])
            )

            if not neighbors_sorted:
                nodes.pop()
                continue

            best_tile = neighbors_sorted[0]
            nodes.append(best_tile.pos)
            visited.add(best_tile.pos)

        return Path(nodes)

class BranchAndBoundAgent(Agent):

    def __init__(self):
        super().__init__("BranchAndBound")

    def find_path(self, grid: Grid, start: tuple[int, int], goal: tuple[int, int]) -> Path:
        r, c = start
        nodes = [{"path": [start], "cost": grid.get(r, c).cost}]


        while nodes:
            best = min(nodes, key=lambda p: (p["cost"], len(p["path"])))
            nodes.remove(best)

            current = best["path"][-1]
            if current == goal:
                return Path(best["path"])

            r, c = current
            for neighbor in grid.neighbors4(r, c):
                if neighbor.pos not in best["path"]:
                    new_path = best["path"] + [neighbor.pos]
                    new_cost = best["cost"] + neighbor.cost
                    nodes.append({"path": new_path, "cost": new_cost})

        return Path([])


class AStar(Agent):

    def __init__(self):
        super().__init__("AStar")

    def find_path(self, grid: Grid, start: tuple[int, int], goal: tuple[int, int]) -> Path:
        r, c = start
        nodes = [{"path": [start], "gcost":grid.get(r,c).cost, "hcost": grid.manhattan(start, goal)}]

        while nodes:
            best = min(nodes, key=lambda p: (p["gcost"] + p["hcost"], len(p["path"])))
            nodes.remove(best)
            current = best["path"][-1]
            if current == goal:
                return Path(best["path"])

            r, c = current
            for neighbor in grid.neighbors4(r, c):
                if neighbor.pos not in best["path"]:
                    new_path = best["path"] + [neighbor.pos]
                    new_cost_g= best["gcost"] + neighbor.cost
                    new_cost_h=grid.manhattan(neighbor.pos, goal)
                    nodes.append({"path": new_path, "gcost": new_cost_g, "hcost": new_cost_h})

        return Path([])


AGENTS: dict[str, Callable[[], Agent]] = {
    "Example": ExampleAgent,
    "DFS": DFSAgent,
    "BranchAndBound": BranchAndBoundAgent,
    "AStar": AStar
}


def create_agent(name: str) -> Agent:
    if name not in AGENTS:
        raise ValueError(f"Unknown agent '{name}'. Available: {', '.join(AGENTS.keys())}")
    return AGENTS[name]()
