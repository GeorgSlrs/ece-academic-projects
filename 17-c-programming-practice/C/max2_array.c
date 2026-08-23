#include <stdio.h>
#include <stdlib.h>
#include <time.h>

#define N 25

void max2_array(int *array, int *max1, int *max2);

int main(void)
{
    int array_tested[N];
    int i, max1, max2;
    srand(time(NULL));

    for (i = 0; i < N; i ++)
    {
        array_tested[i] = rand()%500;
    }

    for(i = 0; i < N; i ++)
    {
        printf("%d\t",array_tested[i]);
        if ((i + 1) % 6 == 0) // +1 added so it prints a newline after every 6 numbers
        {
            printf("\n");
        }
    }

    printf("\n");
    max2_array(array_tested, &max1, &max2);
    printf("max1 : %d\t max2 : %d", max1, max2);

    return 0;
}

void max2_array(int *array, int *max1, int *max2)
{
    *max1 = array[0];
    *max2 = array[1];

    if (*max1 < *max2) 
    {
        // Swap max1 and max2 if max1 is less than max2
        int temp = *max1;
        *max1 = *max2;
        *max2 = temp;
    }

    for (int i = 2; i < N; i++) // Starting from 2 as we have already considered first two elements
    {
        if (array[i] > *max1) 
        {
            *max2 = *max1;
            *max1 = array[i];
        } 
        else if(array[i] > *max2 && array[i] != *max1) 
        {
            *max2 = array[i];
        }
    }
}
