#include <stdio.h>

int main(void)
{
    int x,y,z;
    int max,min,mid;

    printf("Please give the first number: \n");
    scanf("%d", &x);
    printf("Please give the second number: \n");
    scanf("%d", &y);
    printf("Please give the third number: \n");
    scanf("%d", &z);

    max = x;
    min = x;
    mid = x;
    if (max < y)
    {
        max = y;
        
    }

    if (max < z)
    {
        max = z;
    }

    if (min > y)
    {
        min = y;
    }

    if (min > z)
    {
        min = z;
    }

    if (!min<=mid<=max)
    {
        mid = y;
        if (!min<=mid<=max)
        {
            mid = z;
        }
    }

    printf("The 3 numbers in ascending order are: %d, %d, %d", min, mid, max);

    return 0;

}