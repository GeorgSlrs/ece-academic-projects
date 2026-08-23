#include <stdio.h>
#include <string.h>

int main()
{
    char src[12] = "vd";
    char dest[12] = "bbbbbbbbbbb";
    memset(dest,'d',sizeof(char) * 5);
    printf("%s",dest);
    return 0;
}