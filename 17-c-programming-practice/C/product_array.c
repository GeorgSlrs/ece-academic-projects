#include <stdio.h>

#define SIZE 10


int main(void)
{
    int matrix[SIZE];
    
    int i;

    int product = 1;

    for (i = 0; i < 10; i++)
    {
        printf("Please enter the %d-th number \n", i + 1);
        scanf("%d", &matrix[i]);
        while (matrix[i] > 8 || matrix [i] < 1)
        {
            printf("Please enter an integer between 1 and 8 \n");
            printf("Please enter the %d-th number \n", i + 1);
            scanf("%d", &matrix[i]);
        }
    }


    for (i = 0; i < SIZE; i++)
    {
        product *= matrix[i];
    }

    printf("The product is %d", product);
    return 0;
}