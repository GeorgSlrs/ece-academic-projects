#include <stdio.h>

#define SIZE 5

int main(void)
{
	int pinakas[SIZE];
	int i;
	int sum;
	
	
	for (i=0; i<SIZE; i++)
	{
		printf("Please enter the %d-th number: ", i+1);
		scanf("%d",&pinakas[i]);
	}
	
	
	
	sum=0;
	for (i=0; i<SIZE; i++)
	{
		sum=sum+pinakas[i];
	}
	
	printf("The sum of the given numbers is: %d", sum);
	
    return 0;
}