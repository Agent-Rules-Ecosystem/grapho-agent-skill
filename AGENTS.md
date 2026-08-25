---
name: grapho-agent-skill
type: runner-tooling
description: Deterministic code graph engine, AST analysis, and Clean Architecture layer parser.
---

# 🕸️ Grapho Agent Skill Directive

## Bootstrap de la Habilidad

Cuando se invoque el comando `$grapho` o cualquier subcomando (`$grapho:audit`, `$grapho:scan`, `$grapho:mermaid`), el agente **DEBE** cargar los siguientes archivos en orden:

1. `SKILL.md` ← Matriz de capacidades, diagnósticos y directiva de invocación de scripts.
2. `core/commands.md` ← Registro de $-comandos expuestos.
3. `core/brain.md` ← Reglas de triaje de dependencias y límites de líneas por archivo.
4. `core/path_map.md` ← Ubicación de los analizadores ejecutables `.py` y salida en `overview/grapho/`.

---

## Reglas Canónicas de Análisis de Grafos

1. **Ejecución Determinista Vía Script Python (< 1s)**:
   * El agente **NUNCA** debe leer manualmente 20+ archivos para construir el árbol de dependencias si puede ejecutar el script correspondiente (`python3 .skill/grapho-agent-skill/scripts/scan_*.py .`).
   * Toda extracción de mapa de código debe apoyarse en la salida procesada del script.

2. **Persistencia en `overview/grapho/`**:
   * Los resultados del análisis técnico se escribirán obligatoriamente en `overview/grapho/grapho_data.json` y `overview/work/skill/grapho.md`.

3. **Detección de Monolitos (>300 líneas)**:
   * Todo archivo fuente que supere las 300 líneas de código debe marcarse automáticamente como alerta de refactorización (`WARNING_MONOLITH`).

4. **Verificación de Regla de Dependencia Clean Architecture**:
   * Las capas superiores (`domain`) **nunca** deben importar capas inferiores (`data` o `presentation`).
   * Toda violación debe ser reportada como `CLEAN_ARCH_VIOLATION`.
