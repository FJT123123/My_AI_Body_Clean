import os

with open("openclaw_continuity.py", "r", encoding="utf-8") as f:
    lines = f.readlines()

blocks = []
blocks.append(lines[3349-1:3390]) # RuntimeState
blocks.append(lines[661-1:744])   # EvolutionRoadmap
blocks.append(lines[440-1:599])   # EvolutionMetrics
blocks.append(lines[348-1:429])   # EmotionalState

del lines[3349-1:3390]
del lines[661-1:744]
del lines[440-1:599]
del lines[348-1:429]

header = """import os
import json
import sqlite3
import threading
import time
from datetime import datetime
import math
from typing import Dict, Any, List, Optional

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
WORKSPACE_DIR = os.path.join(ROOT_DIR, "workspace")
DB_PATH = os.path.join(WORKSPACE_DIR, "v3_episodic_memory.db")
ROADMAP_FILE = os.path.join(WORKSPACE_DIR, "evolution_roadmap.json")

"""

with open("workspace/core_components/cognitive_state.py", "w", encoding="utf-8") as f:
    f.write(header)
    f.writelines(blocks[3])
    f.write("\n\n")
    f.writelines(blocks[2])
    f.write("\n\n")
    f.writelines(blocks[1])
    f.write("\n\n")
    f.writelines(blocks[0])

for i, line in enumerate(lines):
    if line.startswith("import workspace.core_components.tool_engine as tool_engine"):
        lines.insert(i+1, "from workspace.core_components.cognitive_state import EmotionalState, EvolutionMetrics, EvolutionRoadmap, RuntimeState\n")
        break

with open("openclaw_continuity.py", "w", encoding="utf-8") as f:
    f.writelines(lines)
