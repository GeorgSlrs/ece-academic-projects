#include <stdio.h>

int main(void)
{
    int dice1, dice2;
    int sum1 = 0,sum2 = 0;
    printf("Please give the value of the first dice of pl1: \n");
    scanf("%d",&dice1);
    sum1 += dice1;
    printf("Please give the value of the second dice of pl1: \n");
    scanf("%d",&dice1);
    sum1 += dice1;
    printf("Please give the value of the first dice of pl2: \n");
    scanf("%d",&dice2);
    sum2 += dice2;
    printf("Please give the value of the first dice of pl2: \n");
    scanf("%d",&dice2);
    sum2 += dice2;

    if (sum1 > sum2)
    {
        printf("Player 1 wins!\n");
    }
    else if (sum1 < sum2)
    {
        printf("Player2 wins!\n");
    }

    else
    {
        
        printf("It's a tie!\n");
    }

    return 0;

}