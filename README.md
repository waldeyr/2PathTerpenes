![2Path for Plant Terpenes](https://github.com/waldeyr/2PathTerpenes/blob/master/interface/img/2PathLogo.png)

## [EN] How to use it?

First, you need to have a Linux environment with MedØlDatschgerl (MØD) version 0.8.0 or bigger.
Assuming you have [Docker](https://docs.docker.com/install/linux/docker-ce/ubuntu/) installed, then just pull the image:

`docker pull waldeyr/mod_v0.8.0:v1.0`

Clone this repository repositório

`git clone https://github.com/waldeyr/2PathTerpenes.git && cd 2PathTerpenes`

Run the code:

`docker run --rm --volume $(pwd):/home/shared/ --workdir /home/shared/ waldeyr/mod_v0.8.0:v1.0 /home/mod-v0.8.0/bin/mod -f /home/shared/molecules.py -f /home/shared/simulation.py -f /home/shared/printer.py `

The simulation.py is generated by the [index.html](interface/index.html)

### Associated publications 
[Exploring Plant Sesquiterpene Diversity by Generating Chemical Networks](https://www.mdpi.com/2227-9717/7/4/240)

### Screenshot

![Screenshot](https://github.com/waldeyr/2PathTerpenes/blob/master/interface/img/screenshot01.png)


## [PT-BR] Como configurar e rodar as simulações?

Assumindo que o [Docker](https://docs.docker.com/install/linux/docker-ce/ubuntu/) esteja instalado em um ambiente Linux, baixar a imagem Docker:

`docker pull waldeyr/mod_v0.8.0:v1.0`

Clonar este repositório em seu computador

`git clone https://github.com/waldeyr/2PathTerpenes.git`

Entrar na pasta

`cd 2PathTerpenes`

Rodar o Docker em modo interativo compartilhando a pasta local atual (pwd) com a pasta shared do container

`docker run --rm -v $(pwd):/home/shared -it waldeyr/mod_v0.8.0:v1.0 bash`

Ou simplesmente rodar o script no Docker sem "entrar" no container

``docker run --rm --volume $(pwd):/home/shared/ --workdir /home/shared/ waldeyr/mod_v0.8.0:v1.0 /home/mod-v0.8.0/bin/mod -f /home/shared/molecules.py -f /home/shared/simulation.py -f /home/shared/printer.py``



P.S. The old version is [here](https://bitbucket.org/wmcs/2path15/src/master/)

P.S. A versão antiga está [aqui](https://bitbucket.org/wmcs/2path15/src/master/)
