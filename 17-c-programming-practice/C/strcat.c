#include <stdio.h>
#include <string.h>

int main()
{
    char src[12] = "aaaaaaaaaaa";
    char dest[12] = "bbbbbbbbbbb";
    printf("strlen of dest before strcat : %d ",strlen(dest));
    strcat(dest, src);
    printf("strlen of dest after strcat : %d ",strlen(dest));
    printf("src = %s, dest = %s", src, dest);
    return 0;
}