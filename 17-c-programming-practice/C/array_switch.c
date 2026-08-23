#include <stdio.h>
#include <stdlib.h>
#include <time.h>

#define SIZE 1000

void init_array(int *pinakas, int n, int a, int b);
void print_array(int *pinakas, int n);
int max_array(int *pinakas, int n);

int main(void)
{
	int array[SIZE],N;
	int choice,a,b;
	
	while (1)
	{
		system("cls");
		printf("\n\nMenu");
		printf("\n--------------");
		printf("\n1-Enter the size of the array");
		printf("\n2-Initialization of the array");
		printf("\n3-Find the element of the array with the max value");
		printf("\n4-Print the array");
		printf("\n5-Exit");
		printf("\n Choice? ");
		scanf("%d", &choice);
		
		switch(choice)
		{
			case 1:
				printf("Please give the size of the array: \n");
				scanf("%d", &N); 
				break;
			case 2:
				printf("Please give the start of the interval: \n");
				scanf("%d",&a);
				printf("Please enter the end of the interval: \n");
				scanf("%d",&b);
				init_array(array, N, a, b);	
				break;
			case 3:
				printf("Largest element is: %d", max_array(array, N));
				break;
			case 4:
				print_array(array, N);
				break;
			case 5:
				printf("Bye Bye");
				exit(0);	
			default:
				printf("Wrong input! ");		
		}
		
		printf("\n\n");
		system("pause");
				
	}
    return 0;
}

void init_array(int *pinakas, int n, int a, int b)
{
	int i;
	
	srand(time(NULL));
	
	for (i=0; i<n; i++)
		pinakas[i]=a+rand()%(b-a+1);
}

void print_array(int *pinakas, int n)
{
	int i;
	
	printf("[");
	for (i=0; i<n-1; i++)
		printf("%d, ",pinakas[i]);
	printf("%d]",pinakas[n-1]);
}

int max_array(int *pinakas, int n)
{
	int i,max;
	
	max=pinakas[0];
	
	for (i=1; i<n; i++)
	{
		if (pinakas[i]>max)
			max=pinakas[i];
	}
	
	return max;
}