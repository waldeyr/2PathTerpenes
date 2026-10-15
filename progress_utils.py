# Helpers de progresso compartilhados pelos scripts do pipeline
# (molecules.py, simulation.py, export_hypergraph.py, printer.py,
# organize_hypergraph_assets.py). Segue o mesmo padrão de compatibilidade
# try/except usado nos demais scripts: funciona com ou sem tqdm instalado.
import contextlib
import fcntl
import json
import os
import sys
import tempfile
import time

if os.getcwd() not in sys.path:
    sys.path.insert(0, os.getcwd())

try:
    from tqdm import tqdm
except ImportError:
    tqdm = None


PROGRESS_FILE = os.environ.get("PIPELINE_PROGRESS_FILE")
_last_report = {}


def update_progress(path, **fields):
    """Serialize event and heartbeat updates from separate host/container processes.

    The stage runner emits heartbeats independently of Python's GIL, including
    while MØD is executing native code or compiling the PDF report.
    """
    if not path:
        return
    path = os.fspath(path)
    directory = os.path.dirname(os.path.abspath(path))
    os.makedirs(directory, exist_ok=True)
    with open(f"{path}.lock", "a", encoding="utf-8") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        try:
            with open(path, encoding="utf-8") as handle:
                payload = json.load(handle)
        except FileNotFoundError:
            payload = {}
        payload.update(fields)
        payload["updatedAt"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        descriptor, temporary = tempfile.mkstemp(prefix=".progress-", suffix=".json", dir=directory)
        try:
            with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
                json.dump(payload, handle)
                handle.write("\n")
            os.replace(temporary, path)
        except BaseException:
            if os.path.exists(temporary):
                os.unlink(temporary)
            raise
    return payload


def _write_progress(description, current=None, total=None, status="running"):
    update_progress(PROGRESS_FILE, description=description, current=current, total=total,
                    status=status, phaseUpdatedAt=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()))


def _should_report(description, current, total):
    """Limit textual progress updates to roughly twenty messages per phase."""
    if not total:
        return True
    interval = max(1, total // 20)
    previous = _last_report.get(description)
    if current == total or current == 0 or previous is None or current - previous >= interval:
        _last_report[description] = current
        return True
    return False


@contextlib.contextmanager
def phase(description):
    # Banner de fase com spinner indeterminado (tempo decorrido), usado para
    # etapas cujo progresso real ocorre dentro do kernel C++ do MØD.
    _write_progress(description, status="running")
    if tqdm is None:
        print(f"==> {description}...", flush=True)
        start = time.time()
        outcome = "failed"
        try:
            yield
        except BaseException:
            _write_progress(description, status="failed")
            raise
        else:
            outcome = "completed"
            _write_progress(description, status="completed")
        finally:
            print(f"==> {description} {outcome} ({time.time() - start:.1f}s)", flush=True)
        return

    bar = tqdm(total=1, desc=description, bar_format="{desc}: {elapsed}")
    try:
        yield bar
    except BaseException:
        _write_progress(description, status="failed")
        raise
    else:
        bar.update(1)
        _write_progress(description, current=1, total=1, status="completed")
    finally:
        bar.close()


def phase_start(description):
    # Versao sem `with`, util para envolver o corpo inteiro de um script
    # sem precisar reindentar (ex.: molecules.py).
    _write_progress(description, status="running")
    if tqdm is None:
        print(f"==> {description}...", flush=True)
        return (None, description, time.time())
    return (tqdm(total=1, desc=description, bar_format="{desc}: {elapsed}"), description, None)


def phase_end(token):
    bar, description, start = token
    if bar is None:
        print(f"==> {description} completed ({time.time() - start:.1f}s)", flush=True)
        _write_progress(description, status="completed")
        return
    bar.update(1)
    bar.close()
    _write_progress(description, current=1, total=1, status="completed")


def progress_iter(iterable, **kwargs):
    """Publish real counters; the external stage runner supplies heartbeats."""
    items = list(iterable)
    description = kwargs.get("desc", "Working")
    total = len(items)
    _write_progress(description, current=0, total=total, status="running")

    iterator = tqdm(items, **kwargs) if tqdm is not None else items
    for current, item in enumerate(iterator, start=1):
        yield item
        if _should_report(description, current, total):
            _write_progress(description, current=current, total=total)
            print(f"[progress] {description}: {current}/{total}", flush=True)

    _write_progress(description, current=total, total=total, status="completed")
