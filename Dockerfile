# Base Debian-Slim enxuta e compatível
FROM mambaorg/micromamba:1.5

# Ativar automaticamente o ambiente Conda/Micromamba base durante a compilação (docker build)
ARG MAMBA_DOCKERFILE_ACTIVATE=1

# Mudar para root temporariamente para instalar dependências do sistema
USER root

# Instalar compilador LaTeX minimalista e make para geração de PDFs do PostMØD
RUN apt-get update && apt-get install -y --no-install-recommends \
    texlive-latex-base \
    texlive-fonts-recommended \
    texlive-latex-extra \
    texlive-science \
    texlive-lmodern \
    make \
    && rm -rf /var/lib/apt/lists/*

# Voltar para o usuário do container por segurança
USER $MAMBA_USER

WORKDIR /app

# Instala MØD, Graphviz e Openbabel de forma compatível e limpa caches
RUN micromamba install -y -n base -c jakobandersen -c conda-forge \
    mod \
    graphviz \
    openbabel \
    && micromamba clean --all --yes

# Configurar variáveis de ambiente necessárias
ENV PATH="/opt/conda/bin:${PATH}"

# Inicializar os formatos do pós-processador do MØD para LaTeX
RUN mod_post --install-format

# Define o entrypoint padrão do wrapper de simulação MØD
ENTRYPOINT ["mod"]
