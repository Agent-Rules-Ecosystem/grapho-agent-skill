# 🕸️ Grapho Agent Skill

> **Skill Transversal de Análisis Determinista de Grafos de Código y Arquitectura**  
> Proporciona motores de escaneo ultrarrápidos (< 1s) para extraer el árbol de dependencias, validar capas Clean Architecture y exportar datos para diagramas Mermaid y el visualizador `grapho-3d-visualizer-agent-skill`.

---

## 📌 Propósito y Alcance

1. ⚡ **Velocidad Determinista (< 1s)**: Analizar la estructura y grafo del código sin que la IA tenga que leer individualmente miles de archivos.
2. 📉 **Ahorro Masivo de Tokens (~80-90%)**: Reducir el consumo de tokens en tareas de exploración de dependencias de 50k tokens a menos de 1k tokens.
3. 🎯 **Cero Alucinaciones**: Extracción 100% exacta del mapa de imports, clases y módulos vía AST/Regex.
4. 🚨 **Auditoría de Limite de Líneas & Clean Arch**: Detectar archivos monolíticos (>300 líneas) y violaciones de capas arquitectónicas.

---

## ⚡ $-Comandos de Grapho

| Comando | Acción | Descripción |
|---|---|---|
| `$grapho` | Bootstrap | Activa la skill, ejecuta el escáner del lenguaje activo y genera `grapho_data.json`, `architecture.mmd` y `radar.md`. |
| `$grapho:radar` | AST Radar | Genera el índice sintético `overview/grapho/radar.md` para localización rápida de archivos durante `$work`. |
| `$grapho:scan` | Escaneo AST | Ejecuta el escáner AST correspondiente y actualiza `overview/grapho/grapho_data.json`. |
| `$grapho:audit` | Auditoría | Evalúa violaciones Clean Arch, monolitos y acoplamiento en `overview/work/skill/grapho.md`. |
| `$grapho:mermaid` | Exportar Diagrama | Convierte el grafo de dependencias a un diagrama Mermaid (`overview/grapho/architecture.mmd`). |
| `$grapho:json` | Exportar JSON | Escribe el JSON estructurado en `overview/grapho/grapho_data.json` para ser consumido por `$grapho3d`. |

---

## ⚡ Quick Start

**1. Instala la skill como submódulo**
```bash
git submodule add git@github.com:Agent-Rules-Ecosystem/grapho-agent-skill.git .skill/grapho-agent-skill
```

**2. Activa la skill con `$boot`**
```text
$boot
```

**3. Ejecuta el primer comando de la skill**
```text
$grapho:audit
```

---

