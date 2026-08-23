#include <stdio.h>

int main(void)
{
    int x,y,z;
    int max;
    printf("Please give the first number\n");
    scanf("%d",&x);
    max = x;
    printf("Please give the second number\n");
    scanf("%d",&y);
    printf("Please give the third number\n");
    scanf("%d",&z);
    if (max < y)
    {
        max = y;
    }
    if (max < z)
    {
        max = z;
    }

    printf("The highest number of those 3 has a value of %d.", max);
    return 0;
}