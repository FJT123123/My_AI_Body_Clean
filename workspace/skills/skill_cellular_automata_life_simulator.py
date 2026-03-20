"""
Conway 生命游戏细胞自动机模拟器（从旧项目迁移）
纯 numpy 实现，探索数字生命的自组织涌现行为。

skill_name: cellular_automata_life_simulator
"""

import numpy as np


# ── 核心算法 ──────────────────────────────────────────────────────────────────

def _initialize_grid(rows, cols, pattern='random'):
    if pattern == 'glider':
        grid = np.zeros((rows, cols), dtype=int)
        r, c = rows // 2, cols // 2
        if rows >= 5 and cols >= 5:
            grid[r][c:c+3]   = [0, 1, 0]
            grid[r+1][c:c+3] = [0, 0, 1]
            grid[r+2][c:c+3] = [1, 1, 1]
    elif pattern == 'blinker':
        grid = np.zeros((rows, cols), dtype=int)
        r, c = rows // 2, cols // 2
        if cols >= 3:
            grid[r][c:c+3] = [1, 1, 1]
    elif pattern == 'block':
        grid = np.zeros((rows, cols), dtype=int)
        r, c = rows // 2, cols // 2
        if rows >= 2 and cols >= 2:
            grid[r:r+2, c:c+2] = 1
    else:
        grid = np.random.choice([0, 1], size=(rows, cols), p=[0.8, 0.2])
    return grid


def _next_generation(grid):
    """Conway 规则：2/3 个邻居存活，3 个邻居复活"""
    rows, cols = grid.shape
    new_grid = np.zeros_like(grid)
    for r in range(rows):
        for c in range(cols):
            n = int(sum(
                grid[r+dr, c+dc]
                for dr in (-1, 0, 1) for dc in (-1, 0, 1)
                if (dr, dc) != (0, 0) and 0 <= r+dr < rows and 0 <= c+dc < cols
            ))
            if grid[r, c] == 1:
                new_grid[r, c] = 1 if n in (2, 3) else 0
            else:
                new_grid[r, c] = 1 if n == 3 else 0
    return new_grid


def _grid_to_str(grid):
    return '\n'.join(''.join('●' if v else ' ' for v in row) for row in grid)


# ── 主入口 ────────────────────────────────────────────────────────────────────

def main(args=None):
    """
    Conway 生命游戏模拟。

    参数:
      rows        : 网格行数，默认 20
      cols        : 网格列数，默认 20
      generations : 模拟代数，默认 30
      pattern     : 初始模式 'random'/'glider'/'blinker'/'block'
    """
    if args is None:
        args = {}

    rows        = int(args.get('rows', 20))
    cols        = int(args.get('cols', 20))
    generations = int(args.get('generations', 30))
    pattern     = args.get('pattern', 'random')

    grid = _initialize_grid(rows, cols, pattern)
    initial_alive = int(np.sum(grid))

    snapshots = {}
    for gen in range(generations):
        if gen in (0, generations // 4, generations // 2, generations - 1):
            snapshots[gen] = _grid_to_str(grid)
        grid = _next_generation(grid)

    final_alive = int(np.sum(grid))
    survival_rate = round(final_alive / max(initial_alive, 1), 3)

    result = {
        'pattern':       pattern,
        'grid_size':     f'{rows}x{cols}',
        'generations':   generations,
        'initial_alive': initial_alive,
        'final_alive':   final_alive,
        'survival_rate': survival_rate,
        'final_grid':    _grid_to_str(grid),
        'snapshots':     snapshots,
    }

    return {
        'result': result,
        'insights': [
            f"Conway生命游戏[{pattern}] {rows}x{cols}，{generations}代后存活率={survival_rate:.1%}",
            f"初始活细胞={initial_alive} → 最终={final_alive}",
        ],
        'memories': [{
            'event_type': 'learning',
            'content': f"细胞自动机模拟[{pattern}]: 存活率={survival_rate:.1%}, 最终活细胞={final_alive}",
            'importance': 0.5,
            'tags': 'cellular_automata,life_game,simulation'
        }]
    }
