#include <stdio.h>

#define N 20


int main(void)
{
    int matrix[N];
    int i;
    int min;


    matrix[0] = 3;

    for (i = 0; i < N; i++)
    {
        printf("Please enter the %d - th number\n", i + 1);
        scanf("%d", &matrix[i]);
        if ((!(matrix[i] >= 2 && matrix[i] <= 20)))
        {   do
            {
                printf("Please enter a number between 2 and 20\n");
                scanf("%d", &matrix[i]);
            } while ((!(matrix[i] >= 2 && matrix[i] <= 20)));
        }
        if (min > matrix[i])
            {
                min = matrix[i];
            }
    }

    printf("The lowest number given is %d", min);
    
    return 0;
}