#include <stdio.h>
#include <stdlib.h>
#include <time.h>

#define N 20


void init_array(int *array, int n, int a, int b);
void print_array(int *array, int n);
int max_array(int *matrix, int n);

int main (void)
{
    int array[N];

    init_array(array,N,0,50000);
    print_array(array,N);
    printf("\nThe max value element of the array is %d.",max_array(array, N));
    return 0;
}

void init_array(int *array, int n, int a, int b)
{
    srand(time(NULL));
    for(int i = 0; i < n; i++)
    {
        array[i] = a + rand()%(b-a+1);
    }
}

void print_array(int *array, int n)
{
    for(int i = 0; i <n; i ++)
    {
        if (i % 8 == 0)
        {
            printf("\n");
        }
        printf("%d\t", array[i]);
    }
}

int max_array(int *matrix, int n)
{
    int max = matrix[0];
    for (int i = 1; i < n; i ++)
    {
        if (max < matrix[i]) max = matrix[i];
    }

    return max;
}