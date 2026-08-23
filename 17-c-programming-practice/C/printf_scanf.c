#include <stdio.h>

#define SIZE 100

int main()
{
    char string[SIZE];
    int ret;
    printf("Enter the string: \n");
    
    ret = scanf("%s", string); //stops in whitespaces
    printf("You entered: %s.Return value of scanf: %d", string, ret);
    return 0;
}