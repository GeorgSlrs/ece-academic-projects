#include <stdio.h>
#include <stdlib.h>
#include <time.h>


int main(void)
{
    int hidden, guessed;

    srand(time(NULL));

    hidden = rand()%100;
    do
    {
        printf("\nPlease enter the hidden number!\n");
        scanf("%d",&guessed);

        if (hidden > guessed) printf("\nPlease enter a larger number!\n");
        else if (hidden < guessed) printf("\nPlease enter a smaller number!\n");
        else printf("You have found the hidden number! It is %d", hidden);
    } while (hidden != guessed);
    
    return 0;
}