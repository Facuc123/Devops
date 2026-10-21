#!/usr/bin/env bash
# Genera tráfico contra la API para que el dashboard de Golden Signals tenga datos.
#
# Mezcla requests exitosos (2xx), errores de cliente (4xx) y, opcionalmente,
# errores de servidor (5xx) con /chaos/boom. Solo usa curl: no hay que instalar nada.
#
# Uso:
#   ./scripts/generar_trafico.sh                     # 2 minutos contra localhost:8000
#   DURACION=300 ./scripts/generar_trafico.sh        # 5 minutos
#   CAOS=1 ./scripts/generar_trafico.sh              # suma 5xx (requiere CHAOS_ENABLED=true en la API)
#   URL=https://mi-app.onrender.com ./scripts/generar_trafico.sh

set -euo pipefail

URL="${URL:-http://localhost:8000}"
DURACION="${DURACION:-120}"     # segundos
CONCURRENCIA="${CONCURRENCIA:-5}"
CAOS="${CAOS:-0}"

curl -fs "$URL/health" > /dev/null || {
  echo "La API no responde en $URL/health. ¿Está levantada (docker compose up -d)?" >&2
  exit 1
}

# Un incidente viejo para que /status y /incidentes/{id} tengan datos reales.
ID=$(curl -fs -X POST "$URL/incidentes" -H "Content-Type: application/json" \
  -d '{"titulo":"Incidente de prueba de carga","severidad":"SEV3","descripcion":"Generado por generar_trafico.sh","ocurrido_en":"2026-10-01T12:00:00Z"}' \
  | sed -E 's/.*"id":"([^"]+)".*/\1/')

pedir() {
  local metodo="$1" ruta="$2"
  curl -s -o /dev/null -w "%{http_code}\n" -X "$metodo" "$URL$ruta"
}

trabajador() {
  local fin=$((SECONDS + DURACION))
  while [ "$SECONDS" -lt "$fin" ]; do
    local r=$((RANDOM % 100))
    if   [ "$r" -lt 35 ]; then pedir GET /status
    elif [ "$r" -lt 60 ]; then pedir GET /incidentes
    elif [ "$r" -lt 75 ]; then pedir GET "/incidentes/$ID"
    elif [ "$r" -lt 85 ]; then pedir GET /health
    elif [ "$r" -lt 92 ]; then pedir GET "/incidentes/00000000-0000-0000-0000-000000000000"  # 404
    elif [ "$r" -lt 96 ]; then pedir GET /no-existe                                          # 404
    elif [ "$CAOS" = "1" ]; then pedir POST /chaos/boom                                      # 500
    else pedir GET /status
    fi
    sleep 0.$((RANDOM % 3))
  done
}

echo "Generando tráfico contra $URL durante ${DURACION}s con $CONCURRENCIA trabajadores (caos=$CAOS)..."

for _ in $(seq "$CONCURRENCIA"); do
  trabajador &
done | sort | uniq -c | awk '{printf "  HTTP %s: %s requests\n", $2, $1}'

wait
