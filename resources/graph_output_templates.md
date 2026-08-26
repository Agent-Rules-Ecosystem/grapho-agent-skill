# 🛠️ Graph Output JSON Schema

Estructura canónica del archivo `overview/grapho/grapho_data.json`:

```json
{
  "project_name": "MyProject",
  "generated_at": "2026-08-25T00:00:00Z",
  "metrics": {
    "total_files": 45,
    "total_lines": 4250,
    "monolith_count": 2,
    "violations_count": 0,
    "high_coupling_count": 1
  },
  "nodes": [
    {
      "id": "lib/domain/usecases/get_user.dart",
      "label": "GetUserUseCase",
      "layer": "domain",
      "lines": 45,
      "is_monolith": false,
      "fan_in": 3,
      "fan_out": 2,
      "is_high_coupling": false
    }
  ],
  "edges": [
    {
      "from": "lib/presentation/pages/user_page.dart",
      "to": "lib/domain/usecases/get_user.dart",
      "type": "import"
    }
  ]
}
```
