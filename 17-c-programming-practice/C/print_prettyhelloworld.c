#include <stdio.h>

#define M 20
#define N 4

int main(void)
{
	int i;
	
	//1st line
	printf("\n\n\n\n\t\t%c",201);
	for (i=1; i<=M; i++)
		printf("%c", 205);
	printf("%c",187);
	
	//2nd line
	printf("\n\t\t%c",186);
	for (i=1; i<=N; i++)
		printf(" ", 205);
	printf("Hello World!");
	for (i=1; i<=N; i++)
		printf(" ", 205);
	printf("%c",186);
	
	//3rd line
	printf("\n\t\t%c",200);
	for (i=1; i<=M; i++)
		printf("%c", 205);
	printf("%c\n\n\n\n",188);	

	
}