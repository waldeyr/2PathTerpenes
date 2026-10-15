![2Path for Plant Terpenes](https://github.com/waldeyr/2PathTerpenes/blob/master/docs/img/2PathLogo.png)

# 2PathTerpenes

*Disponível também em:* 🇺🇸 *[English](README.md)*

## Resumo do projeto
O **2PathTerpenes** é uma ferramenta de bioinformática e modelagem química baseada em gramática de grafos para reconstruir e explorar redes metabólicas de biossíntese de terpenos vegetais (monoterpenos C10 e sesquiterpenos C15). O projeto utiliza o simulador **MedØlDatschgerl (MØD)** e o formalismo de Double Pushout (DPO) para gerar caminhos de síntese de moléculas complexas (como $\beta$-caryophyllene, $\alpha$-humulene e $\beta$-farnesene) a partir de precursores acíclicos lineares como o Farnesyl Diphosphate (FPP). Os resultados da simulação podem ser exportados em relatórios estruturais PDF ou como um visualizador interativo de hipergrafo em HTML/JavaScript, opcionalmente anotado com identificadores de compostos da base ChEMBL.

## Lista de funcionalidades
*   **Definição Topológica de Moléculas**: Modelagem de precursores químicos e carbocátions usando representações lineares SMILES e DFS em grafos.
*   **Gramática de Regras de Reação GML**: Aplicação de mecanismos de reação realistas (ciclizações, rearranjos Wagner-Meerwein, shifts de hidreto, eliminação e adição de água).
*   **Geração Automática de Redes Químicas**: Exploração combinatorial e busca de caminhos de reachability resolvidos por Programação Linear Inteira (ILP).
*   **Exportação e Plotagem Visual**: Geração de relatórios em formato PDF com o grafo de derivação química estrutural.
*   **Análise de Restrições de Ciclização**: Propostas de filtros termodinâmicos e geométricos tridimensionais (tensão de anel) nas rotas químicas.

---

# Arquitetura

## Banco de dados (ou outra forma de armazenamento que estiver sendo usada)
Este projeto usa arquivos baseados no formato JSON para armazenamento persistente dos dados do grafo e cache de metadados, além de um conjunto de arquivos GML com regras de reação.

### Diagrama de banco de dados
```mermaid
erDiagram
    HYPERGRAPH_JSON ||--o{ NODE_JSON : contains
    HYPERGRAPH_JSON ||--o{ HYPEREDGE_JSON : contains
    CHEMBL_CACHE_JSON ||--o{ CHEMBL_ENTRY_JSON : stores

    NODE_JSON {
        string id PK
        string name
        string smiles
        int charge
        int cycles
        string image
        int iteration
        string chemblId
        string chemblName
        string pubchemId
        string pubchemName
    }

    HYPEREDGE_JSON {
        string id PK
        string_array sources
        string_array targets
        string_array rules
        string category
    }

    CHEMBL_ENTRY_JSON {
        string smiles PK
        string inchikey
        string chemblId
        string chemblName
        string pubchemId
        string pubchemName
    }
```

### Dicionário de dados

#### Tabela de Nós (dentro de `hypergraph.json` -> `nodes`)
| Campo | Tipo | Descrição |
|---|---|---|
| `id` | String | Identificador único do vértice (ex: `v0`, `v1`). |
| `name` | String | Nome do composto químico (ex: `GPP`, `limonene`). |
| `smiles` | String | Representação SMILES da estrutura molecular. |
| `charge` | Integer | Carga líquida do carbocátion ou molécula neutra. |
| `cycles` | Integer | Número de ciclos/anéis na molécula. |
| `image` | String | Caminho relativo para o arquivo SVG com a representação molecular. |
| `iteration` | Integer | Passos/nível de caminho mais curto a partir dos precursores iniciais (0-indexed). |
| `chemblId` | String | (Opcional) Identificador do composto na base ChEMBL. |
| `chemblName` | String | (Opcional) Nome comum retornado pela base ChEMBL. |
| `pubchemId` | String | (Opcional) Identificador do composto na base PubChem (CID). |
| `pubchemName` | String | (Opcional) Nome comum retornado pela base PubChem. |

#### Tabela de Hiperarestas (dentro de `hypergraph.json` -> `hyperedges`)
| Campo | Tipo | Descrição |
|---|---|---|
| `id` | String | Identificador único da hiperaresta/reação (ex: `e0`, `e1`). |
| `sources` | Vetor de Strings | Identificadores dos nós reagentes (eductos). |
| `targets` | Vetor de Strings | Identificadores dos nós produtos. |
| `rules` | Vetor de Strings | Nomes das regras de reação aplicadas. |
| `category` | String | Categoria da reação (`mono`, `sesqui` ou `common`). |

#### Tabela de Cache ChEMBL (`chembl_cache.json`)
| Campo | Tipo | Descrição |
|---|---|---|
| `smiles` | String | Representação SMILES da molécula (Chave Primária). |
| `inchikey` | String | InChIKey calculado (hash) da estrutura SMILES. |
| `chemblId` | String | Identificador do composto na base ChEMBL (ou null se não houver correspondência). |
| `chemblName` | String | Nome comum do composto na base ChEMBL (ou null se não houver correspondência). |
| `pubchemId` | String | Identificador do composto na base PubChem (ou null se não houver correspondência). |
| `pubchemName` | String | Nome comum do composto na base PubChem (ou null se não houver correspondência). |

## Componentes
O fluxo de simulação é dividido em componentes de especificação de grafos, aplicação de gramáticas DPO, geração do grafo de derivação e persistência em banco de dados.

### Diagrama de componentes
```mermaid
graph TD
    UI[Interface Web: index.html] -->|Gera parâmetros| SimPy[simulation.py]
    SimPy -->|Importa moléculas| MolPy[molecules.py]
    SimPy -->|Carrega regras GML| RulesGML[rules/*.gml]
    SimPy -->|Invoca| MOD[MØD Wrapper/Library]
    MOD -->|Constrói| DG[Derivation Graph]
    DG -->|Formata Relatório| PrintPy[printer.py]
    PrintPy -->|Gera| PDF[Relatório PDF]
    DG -->|Exporta| ExportPy[export_hypergraph.py]
    ExportPy -->|Grava| HGJSON[hypergraph.json]
    HGJSON -->|Anota| AnnotatePy[annotate_chembl.py]
    AnnotatePy -->|Consulta| ChEMBL[APIs ChEMBL & PubChem]
    HGJSON -->|Renderiza| HGHTML[hypergraph.html]
```

### Interface Web
A interface web (https://waldeyr.github.io/2PathTerpenes) fornece um painel responsivo para selecionar regras de reação e definir parâmetros de simulação.

### Tecnologias e suas versões

| Tecnologia | Versão | Função Principal |
|---|---|---|
| MedØlDatschgerl (MØD) | v1.0.0+ | Kernel de transformação de grafos químicos (DPO) e solver ILP. |
| Python | v3.8+ | Scripts de automação da simulação (`molecules.py`, `simulation.py`, `printer.py`). |
| Open Babel | v3.0+ | Geração de conformações 3D e cálculo de energia dos carbocátions. |
| Docker | v19.x+ | Empacotamento de ambiente Linux completo para execução do MØD de forma agnóstica. |

---

## Funcionalidades

### Requisitos

| Funcionalidade | Campo de Formulário | Campo de Banco de Dados | Regras Aplicadas |
|---|---|---|---|
| **Definição de Moléculas** | N/A (Arquivo de script) | `Compound.smiles`, `Compound.modName` | Sintaxe SMILES ou DFS para inicializar o multiset de reagentes da simulação. |
| **Geração de Rede Química** | N/A (Arquivo de script) | `Rule.modName`, `Compound.id` | Aplicação repetitiva de regras de DPO graph rewriting (`addSubset >> repeat`). |
| **Geração de PDF** | N/A (Relatório final) | N/A | Renderização dos intermediários com hidrogênios colapsados e coloração (vermelho para anéis, azul para cargas). |
| **Gravação de Cenários** | N/A (Script de carga) | `Scenario.scenarioID`, `Scenario.ncbiAccession`, `Scenario.pubmedAccession` | Mapeamento relacional de moléculas e reações físicas com ensaios in vitro descritos na literatura. |

---

## Análise de Restrições de Ciclização nas Regras de Simulação
Durante a geração de caminhos de síntese de sesquiterpenos, reações de ciclização eletrofílica ocorrem com alta reatividade molecular. Como o MØD tradicional atua apenas a nível topológico de grafos discretos, ciclizações impossíveis de ocorrer no espaço 3D real por alta tensão conformacional poderiam ser simuladas.

Identificamos **quatro possíveis melhorias de arquitetura** para implementar restrições de ciclização nas simulações:
1.  **Filtro de Energia Conformacional (via Open Babel)**: Com o MØD v1.0.0+, o Open Babel calcula coordenadas 3D e estima a energia livre de cada carbocátion via campo de força MMFF94 (`Graph.energy`). Pode-se implementar uma validação em Python que descarte intermediários de ciclização cujo delta de energia conformacional em relação ao precursor seja excessivo (tensão do anel inviável).
2.  **Restrições no Contexto das Regras GML**: Adição de caminhos rígidos e topologia impeditiva no `context` do GML. Impede a regra de ser aplicada se a molécula já tiver sistemas de anéis adjacentes rígidos que impeçam fisicamente o dobramento da cadeia.
3.  **Heurísticas com Estratégia de Derivação Customizada (DGStrat em Python)**: Utilização de uma estratégia de derivação escrita em Python para interceptar a criação de ciclos e bloquear reações que gerem anéis tensionados incompatíveis (ex: anéis com pontes complexas de 3 ou 4 carbonos em locais inadequados).
4.  **Hyperflow e Programação Linear com Custos**: No MØD v1.0, o solver de Programação Linear Inteira (ILP) pode atribuir custos e capacidades baseados em restrições termodinâmicas no fluxo geral da rede, minimizando caminhos energeticamente desfavoráveis.

---

## Instalação e uso

### Organização dos Arquivos de Regras e Recursos
*   **Regras GML (`rules/`)**: Todas as regras de reação GML oficiais são mantidas e atualizadas diretamente no diretório `rules/`.
*   **Imagens de Recursos (`docs/img/`)**: Apenas imagens que são ativamente usadas ou dinamicamente referenciadas (como visualizações de regras) por `docs/index.html` são mantidas no controle de versão. Arquivos temporários ou redundantes de imagem são limpos antes do commit.

### Gerando Previews de Regras GML

Para gerar as imagens de visualização SVG das regras de reação química exibidas na interface web:

1. **Execute o gerador dentro do Docker** (isso compila as regras GML e gera arquivos `.pdf` em `out/`):
   ```bash
   docker run --rm --user "$(id -u):$(id -g)" --volume "$(pwd):/home/shared" --workdir /home/shared 2path-terpenes-mod:latest -f /home/shared/generate_rules_svg.py
   ```

2. **Converta os PDFs gerados em SVGs** (rodando o loop dentro do container MØD de uma só vez):
   ```bash
   docker run --rm --user "$(id -u):$(id -g)" --entrypoint /bin/bash --volume "$(pwd):/home/shared" --workdir /home/shared 2path-terpenes-mod:latest -c "for f in out/*_{L,K,R}.pdf; do mod_post --mode pdfToSvg \${f%.pdf} \${f%.pdf}; done"
   ```

3. **Copie as imagens geradas para a pasta de recursos**:
   ```bash
   python organize_svgs.py
   ```
   Este script auxiliar copia os componentes `_L.svg`, `_K.svg` e `_R.svg` de `out/` diretamente para `docs/img/` mantendo seus nomes originais.

### Rodando Simulações com Docker (Recomendado)

#### Como testar na sua máquina:

1. **Reconstrua a imagem Docker**:
   ```bash
   docker build -t 2path-terpenes-mod:latest .
   ```
   *(Nota: A imagem Docker instala o compilador LaTeX com suporte a fontes Latin Modern por meio do pacote Debian `lmodern`, corrigindo eventuais problemas de compilação do arquivo de resumo `summary.pdf`. Para suportar ambientes LaTeX mínimos, também incluímos um arquivo de fallback mock `lmodern.sty` no workspace, de modo que a compilação use automaticamente as fontes padrão do LaTeX caso o pacote `lmodern` esteja ausente.)*

2. **Execute a simulação principal do projeto**:
   ```bash
   docker run --rm --user "$(id -u):$(id -g)" --volume "$(pwd):/home/shared" --workdir /home/shared 2path-terpenes-mod:latest -f /home/shared/molecules.py -f /home/shared/simulation.py -f /home/shared/printer.py
   ```

### Visualizador Interativo de Hipergrafos (HTML/JS)

Além do relatório em LaTeX/PDF, o grafo de derivação pode ser exportado como um "mapa de metrô" interativo e autocontido no navegador: moléculas são estações e reações (que podem ter vários educts/produtos) são as conexões entre linhas, coloridas por categoria de regra (Mono/Sesqui/Common).

#### Forma rápida (recomendada): `run-pipeline.sh`

Use este comando para gerar o visualizador. Ele é o único ponto de entrada que
executa simulação, exportação do hipergrafo, conversão PDF→SVG, validações e a
montagem do HTML. Os comandos Docker manuais usados apenas com `printer.py`
geram PDFs, mas **não** geram o HTML.

```bash
bash run-pipeline.sh
```

Cada execução é isolada em `runs/<id>/`, para que uma rodada não reutilize
assets de outra. Ao final, o script informa o caminho de
`runs/<id>/report/hypergraph.html`, que pode ser aberto diretamente (sem
servidor). Acompanhe uma rodada longa por:

```bash
tail -f runs/<id>/logs/pipeline.log
cat runs/<id>/status.json
cat runs/<id>/progress.json
```

Para executar a simulação expandida (todas as regras, sete iterações), use:

```bash
bash run-pipeline.sh --full
```

Antes de uma rodada longa, verifique o fluxo inteiro com uma única iteração:

```bash
bash run-pipeline.sh --smoke
```

O pipeline preserva um log por etapa em `runs/<id>/logs/` e um log consolidado
em `logs/pipeline.log`. O `status.json` registra o PID, commit Git, alterações
locais, horários, etapa e código de saída. Falhas de comandos, de gravação de
logs ou de outros auxiliares encerram a rodada como `failed`. Sinais `SIGHUP`,
`SIGINT` e `SIGTERM` também registram a interrupção e encerram os processos
da etapa. `SIGKILL` e desligamento da máquina não permitem esse tratamento.

Antes da publicação, o validador compara o JSON embutido no HTML com
`out/hypergraph.json`, confere os caminhos das imagens e rejeita arquivos
ausentes ou vazios, incluindo CSS, JavaScript e logo. O relatório é montado
em `report.tmp/` e só recebe o nome `report/` após passar na validação.
Uma falha preserva os artefatos da rodada para inspeção.

As iterações em Python publicam contadores reais e usam `tqdm` quando disponível.
Durante o processamento interno do MØD e a compilação de PDFs, um processo
separado publica um heartbeat a cada 30 segundos no log e em `progress.json`.
O heartbeat informa que a etapa está ativa; não estima um percentual do kernel.
O arquivo separa o estado da etapa (`stageStatus`) do estado da última fase
Python (`status`) e informa o tempo decorrido (`stageElapsedSeconds`).

#### Rodadas longas e configuração

Para manter uma execução após desconectar o SSH, use `nohup` com um ID conhecido:

```bash
nohup bash run-pipeline.sh --full --run-id rodada-full > rodada-full-console.log 2>&1 < /dev/null &
tail -f rodada-full-console.log
```

O script também é executável diretamente como `./run-pipeline.sh`. O ID precisa
ser novo; uma rodada existente não é sobrescrita nem retomada automaticamente.

Para usar outro disco ou ajustar o intervalo de acompanhamento:

```bash
RUNS_DIR=/caminho/para/rodadas HEARTBEAT_SECONDS=15 bash run-pipeline.sh --full --run-id rodada-full
```

`RUNS_DIR` aceita caminhos absolutos ou relativos ao diretório de onde o comando
é executado. O diretório real da rodada é montado no container como `/run`.
`IMAGE` seleciona uma imagem Docker já construída. A pré-checagem verifica a
imagem, a escrita e o espaço livre no disco de destino: no mínimo 6 GiB para
rodadas normais/completas e 1 GiB para `--smoke`. Use `MIN_FREE_GIB` para ajustar
esse mínimo; ele não é uma estimativa nem uma garantia de espaço para toda a rodada.
O host precisa de Python 3.9+ e Docker, em Linux ou macOS.

#### Testes de regressão

```bash
python3 -m unittest discover -s tests -v
```

Os testes verificam pacotes inválidos, sinais, falhas de logging, heartbeat e
diretórios personalizados usando um substituto do Docker. Não executam o MØD;
para verificar a integração real com a imagem instalada, execute `--smoke`.

#### Execução manual na raiz do projeto

Os passos abaixo usam os diretórios `out/` e `report/` da raiz, sem o isolamento
e o acompanhamento fornecidos por `run-pipeline.sh`.

1. **Exportar o hipergrafo como JSON** (executar junto com os scripts de simulação existentes):
   ```bash
   docker run --rm --user "$(id -u):$(id -g)" --volume "$(pwd):/home/shared" --workdir /home/shared 2path-terpenes-mod:latest -f /home/shared/molecules.py -f /home/shared/simulation.py -f /home/shared/export_hypergraph.py -f /home/shared/printer.py
   ```
   Isso grava `out/hypergraph.json` e renderiza um PDF de representação para cada molécula.

2. **Converter somente os PDFs referenciados em `out/hypergraph.json` para SVG**:
   ```bash
   docker run --rm --user "$(id -u):$(id -g)" --entrypoint python --volume "$(pwd):/home/shared" --workdir /home/shared 2path-terpenes-mod:latest /home/shared/convert_hypergraph_svgs.py
   ```

3. **(Opcional) Anotar as moléculas com identificadores de bases de dados**:
   ```bash
   python annotate_chembl.py
   ```
   Para cada molécula com o campo `smiles`, este script calcula seu InChIKey (via CLI `obabel`) e busca uma correspondência exata na [API REST do ChEMBL](https://www.ebi.ac.uk/chembl/api/data/molecule). Se nenhuma correspondência for encontrada, o script faz um fallback consultando o InChIKey na **API REST do PubChem (PUG-REST)**. Ele adiciona os campos `chemblId`/`chemblName` ou `pubchemId`/`pubchemName` a `out/hypergraph.json` quando há correspondência. Os resultados são armazenados em cache em `out/chembl_cache.json`, de modo que execuções repetidas não consultam as APIs externas para estruturas já vistas. Moléculas anotadas exibem seus respectivos links e nomes comuns no painel de detalhes do visualizador e passam a ser pesquisáveis por esse nome.

4. **Gerar o relatório standalone**:
   ```bash
   python organize_hypergraph_assets.py
   ```
   Isso monta `report/hypergraph.html` junto com seu CSS/JS e as representações SVG das moléculas, com os dados do hipergrafo embutidos inline para a página funcionar offline via `file://`.
   Se `report/` já existir, escolha um destino novo com `REPORT_DIR=report-novo python3 organize_hypergraph_assets.py`; o montador preserva pacotes anteriores.

5. **Abrir `report/hypergraph.html`** diretamente no navegador. A pasta `report/` inteira é autocontida e pode ser zipada e compartilhada.

O visualizador suporta pan/zoom, busca por nome de molécula, filtro por categoria de reação, e clique em uma molécula ou reação para ver detalhes (SMILES, carga, anéis, regra(s) aplicada(s)).
