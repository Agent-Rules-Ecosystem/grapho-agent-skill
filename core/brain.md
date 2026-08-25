# 🧠 Brain Engine — Grapho Decision Matrix

## 1. Detección de Violaciones Clean Architecture

```text
¿El módulo escaneado pertenece a la capa Domain?
└── SÍ ==> Verificación de Imports:
           ├── Importa `data/`         ==> VIOLACIÓN GRAVE (CLEAN_ARCH_VIOLATION).
           ├── Importa `presentation/` ==> VIOLACIÓN CRÍTICA (CLEAN_ARCH_VIOLATION).
           └── Importa `domain/`       ==> VÁLIDO.
```

---

## 2. Clasificación de Archivos por Tamaño

- **< 150 líneas**: Tamaño óptimo.
- **150 a 300 líneas**: Tamaño aceptable.
- **> 300 líneas**: Archivo Monolítico (`WARNING_MONOLITH`). Requiere refactorización.
