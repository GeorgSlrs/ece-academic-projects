#include <stdio.h>

int main(void)
{
    for(int i = 1; i <= 5; i++)
    {
        for(int j = 1; j < 4*5; j++)
        {
           if (j%2 != 0)
           {
                printf("%d",j%5);
           }
           else if (j%2 == 0)
           {
            printf("%d");
           } 
        }
    }
    return 0;-
}