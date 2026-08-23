#include <stdio.h>
#define SIZE 150


int main(void)
{
    char str[SIZE];
    int i;

    printf("Please enter the string: \n");
    gets(str);

    while (str[i] != '\0')
    {

        if(str[i] >= 'a' && str[i] <= 'z')
        {
            str[i]-=32;
        }
        i++;
    }

    printf("\nNew string is %s",str);
    return 0;
}