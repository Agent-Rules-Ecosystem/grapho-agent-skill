#!/usr/bin/env python3
"""
scan_auto.py — Auto-detects the project stack and runs the appropriate scanner.
Detection priority: Flutter/Dart > TypeScript/Web > Python
Writes output to overview/grapho/grapho_data.json
"""

import os
import sys
import subprocess

def detect_stack(target_dir='.'):
    """Walk the project and count file extensions to determine the dominant stack."""
    counts = {'dart': 0, 'ts': 0, 'tsx': 0, 'svelte': 0, 'jsx': 0, 'js': 0, 'py': 0}

    for root, dirs, files in os.walk(target_dir):
        # Exclude noise directories
        dirs[:] = [d for d in dirs if d not in (
            'node_modules', '.next', 'dist', 'build', '.git',
            '__pycache__', 'venv', '.venv', '.dart_tool', 'build'
        )]
        for f in files:
            ext = f.rsplit('.', 1)[-1].lower()
            if ext in counts:
                counts[ext] += 1

    dart_total = counts['dart']
    web_total = counts['ts'] + counts['tsx'] + counts['svelte'] + counts['jsx'] + counts['js']
    python_total = counts['py']

    print(f"🔍 [Grapho Auto-Detect] Archivos encontrados → Dart: {dart_total} | Web/TS: {web_total} | Python: {python_total}")

    if dart_total >= web_total and dart_total >= python_total:
        return 'flutter'
    elif web_total >= python_total:
        return 'typescript'
    else:
        return 'python'

def run_scanner(stack, target_dir):
    skill_dir = os.path.dirname(os.path.abspath(__file__))

    scanner_map = {
        'flutter':    os.path.join(skill_dir, 'scan_flutter.py'),
        'typescript': os.path.join(skill_dir, 'scan_typescript.py'),
        'python':     os.path.join(skill_dir, 'scan_python.py'),
    }

    scanner = scanner_map.get(stack)
    if not scanner or not os.path.exists(scanner):
        print(f"❌ Scanner no encontrado para stack: {stack}")
        sys.exit(1)

    stack_labels = {
        'flutter': '📱 Flutter / Dart',
        'typescript': '🌐 Web / TypeScript',
        'python': '🐍 Python',
    }
    print(f"⚡ [Grapho Auto-Detect] Stack detectado: {stack_labels[stack]}")
    print(f"▶  Ejecutando: {os.path.basename(scanner)} {target_dir}\n")

    result = subprocess.run([sys.executable, scanner, target_dir])
    sys.exit(result.returncode)

if __name__ == '__main__':
    target = sys.argv[1] if len(sys.argv) > 1 else '.'
    stack = detect_stack(target)
    run_scanner(stack, target)
