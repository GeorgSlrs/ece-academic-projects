#include <stdio.h>

int main()
{
    int age = 0;
    printf("Please give me your age: \n");
    scanf("%d", &age);
    if (age < 18)
    {
        printf("You are not an adult!\n");
    }
    else
    {
        printf("You are an adult!\n");
        if (age > 66)
        {
            printf("You are retired!\n");
        }

        else
        {
            printf("You are not retired!");
        }
    }

    return 0;
}