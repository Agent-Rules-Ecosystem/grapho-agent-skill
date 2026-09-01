#!/usr/bin/env python3
"""
export_radar.py — Converts overview/grapho/grapho_data.json into a lightweight markdown Radar index (overview/grapho/radar.md).
Designed for fast file path lookup during $work tasks before promoting to overview/architecture/.
"""

import os
import sys
import json
from datetime import datetime

def json_to_radar(json_path):
    if not os.path.exists(json_path):
        print(f"❌ Error: {json_path} not found. Run scan script first.")
        sys.exit(1)

    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    nodes = data.get('nodes', [])
    metrics = data.get('metrics', {})
    stack = data.get('stack', 'desconocido').capitalize()

    lines = [
        "# 🕸️ Grapho AST Radar Index",
        "",
        f"> **Generado**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} · **Stack**: {stack}",
        "> **Prioridad**: Telemetría Derivada (Prioridad 2 — Radiografía AST)",
        "> **Propósito**: Navegación rápida para localizar archivos no documentados en `overview/architecture/` durante tareas en `$work`.",
        "",
        "## 📊 Métricas Rápidas",
        f"- **Archivos escaneados**: {metrics.get('total_files', len(nodes))}",
        f"- **Líneas totales**: {metrics.get('total_lines', 0)}",
        f"- **Monolitos (>300L)**: {metrics.get('monolith_count', 0)}",
        f"- **Violaciones Clean Arch**: {metrics.get('violations_count', 0)}",
        f"- **Alto acoplamiento**: {metrics.get('high_coupling_count', 0)}",
        "",
        "## 📍 Índices de Archivos y Componentes",
        "",
        "| Componente | Capa | Ruta Relativa | Líneas | Monolito | Fan-In / Fan-Out |",
        "|---|---|---|---|---|---|"
    ]

    for n in sorted(nodes, key=lambda x: x.get('id', '')):
        label = n.get('label', '')
        layer = n.get('layer', 'other')
        rel_path = f"`{n.get('id', '')}`"
        line_count = f"{n.get('lines', 0)}L"
        monolith = "🚨 SÍ" if n.get('is_monolith') else "❌"
        fan_in = n.get('fan_in', 0)
        fan_out = n.get('fan_out', 0)
        coupling = f"{fan_in} / {fan_out}"

        lines.append(f"| `{label}` | {layer} | {rel_path} | {line_count} | {monolith} | {coupling} |")

    lines.append("")
    lines.append("---")
    lines.append("💡 *Una vez localizado y verificado el archivo durante `$work`, documenta la estructura confirmada en `overview/architecture/modules/<modulo>.md`.*")

    output_dir = os.path.dirname(json_path)
    output_file = os.path.join(output_dir, 'radar.md')

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("\n".join(lines))

    print(f"✅ [Grapho Engine] AST Radar Index saved to {output_file}")

if __name__ == '__main__':
    target_json = sys.argv[1] if len(sys.argv) > 1 else 'overview/grapho/grapho_data.json'
    json_to_radar(target_json)
