#include <stdio.h>
#include <stdlib.h>

struct aresta{ //Admite o tipo aresta como sendo
	char* v1;
	char* v2;
	char c;
};
typedef struct aresta Aresta;

struct grafo{
	Aresta **a;
	int numVertice;
	int numAresta;
};

typedef struct grafo Grafo;

Aresta** inicializarMatriz( int v){

	Aresta** a = (Aresta**)malloc(v*v*sizeof(Aresta*));

	for (int i=0; i<v; i++){
		a[i]=(Aresta*)malloc(v*sizeof(Aresta));
	}
	for(int i=0;i<v; i++){
		for(int j=0; j<v;j++){
		a[i][j].c='0';
	}
	}
			return a;
}


Grafo* definirAresta(Grafo*g, int v){

	char** nome = (char**)malloc(v*sizeof(char*));
	for(int i=0; i<v; i++) {
			nome[i]=(char*)malloc(v*v*sizeof(char));
			scanf("%s",nome[i]);
			}

	for(int i=0;i<v; i++){
		for(int j=0; j<v;j++){

		g->a[i][j].v1=nome[i];
		g->a[i][j].v2=nome[j];

	}
	
}

	return g;

}


void printar(Grafo *gr){
	for(int i=0; i<gr->numVertice; i++) {
		for(int j=0; j<gr->numVertice; j++){
			printf("(%s, %s, %c)", gr->a[i][j].v1,gr->a[i][j].v2,gr->a[i][j].c);
		}
		printf("\n");
	}
}

Grafo* criar_grafo( int v){

	Grafo* g = (Grafo*)malloc(sizeof(Grafo));
	g->numVertice=v;
	g->numAresta=0;
	//g->a=NULL;
	g->a=inicializarMatriz(v);
	
	return g;

}

Grafo* inserir_aresta(Grafo* g, int linha, int col){
	if(g->a[linha][col].c=='0'){
		g->a[linha][col].c='1';
		g->numAresta++;
	}

	return g;

}


int main()
{
	printf("Digite a quantidade de vértices do grafo:\n");
	int v;
	scanf("%d",&v);
	Grafo *g = criar_grafo(v);
	printf("Digite nomes dos vértices:\n");
	g=definirAresta(g,v);
	system("clear");
	printar(g);
	
}
