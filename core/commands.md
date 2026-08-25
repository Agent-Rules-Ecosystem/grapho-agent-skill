# 🕸️ Registro de $-Comandos de Grapho

## Comandos de Análisis

- `$grapho`: Detecta la tecnología del proyecto y ejecuta el escáner AST correspondiente.
- `$grapho:audit`: Evalúa violaciones de Clean Arch y detecta archivos monolíticos (>300 líneas). Registra la salida en `overview/work/skill/grapho.md`.
- `$grapho:mermaid`: Genera o actualiza el diagrama Mermaid en `overview/grapho/architecture.mmd`.
- `$grapho:json`: Exporta el JSON estructurado completo a `overview/grapho/grapho_data.json` para ser consumido por visualizadores.

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
