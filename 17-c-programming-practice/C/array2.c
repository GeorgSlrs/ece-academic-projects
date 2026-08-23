#include <stdio.h>
#include <stdlib.h>
#include <time.h>

#define N 5
#define M 8


int main(void)
{
    int array[N][M];

    srand(time(NULL));

    for(int i =0; i < N; i ++)
    {
        for(int j = 0; j < M; j++)
        {
            array[i][j] = rand()%200;
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