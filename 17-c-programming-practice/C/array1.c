#include <stdio.h>
#include <stdlib.h>
#include <time.h>

#define SIZE 100

int main(void)
{
    int N;
    int array[SIZE];

    srand(time(NULL)); // new seed every time

    do
    {
        printf("Please enter the size of the matrix (between 21 and 99): \n");
        scanf("%d", &N);
    } while (N <= 20 || N >= 100);

    for (int i = 0; i < N; i++)
    {
        array[i] = rand() % 1000; // Assuming you want numbers in the range 0-999
    }

    for (int i = 0; i < N; i++)
    {
        if (i % 10 == 0 && i != 0)
        {
            printf("\n\n");
        }

        printf("%4d ", array[i]); // "%4d" formats the integer, aligning it to the right and padding with spaces
    }

    printf("\n");

    return 0;
}
