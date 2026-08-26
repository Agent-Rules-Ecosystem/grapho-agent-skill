#!/usr/bin/env python3
"""
scan_python.py — Native AST scanner for Python projects using the `ast` module.
Extracts module imports, line counts, monoliths (>300 lines) and writes JSON to overview/grapho/grapho_data.json
"""

import os
import ast
import sys
import json
from datetime import datetime

def classify_python_layer(rel_path):
    path_lower = rel_path.lower()
    if 'domain' in path_lower or 'models' in path_lower or 'schemas' in path_lower:
        return 'domain'
    elif 'data' in path_lower or 'db' in path_lower or 'repositories' in path_lower or 'services' in path_lower:
        return 'data'
    elif 'api' in path_lower or 'routers' in path_lower or 'views' in path_lower or 'controllers' in path_lower:
        return 'presentation'
    elif 'core' in path_lower or 'config' in path_lower or 'utils' in path_lower:
        return 'core'
    elif rel_path.endswith('main.py') or rel_path.endswith('app.py'):
        return 'root'
    return 'other'

def scan_python_project(target_dir='.'):
    nodes = []
    edges = []
    monolith_count = 0
    violations_count = 0
    total_lines = 0

    for root, _, files in os.walk(target_dir):
        if 'venv' in root or '.venv' in root or '.git' in root or '__pycache__' in root:
            continue

        for file in files:
            if file.endswith('.py'):
                full_path = os.path.join(root, file)
                rel_path = os.path.relpath(full_path, target_dir)

                with open(full_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()

                lines = content.splitlines()
                line_count = len(lines)
                total_lines += line_count
                is_monolith = line_count > 300
                if is_monolith:
                    monolith_count += 1

                layer = classify_python_layer(rel_path)
                node_id = rel_path.replace('\\', '/')

                nodes.append({
                    "id": node_id,
                    "label": os.path.basename(file),
                    "layer": layer,
                    "lines": line_count,
                    "is_monolith": is_monolith
                })

                # Parse AST imports
                try:
                    tree = ast.parse(content, filename=full_path)
                    for node in ast.walk(tree):
                        if isinstance(node, ast.Import):
                            for alias in node.names:
                                edges.append({"from": node_id, "to": alias.name, "type": "import"})
                        elif isinstance(node, ast.ImportFrom):
                            if node.module:
                                edges.append({"from": node_id, "to": node.module, "type": "import"})
                except Exception:
                    pass

    # Calculate coupling metrics (fan_in and fan_out)
    fan_in_map = {n['id']: 0 for n in nodes}
    fan_out_map = {n['id']: 0 for n in nodes}

    for e in edges:
        from_id = e['from']
        to_id = e['to']
        if from_id in fan_out_map:
            fan_out_map[from_id] += 1
        if to_id in fan_in_map:
            fan_in_map[to_id] += 1

    high_coupling_count = 0
    for node in nodes:
        node_id = node['id']
        f_in = fan_in_map.get(node_id, 0)
        f_out = fan_out_map.get(node_id, 0)
        node['fan_in'] = f_in
        node['fan_out'] = f_out
        is_high_coupling = f_out > 10 or f_in > 15
        node['is_high_coupling'] = is_high_coupling
        if is_high_coupling:
            high_coupling_count += 1

    graph_data = {
        "project_name": os.path.basename(os.path.abspath(target_dir)),
        "stack": "python",
        "generated_at": datetime.now().isoformat() + "Z",
        "metrics": {
            "total_files": len(nodes),
            "total_lines": total_lines,
            "monolith_count": monolith_count,
            "violations_count": violations_count,
            "high_coupling_count": high_coupling_count
        },
        "nodes": nodes,
        "edges": edges
    }

    output_dir = os.path.join(target_dir, 'overview', 'grapho')
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, 'grapho_data.json')

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(graph_data, f, indent=2)

    print(f"✅ [Grapho Engine] Python AST Scan complete! Scanned {len(nodes)} files ({total_lines} lines). JSON saved to {output_path}")
    return graph_data

if __name__ == '__main__':
    target = sys.argv[1] if len(sys.argv) > 1 else '.'
    scan_python_project(target)
