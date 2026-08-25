# 🏰 Clean Architecture Graph Rules

## Grafo de Dependencias Permitido

```text
Presentation Layer ---> Domain Layer <--- Data Layer
      |                                      |
      v                                      v
  (UI/Bloc)                             (DB/API/HTTP)
```

1. **Domain Layer**: Libre de dependencias externas o de UI/Data.
2. **Presentation Layer**: Depende únicamente de `Domain` (Casos de Uso / Entidades).
3. **Data Layer**: Implementa las interfaces definidas en `Domain`.
