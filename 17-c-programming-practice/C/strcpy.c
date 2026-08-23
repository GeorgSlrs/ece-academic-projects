#include <stdio.h>
#include <string.h>

int main()
{
    char src[12] = "aaaaaaaaaaa";
    char dest[12] = "bbbbbbbbbbb";
    strncpy(dest, src,4);
    //strcpy and strncpy overrrides
    printf("src = %s, dest = %s", src, dest);
    return 0;
}