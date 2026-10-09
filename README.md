# Devops
Trabajo práctico Devops - Universidad de Palermo - Integrantes: Facundo Canto y Luciano Sicolo
## Estrategia de versionado

El proyecto utiliza Versionado Semántico (SemVer), siguiendo el formato
`MAJOR.MINOR.PATCH`:

- `MAJOR`: cambios incompatibles con versiones anteriores.
- `MINOR`: nuevas funcionalidades compatibles.
- `PATCH`: correcciones de errores compatibles.

Elegimos SemVer porque permite identificar claramente el impacto de cada
versión. Un SHA identifica un commit, pero no comunica el tipo de cambio
realizado. El versionado basado en fechas indica cuándo se publicó una versión,
pero tampoco permite saber si contiene una corrección, una funcionalidad nueva
o un cambio incompatible.