#include <stdio.h>

int get_integer(int start, int finish);

int main (void)
{
    printf("Integer = %d", get_integer(2,20));
    return 0;
}

int get_integer(int start, int finish)
{
    int x;

    
    do
    {
        printf("Please enter a number between %d and %d\n",start, finish);
        scanf("%d",&x);
    }while (x < start || x > finish);

    return x;
}