# Helpers de progresso compartilhados pelos scripts do pipeline
# (molecules.py, simulation.py, export_hypergraph.py, printer.py,
# organize_hypergraph_assets.py). Segue o mesmo padrão de compatibilidade
# try/except usado nos demais scripts: funciona com ou sem tqdm instalado.
import contextlib
import os
import sys
import time

if os.getcwd() not in sys.path:
    sys.path.insert(0, os.getcwd())

try:
    from tqdm import tqdm
except ImportError:
    tqdm = None


@contextlib.contextmanager
def phase(description):
    # Banner de fase com spinner indeterminado (tempo decorrido), usado para
    # etapas cujo progresso real ocorre dentro do kernel C++ do MØD.
    if tqdm is None:
        print(f"==> {description}...")
        start = time.time()
        yield
        print(f"==> {description} concluido ({time.time() - start:.1f}s)")
        return

    bar = tqdm(total=1, desc=description, bar_format="{desc}: {elapsed}")
    try:
        yield bar
    finally:
        bar.update(1)
        bar.close()


def phase_start(description):
    # Versao sem `with`, util para envolver o corpo inteiro de um script
    # sem precisar reindentar (ex.: molecules.py).
    if tqdm is None:
        print(f"==> {description}...")
        return (None, description, time.time())
    return (tqdm(total=1, desc=description, bar_format="{desc}: {elapsed}"), description, None)


def phase_end(token):
    bar, description, start = token
    if bar is None:
        print(f"==> {description} concluido ({time.time() - start:.1f}s)")
        return
    bar.update(1)
    bar.close()


def progress_iter(iterable, **kwargs):
    # Barra de progresso sobre um iteravel, com fallback transparente se
    # tqdm nao estiver disponivel.
    items = list(iterable)
    if tqdm is None:
        return items
    return tqdm(items, **kwargs)
