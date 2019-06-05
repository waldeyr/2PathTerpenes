# TCC Daniela

Objetivo

* Simular a biossíntese de monoterpenos em espécies de Milho (Zea mays) - OK;

Objetivos específicos

* Escrever regras de gramática de grafos para transformações químicas a partir do Geranyl Diphosphato - OK;
* Escrever simulações da biossíntese a partir das regras escritas, utilizando diferentes estratégias de derivação - OK;
* Armazenar os resultados em banco de dados - TO DO;
* Criar queries no banco para responder a questõs biológicas relevantes - TO DO;
* Criar um sistema Web para:
1. Gerar o arquivo de simulação - Em andamento;
2. Consulta utilizando as queries construídas -TO DO;

## Como configurar e rodar as simulacoes?

Assumindo que o [Docker](https://docs.docker.com/install/linux/docker-ce/ubuntu/) esteja instalado, baixar a imagem Docker:

`docker pull waldeyr/mod_v0.8.0:v1.0`

Clonar este repositório

`git clone https://github.com/waldeyr/tcc_daniela.git`

Entrar na pasta

`cd tcc_daniela`

Rodar o Docker compartilhando a pasta local atual (pwd) com a pasta shared do container

`docker run --rm -v $(pwd):/home/shared -it waldeyr/mod_v0.8.0:v1.0 bash`

Ou simplesmente rodar o scipt no docker sem entrar no container

``docker run --rm -v $(pwd):/home/shared/ waldeyr/mod_v0.8.0:v1.0 /home/mod-v0.8.0/bin/mod -f /home/shared/molecules.py -f /home/shared/simulation.py -f /home/shared/printer.py``

