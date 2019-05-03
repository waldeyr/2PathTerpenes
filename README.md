# TCC Daniela

Objetivo

* Simular a biossíntese de monoterpenos em espécies de Milho (Zea mays)

Objetivos específicos

* Escrever regras de gramática de grafos para transformações químicas a partir do Geranyl Diphosphato
* Escrever simulações da biossíntese a partir das regras escritas, utilizando diferentes estratégias de derivação 
* Armazenar os resultados em banco de dados
* Criar queries no banco para responder a questõs biológicas relevantes
* Criar um sistema Web para consulta utilizando as queries construídas

Sabinene as target

`/home/docker/mod-v0.7.0/bin/mod -e 'target = smiles ("C=C1CCC2(CC12)C(C)C")' -f simulation.py -f dg.py -f pathway.py`
