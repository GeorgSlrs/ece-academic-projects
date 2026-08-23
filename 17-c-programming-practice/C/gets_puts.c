#include <stdio.h>

int main()
{
    char string[100];

    printf("Enter the string: \n");
    gets(string);
    printf("You entered: ");
    puts(string);
    return 0;
}