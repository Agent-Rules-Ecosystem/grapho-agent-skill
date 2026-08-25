#!/usr/bin/env python3
"""
export_mermaid.py — Converts overview/grapho/grapho_data.json into a clean Mermaid diagram (`overview/grapho/architecture.mmd`).
"""

import os
import sys
import json

def json_to_mermaid(json_path):
    if not os.path.exists(json_path):
        print(f"❌ Error: {json_path} not found. Run scan script first.")
        sys.exit(1)

    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    nodes = data.get('nodes', [])
    edges = data.get('edges', [])

    mermaid_lines = ["graph LR"]

    # Group by layers
    layers = {}
    for node in nodes:
        layer = node.get('layer', 'other')
        if layer not in layers:
            layers[layer] = []
        layers[layer].append(node)

    for layer, layer_nodes in layers.items():
        layer_title = layer.capitalize()
        mermaid_lines.append(f"    subgraph {layer_title}")
        for n in layer_nodes:
            node_id = n['id'].replace('/', '_').replace('.', '_').replace('-', '_')
            label = n['label']
            if n.get('is_monolith'):
                label += " 🚨(>300L)"
            mermaid_lines.append(f'        {node_id}["{label}"]')
        mermaid_lines.append("    end")

    # Add edges (limit max 30 edges for readability)
    for edge in edges[:30]:
        src = edge['from'].replace('/', '_').replace('.', '_').replace('-', '_')
        dst = edge['to'].replace('/', '_').replace('.', '_').replace('-', '_')
        mermaid_lines.append(f"    {src} --> {dst}")

    output_dir = os.path.dirname(json_path)
    output_file = os.path.join(output_dir, 'architecture.mmd')

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("\n".join(mermaid_lines))

    print(f"✅ [Grapho Engine] Mermaid diagram saved to {output_file}")

if __name__ == '__main__':
    target_json = sys.argv[1] if len(sys.argv) > 1 else 'overview/grapho/grapho_data.json'
    json_to_mermaid(target_json)
