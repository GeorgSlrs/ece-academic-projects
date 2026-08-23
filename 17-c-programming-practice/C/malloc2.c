#include <stdio.h>
#include <stdlib.h>
#include <time.h>

#define SIZE 20

int main(void)
{
	int st_array[SIZE][SIZE];
	int **dyn_array;
	int N; 
	int i,j;
	
	srand(time(0));
	
	/* Static Array */ 
	
	do {
		printf("Enter N: \n");
		scanf("%d", &N);
		
		if (N<5 || N>20)
			printf("Wrong Input (5..20). \n");
	} while (N<5 || N>20);
	
	for (i=0; i<N; i++)
	{
		for (j=0; j<=i; j++)
			st_array[i][j]=1+rand()%(8+1);
		
		for (j=i+1; j<N; j++)
			st_array[i][j]=0; 
	}
	
	printf("Static array: \n");
	for (i=0; i<N; i++)
	{
		for (j=0; j<N; j++)
			printf("%d ", st_array[i][j]);
		printf("\n");
	}
	
	/* Dynamic Array */
	
	dyn_array = (int **)malloc(N*sizeof(int *));
	if (!dyn_array)
	{
		printf("Memory allocation failed!\n");
		exit(0);
	}
	
	for (i=0; i<N; i++)
	{
		dyn_array[i]=(int *)malloc((i+1)*sizeof(int));
		if (!dyn_array[i])
		{
			printf("Memory allocation failed!\n");
			exit(0);
		}			
	}

	for (i=0; i<N; i++)
	{
		for (j=0; j<=i; j++)
			dyn_array[i][j]=1+rand()%(8+1);
	}
	
	printf("Dynamic Array: \n");
	for (i=0; i<N; i++)
	{
		for (j=0; j<=i; j++)
			printf("%d ", dyn_array[i][j]);
			
		for (j=i+1; j<N; j++)
			printf("0 ");
		printf("\n");
	}

	/* Copy from static to dynamic */
	
	for (i=0; i<N; i++)
		for (j=0; j<=i; j++)
			dyn_array[i][j]=st_array[i][j];
			
	/* Printing the 2 arrays */ 
	
	printf("Static Array: \n");
	for (i=0; i<N; i++)
	{
		for (j=0; j<N; j++)
			printf("%d ", st_array[i][j]);
		printf("\n");
	}
	
	printf("Dynamic array: \n");
	for (i=0; i<N; i++)
	{
		for (j=0; j<=i; j++)
			printf("%d ", dyn_array[i][j]);
			
		for (j=i+1; j<N; j++)
			printf("0 ");
		printf("\n");
	}
	
	for (i=0; i<N; i++)	
		free(dyn_array[i]);
	free(dyn_array);

	return 0;
					
}