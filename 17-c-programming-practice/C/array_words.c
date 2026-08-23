#include <stdio.h>
#include <stdlib.h>

#define N 10
#define SIZE 512

int main(void)
{
    char *array[N];
    char buffer[SIZE];
    int i

    for (i = 0; i < N; i ++)
    {
        printf("Enter the %d string: ",i);
        gets(buffer);
    }
    return 0;
}