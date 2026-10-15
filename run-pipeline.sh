#!/usr/bin/env bash
# Reproducible pipeline: isolated run -> JSON/PDF -> exact SVGs -> standalone HTML.
set -Eeuo pipefail

IMAGE="${IMAGE:-2path-terpenes-mod:latest}"
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd -P)"
RUNS_DIR="${RUNS_DIR:-$PROJECT_ROOT/runs}"
MODE="standard"
SIMULATION_SCRIPT="simulation.py"
SIMULATION_ITERATIONS=""
RUN_ID=""
MODE_EXPLICIT=""

usage() {
  cat >&2 <<'EOF'
Usage: bash run-pipeline.sh [--full | --smoke] [--run-id ID]

  --full       Run all rules for seven iterations.
  --smoke      Run a one-iteration standard simulation to verify the full
               Docker -> SVG -> HTML pipeline quickly.
  --run-id ID  Use a known identifier (must not already exist).

Each run is written to runs/<run-id>/, including logs/, status.json,
progress.json, out/, and report/. Follow a run with:
  tail -f runs/<run-id>/logs/pipeline.log

Environment: RUNS_DIR (output root), IMAGE (Docker image), MIN_FREE_GIB
(default: 6; smoke: 1), HEARTBEAT_SECONDS (default: 30).
EOF
}

while (( $# > 0 )); do
  case "$1" in
    --full)
      [[ -z "$MODE_EXPLICIT" || "$MODE_EXPLICIT" == "full" ]] || { usage; exit 2; }
      MODE_EXPLICIT="full"
      MODE="full"
      SIMULATION_SCRIPT="simulation-full.py"
      ;;
    --smoke)
      [[ -z "$MODE_EXPLICIT" || "$MODE_EXPLICIT" == "smoke" ]] || { usage; exit 2; }
      MODE_EXPLICIT="smoke"
      MODE="smoke"
      SIMULATION_SCRIPT="simulation.py"
      SIMULATION_ITERATIONS="1"
      ;;
    --run-id)
      shift
      [[ ${1:-} ]] || { usage; exit 2; }
      RUN_ID="$1"
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      usage
      exit 2
      ;;
  esac
  shift
done

[[ -f "$PROJECT_ROOT/$SIMULATION_SCRIPT" ]] || {
  echo "Simulation script not found: $SIMULATION_SCRIPT" >&2
  exit 1
}

if [[ -z "$RUN_ID" ]]; then
  RUN_ID="$(date -u +%Y%m%dT%H%M%SZ)-${MODE}"
fi
if [[ ! "$RUN_ID" =~ ^[A-Za-z0-9][A-Za-z0-9._-]*$ ]]; then
  echo "Invalid run ID: $RUN_ID" >&2
  exit 2
fi

command -v python3 >/dev/null || { echo "python3 is not available" >&2; exit 1; }
mkdir -p "$RUNS_DIR"
RUNS_DIR="$(cd "$RUNS_DIR" && pwd -P)"
RUN_DIR="$RUNS_DIR/$RUN_ID"
LOG_DIR="$RUN_DIR/logs"
STATUS_FILE="$RUN_DIR/status.json"
PROGRESS_FILE="$RUN_DIR/progress.json"
PIPELINE_LOG="$LOG_DIR/pipeline.log"
CURRENT_STAGE="initialization"
ACTIVE_STAGE_PID=""
PIPELINE_COMPLETED=0
FAILURE_MESSAGE=""

if [[ -e "$RUN_DIR" ]]; then
  echo "Run directory already exists: $RUN_DIR" >&2
  exit 2
fi
if ! mkdir "$RUN_DIR"; then
  echo "Could not reserve run directory: $RUN_DIR" >&2
  exit 2
fi

log() {
  local message="[$(date -u +%Y-%m-%dT%H:%M:%SZ)] $*"
  printf '%s\n' "$message" >> "$PIPELINE_LOG"
  printf '%s\n' "$message"
}

mark_failed() {
  local message="$1"
  python3 "$PROJECT_ROOT/pipeline_status.py" stage \
    --status-file "$STATUS_FILE" --name "$CURRENT_STAGE" --stage-status failed \
    --log "logs/${CURRENT_STAGE}.log" --message "$message" --exit-code "$2" || true
  python3 "$PROJECT_ROOT/pipeline_status.py" finish \
    --status-file "$STATUS_FILE" --run-status failed --message "$message" --exit-code "$2" || true
}

on_exit() {
  local code=$?
  trap - EXIT
  trap '' HUP INT TERM
  set +e
  if [[ -n "$ACTIVE_STAGE_PID" ]]; then
    kill -TERM "$ACTIVE_STAGE_PID" 2>/dev/null
    wait "$ACTIVE_STAGE_PID" 2>/dev/null
  fi
  if (( PIPELINE_COMPLETED == 0 )); then
    (( code != 0 )) || code=1
    local message="${FAILURE_MESSAGE:-Pipeline stopped during $CURRENT_STAGE (exit $code)}"
    printf '%s\n' "$message" >&2
    printf '[%s] %s\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$message" >> "$PIPELINE_LOG"
    mark_failed "$message" "$code"
  fi
  exit "$code"
}

on_signal() {
  FAILURE_MESSAGE="Interrupted by $1 during $CURRENT_STAGE"
  if [[ -n "$ACTIVE_STAGE_PID" ]]; then
    kill -s "$1" "$ACTIVE_STAGE_PID" 2>/dev/null || true
  fi
  exit "$2"
}

# EXIT covers logging/helper failures too; these can happen outside a command.
trap on_exit EXIT
trap 'on_signal HUP 129' HUP
trap 'on_signal INT 130' INT
trap 'on_signal TERM 143' TERM

mkdir "$LOG_DIR"
GIT_COMMIT="$(git -C "$PROJECT_ROOT" rev-parse HEAD 2>/dev/null || printf 'unknown')"
if [[ -n "$(git -C "$PROJECT_ROOT" status --porcelain 2>/dev/null || true)" ]]; then
  GIT_DIRTY=true
else
  GIT_DIRTY=false
fi
python3 "$PROJECT_ROOT/pipeline_status.py" init \
  --status-file "$STATUS_FILE" --run-id "$RUN_ID" --mode "$MODE" \
  --simulation-script "$SIMULATION_SCRIPT" --image "$IMAGE" \
  --git-commit "$GIT_COMMIT" --git-dirty "$GIT_DIRTY" --pid "$$"

run_stage() {
  local stage="$1"
  shift
  local stage_log="$LOG_DIR/${stage}.log"
  CURRENT_STAGE="$stage"
  log "Starting stage: $stage"
  python3 "$PROJECT_ROOT/pipeline_status.py" stage \
    --status-file "$STATUS_FILE" --name "$stage" --stage-status running --log "logs/${stage}.log"

  python3 "$PROJECT_ROOT/pipeline_stage.py" --name "$stage" --log "$stage_log" \
    --pipeline-log "$PIPELINE_LOG" --progress-file "$PROGRESS_FILE" \
    --heartbeat-seconds "${HEARTBEAT_SECONDS:-30}" -- "$@" &
  ACTIVE_STAGE_PID=$!
  local command_status=0
  wait "$ACTIVE_STAGE_PID" || command_status=$?
  ACTIVE_STAGE_PID=""

  if (( command_status != 0 )); then
    FAILURE_MESSAGE="Stage $stage failed with exit code $command_status; see logs/${stage}.log"
    exit "$command_status"
  fi
  python3 "$PROJECT_ROOT/pipeline_status.py" stage \
    --status-file "$STATUS_FILE" --name "$stage" --stage-status completed --log "logs/${stage}.log" --exit-code 0
  log "Completed stage: $stage"
}

MIN_FREE_GIB="${MIN_FREE_GIB:-}"
if [[ -z "$MIN_FREE_GIB" ]]; then
  if [[ "$MODE" == "smoke" ]]; then MIN_FREE_GIB=1; else MIN_FREE_GIB=6; fi
fi
run_stage preflight python3 "$PROJECT_ROOT/pipeline_status.py" preflight \
  --image "$IMAGE" --run-dir "$RUN_DIR" --min-free-gib "$MIN_FREE_GIB"

docker_args=(
  run --rm --user "$(id -u):$(id -g)"
  --volume "$PROJECT_ROOT:/workspace:ro"
  --volume "$RUN_DIR:/run"
  --volume "$PROJECT_ROOT/rules:/run/rules:ro"
  --volume "$PROJECT_ROOT/lmodern.sty:/run/lmodern.sty:ro"
  --workdir /run
  --env "PIPELINE_PROGRESS_FILE=/run/progress.json"
  --env "PYTHONPATH=/workspace"
  --env "PYTHONUNBUFFERED=1"
)
if [[ -n "$SIMULATION_ITERATIONS" ]]; then
  docker_args+=(--env "SIMULATION_ITERATIONS=$SIMULATION_ITERATIONS")
fi

run_stage simulation \
  docker "${docker_args[@]}" "$IMAGE" \
  -f /workspace/molecules.py \
  -f "/workspace/$SIMULATION_SCRIPT" \
  -f /workspace/export_hypergraph.py \
  -f /workspace/printer.py

run_stage validate-simulation \
  python3 "$PROJECT_ROOT/validate_pipeline.py" --run-dir "$RUN_DIR" --stage simulation

run_stage svg-conversion \
  docker "${docker_args[@]}" --entrypoint python "$IMAGE" \
  /workspace/convert_hypergraph_svgs.py --out-dir out

run_stage validate-assets \
  python3 "$PROJECT_ROOT/validate_pipeline.py" --run-dir "$RUN_DIR" --stage assets

run_stage report-build \
  env OUTPUT_DIR="$RUN_DIR/out" REPORT_DIR="$RUN_DIR/report.tmp" \
  python3 "$PROJECT_ROOT/organize_hypergraph_assets.py"

run_stage validate-report \
  python3 "$PROJECT_ROOT/validate_pipeline.py" --run-dir "$RUN_DIR" --stage report --report-dir report.tmp

run_stage publish-report mv "$RUN_DIR/report.tmp" "$RUN_DIR/report"

python3 "$PROJECT_ROOT/pipeline_status.py" finish \
  --status-file "$STATUS_FILE" --run-status completed \
  --message "Report generated at report/hypergraph.html" --exit-code 0

log "Done. Open $RUN_DIR/report/hypergraph.html"
printf '\nRun completed: %s\nReport: %s\nStatus: %s\n' "$RUN_ID" "$RUN_DIR/report/hypergraph.html" "$STATUS_FILE"
PIPELINE_COMPLETED=1
