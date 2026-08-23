#include <stdio.h>
#include <stdlib.h>
#include <time.h>

#define SIZE1 100
#define SIZE2 200   

int main(void)
{
    int array[SIZE1][SIZE2];
    int N,M;

    do
    {
        printf("Please enter M: \n");
        scanf("%d",&M);
    } while (M < 10 && M > 100);
    
    do
    {
        printf("\nPlease enter N: \n");
        scanf("%d",&N);
    } while (N < 20 && N > 100);

    for(int i =0; i < N; i ++)
    {
        for(int j = 0; j < M; j++)
        {
            array[i][j] = rand();
        }
    }

    for(int i =0; i < N; i ++)
    {
        for(int j = 0; j < M; j++)
        {
            printf("%d\t",array[i][j]);
        }
        
        printf("\n");
    }

    return 0;
}