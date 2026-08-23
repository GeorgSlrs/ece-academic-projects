#include <stdio.h>

int main()
{
    char string[100];
    int i = 1;


    printf("Enter the string: \n");
     getchar();
    while (c!= '\n');
    {
        string[i] = getchar();

        i++;
    }
    string[i] = '\0';

    printf("You entered: ");
    
    i = 0;

    while (string[i] != '\0')
    {
        putchar(string[i]);
        i++;
    }
    return 0;
}