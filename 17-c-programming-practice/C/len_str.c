#include <stdio.h>

int main(void)
{
    int i = 0;
    char string [1000] = {};

    printf("Please enter a string: \n");

    gets(string);

    while (string[i] != '\0')
    {
        i++;
    }

    printf("The length of the provided string-excluding '\\0' is %d", i);

    return 0;
}