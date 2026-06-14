# Base Debian-Slim enxuta e compatível
# Lean and compatible Debian-Slim base
FROM mambaorg/micromamba:1.5

# Ativar automaticamente o ambiente Conda/Micromamba base durante a compilação (docker build)
# Automatically activate the base Conda/Micromamba environment during build (docker build)
ARG MAMBA_DOCKERFILE_ACTIVATE=1

# Mudar para root temporariamente para instalar dependências do sistema
# Switch to root temporarily to install system dependencies
USER root

# Instalar compilador LaTeX minimalista e make para geração de PDFs do PostMØD
# Install a minimal LaTeX compiler and make for generating PostMØD PDFs
RUN apt-get update && apt-get install -y --no-install-recommends \
    texlive-latex-base \
    texlive-fonts-recommended \
    texlive-latex-extra \
    texlive-science \
    lmodern \
    make \
    && rm -rf /var/lib/apt/lists/*

# Voltar para o usuário do container por segurança
# Switch back to the container user for security
USER $MAMBA_USER

WORKDIR /app

# Instala MØD, Graphviz, Openbabel e tqdm (barras de progresso) de forma compatível e limpa caches
# Install MØD, Graphviz, Openbabel and tqdm (progress bars) in a compatible way and clean caches
RUN micromamba install -y -n base -c jakobandersen -c conda-forge \
    mod \
    graphviz \
    openbabel \
    tqdm \
    && micromamba clean --all --yes

# Configurar variáveis de ambiente necessárias
# Set required environment variables
ENV PATH="/opt/conda/bin:${PATH}"

# Inicializar os formatos do pós-processador do MØD para LaTeX
# Initialize the MØD post-processor formats for LaTeX
RUN mod_post --install-format

# Define o entrypoint padrão do wrapper de simulação MØD
# Define the default entrypoint for the MØD simulation wrapper
ENTRYPOINT ["mod"]
