#include <stdio.h>
#include <stdlib.h>

struct aresta { //Admite o tipo aresta como sendo
    char* v1;
    char* v2;
    char c;
    int existeArestaMatrizA;
    int existeArestaMatrizB;
};
typedef struct aresta Aresta;

struct grafo {
    Aresta **arestasMatrizA;
    Aresta **arestasMatrizB;
    int numVertice;
    int numAresta;
};

typedef struct grafo Grafo;

Aresta** inicializarMatriz(int v) {

    Aresta** a = (Aresta**) malloc(v * v * sizeof (Aresta*));

    for (int i = 0; i < v; i++) {
        a[i] = (Aresta*) malloc(v * sizeof (Aresta));
    }
    for (int i = 0; i < v; i++) {
        for (int j = 0; j < v; j++) {
            a[i][j].c = '0';
        }
    }
    return a;
}

Aresta** inicializarMatriz01(int v) {
    Aresta** matrizA = (Aresta**) malloc(v * v * sizeof (Aresta*));
    for (int i = 0; i < v; i++) {
        matrizA[i] = (Aresta*) malloc(v * sizeof (Aresta));
    }
    //linha 01
    matrizA[0][0].existeArestaMatrizA = 0;
    matrizA[0][1].existeArestaMatrizA = 0;
    matrizA[0][2].existeArestaMatrizA = 0;
    matrizA[0][3].existeArestaMatrizA = 1;
    //linha 02
    matrizA[1][0].existeArestaMatrizA = 0;
    matrizA[1][1].existeArestaMatrizA = 0;
    matrizA[1][2].existeArestaMatrizA = 0;
    matrizA[1][3].existeArestaMatrizA = 1;
    //linha 03
    matrizA[2][0].existeArestaMatrizA = 0;
    matrizA[2][1].existeArestaMatrizA = 0;
    matrizA[2][2].existeArestaMatrizA = 0;
    matrizA[2][3].existeArestaMatrizA = 0;
    //linha 04
    matrizA[3][0].existeArestaMatrizA = 0;
    matrizA[3][1].existeArestaMatrizA = 0;
    matrizA[3][2].existeArestaMatrizA = 1;
    matrizA[3][3].existeArestaMatrizA = 0;
    return matrizA;
}

Aresta** inicializarMatriz02(int v) {
    Aresta** matrizB = (Aresta**) malloc(v * v * sizeof (Aresta*));
    for (int i = 0; i < v; i++) {
        matrizB[i] = (Aresta*) malloc(v * sizeof (Aresta));
    }
    //linha 01
    matrizB[0][0].existeArestaMatrizB = 0;
    matrizB[0][1].existeArestaMatrizB = 0;
    matrizB[0][2].existeArestaMatrizB = 0;
    matrizB[0][3].existeArestaMatrizB = 1;
    //linha 02
    matrizB[1][0].existeArestaMatrizB = 0;
    matrizB[1][1].existeArestaMatrizB = 0;
    matrizB[1][2].existeArestaMatrizB = 0;
    matrizB[1][3].existeArestaMatrizB = 0;
    //linha 03
    matrizB[2][0].existeArestaMatrizB = 0;
    matrizB[2][1].existeArestaMatrizB = 0;
    matrizB[2][2].existeArestaMatrizB = 0;
    matrizB[2][3].existeArestaMatrizB = 0;
    //linha 04
    matrizB[3][0].existeArestaMatrizB = 0;
    matrizB[3][1].existeArestaMatrizB = 0;
    matrizB[3][2].existeArestaMatrizB = 1;
    matrizB[3][3].existeArestaMatrizB = 0;
    return matrizB;
}
Grafo* definirAresta(Grafo*g, int v) {

    char** nome = (char**) malloc(v * sizeof (char*));
    for (int i = 0; i < v; i++) {
        nome[i] = (char*) malloc(v * v * sizeof (char));
        scanf("%s", nome[i]);
    }

    for (int i = 0; i < v; i++) {
        for (int j = 0; j < v; j++) {

            g->arestasMatrizA[i][j].v1 = nome[i];
            g->arestasMatrizA[i][j].v2 = nome[j];

        }

    }

    return g;

}

void printar(Grafo *gr) {
    for (int i = 0; i < gr->numVertice; i++) {
        for (int j = 0; j < gr->numVertice; j++) {
            printf("(%s, %s, %c)", gr->arestasMatrizA[i][j].v1, gr->arestasMatrizA[i][j].v2, gr->arestasMatrizA[i][j].c);
        }
        printf("\n");
    }
}

Grafo* criar_grafo(int v) {
    Grafo* g = (Grafo*) malloc(sizeof (Grafo));
    g->numVertice = v;
    g->numAresta = 0;
    //g->a=NULL;
    //g->a = inicializarMatriz(v);
    g->arestasMatrizA = inicializarMatriz01(v);
    g->arestasMatrizB = inicializarMatriz02(v);
    return g;
}

Grafo* inserir_aresta(Grafo* g, int linha, int col) {
    if (g->arestasMatrizA[linha][col].c == '0') {
        g->arestasMatrizA[linha][col].c = '1';
        g->numAresta++;
    }

    return g;

}

int main() {
    //    printf("Digite a quantidade de vértices do grafo:\n");
    //    int v;
    //    scanf("%d", &v);
    //    Grafo *g = criar_grafo(v);
    //    printf("Digite nomes dos vértices:\n");
    //    g = definirAresta(g, v);
    // Passo 1 - Criar o grafo informando a qtd de vertices
    Grafo *g = criar_grafo(4);


    system("clear");
    printar(g);

}
