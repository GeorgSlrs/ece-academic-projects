#include <stdio.h>
#include <stdlib.h>

int main(void)
{
    int M,N;
    double **p;

    printf("Please enter M: \n");
    scanf("%d",&M);

    printf("\nPlease enter N: \n");
    scanf("%d",&N);

    p = malloc(sizeof(double *) * M);
    if (!p)
    {
        printf("Memory not successfully allocated!.\n");
        exit(1);
    }

    for (int i = 0; i < M; i ++)
    {
        p[i] = malloc(sizeof(double) * N);
        if (!p[i])
        {
            printf("Memory not successfully allocated!.\n");
             exit(1);
        }
    }

    printf("\nMemory that was allocated(in bytes) was: %d.", M*N*sizeof(double)+M*sizeof(double *) + sizeof(p));

    //free the dynamically allocated memory
    for (int i = 0; i < M; i++)
    {
        free(p[i]);
    }

    free(p);

    return 0;
}