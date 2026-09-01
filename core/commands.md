# 🕸️ Registro de $-Comandos de Grapho

## Comandos de Análisis

- `$grapho`: Auto-detecta el stack del proyecto (Dart > TS/Web > Python), ejecuta el escáner AST y genera automáticamente `grapho_data.json`, `architecture.mmd` y `overview/grapho/radar.md`.
- `$grapho:radar`: Genera/actualiza únicamente el índice sintético `overview/grapho/radar.md` para localización rápida de archivos no documentados durante tareas en `$work`.
- `$grapho:scan`: Alias explícito para forzar el escaneo AST completo del repositorio y actualizar `overview/grapho/grapho_data.json`.
- `$grapho:audit`: Evalúa violaciones de Clean Arch, detecta archivos monolíticos (>300 líneas) y alertas de acoplamiento. Registra la salida en `overview/work/skill/grapho.md`.
- `$grapho:mermaid`: Genera o actualiza el diagrama Mermaid en `overview/grapho/architecture.mmd`.
- `$grapho:json`: Exporta o verifica el JSON estructurado completo en `overview/grapho/grapho_data.json` para ser consumido por visualizadores 3D.

## Comandos de Aprendizaje y Evolución

- `$learngrapho "<descripción>"`: Registra una mejora candidata en `overview/learning.md` del proyecto, **marcada con el tag `[grapho-agent-skill]`**, para ser promovida al repositorio oficial de la skill. Incluir: qué mejorar, por qué y en qué archivo de la skill aplica.
- `$revlearngrapho`: Revisa todas las entradas `[grapho-agent-skill]` pendientes en `overview/learning.md` y propone cuáles están listas para ser aplicadas en el repositorio oficial de `grapho-agent-skill`.

### Formato de entrada en `overview/learning.md`

```markdown
### [grapho-agent-skill] <título del aprendizaje>

- **Fecha**: YYYY-MM-DD
- **Skill**: `grapho-agent-skill`
- **Descripción**: <Qué mejorar y por qué>
- **Archivo objetivo en la skill**: `scripts/scan_flutter.py` (ejemplo)
- **Estado**: `PENDIENTE` | `APLICADO`
```

> Para aplicar mejoras al repositorio oficial, usar `$revlearngrapho` y luego hacer PR en `github.com/Agent-Rules-Ecosystem/grapho-agent-skill`.
