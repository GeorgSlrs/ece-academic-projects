#include <stdio.h>

int main()
{
    const int i = 100;
    int j;

    printf("Please give the integer value of the variable: \n ");
    scanf("%d", &j);
    printf("const = %d, var = %d", i, j);
}