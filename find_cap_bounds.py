import ast
with open("openclaw_continuity.py", "r", encoding="utf-8") as f:
    code = f.read()

tree = ast.parse(code)
targets = [
    "_load_capability_module",
    "_get_capability_contract",
    "_verify_capability_with_sandbox",
    "_evaluate_capability_performance",
    "_diagnose_capability_usage",
    "_auto_load_patches",
    "_auto_restore_daemons"
]

bounds = []
for node in tree.body:
    if isinstance(node, ast.FunctionDef) and node.name in targets:
        start = node.lineno
        if node.decorator_list:
            start = min(d.lineno for d in node.decorator_list)
        bounds.append((start, node.end_lineno, node.name))

for t in sorted(bounds):
    print(t)
