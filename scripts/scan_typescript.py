#!/usr/bin/env python3
"""
scan_typescript.py — Regex import scanner for TypeScript/JavaScript/Web projects.
Extracts component layers, line counts, monoliths (>300 lines) and writes JSON to overview/grapho/grapho_data.json
"""

import os
import re
import sys
import json
from datetime import datetime

def classify_web_layer(rel_path):
    path_lower = rel_path.lower()
    if 'domain' in path_lower or 'types' in path_lower or 'models' in path_lower:
        return 'domain'
    elif 'data' in path_lower or 'services' in path_lower or 'api' in path_lower or 'store' in path_lower:
        return 'data'
    elif 'components' in path_lower or 'routes' in path_lower or 'pages' in path_lower or 'views' in path_lower or 'ui' in path_lower:
        return 'presentation'
    elif 'core' in path_lower or 'utils' in path_lower or 'config' in path_lower:
        return 'core'
    elif rel_path.endswith('index.ts') or rel_path.endswith('main.ts') or rel_path.endswith('App.tsx') or rel_path.endswith('App.svelte'):
        return 'root'
    return 'other'

def scan_ts_project(target_dir='.'):
    nodes = []
    edges = []
    monolith_count = 0
    violations_count = 0
    total_lines = 0

    import_regex = re.compile(r"import\s+.*?from\s+['\"]([^'\"]+)['\"]")

    for root, _, files in os.walk(target_dir):
        if 'node_modules' in root or '.next' in root or 'dist' in root or '.git' in root:
            continue

        for file in files:
            if file.endswith(('.ts', '.tsx', '.js', '.jsx', '.svelte')):
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

                layer = classify_web_layer(rel_path)
                node_id = rel_path.replace('\\', '/')

                nodes.append({
                    "id": node_id,
                    "label": os.path.basename(file),
                    "layer": layer,
                    "lines": line_count,
                    "is_monolith": is_monolith
                })

                imports = import_regex.findall(content)
                for imp in imports:
                    if not imp.startswith('.'):
                        continue
                    edges.append({"from": node_id, "to": imp, "type": "import"})

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
        "stack": "typescript",
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

    print(f"✅ [Grapho Engine] Web/TS Scan complete! Scanned {len(nodes)} files ({total_lines} lines). JSON saved to {output_path}")
    return graph_data

if __name__ == '__main__':
    target = sys.argv[1] if len(sys.argv) > 1 else '.'
    scan_ts_project(target)
