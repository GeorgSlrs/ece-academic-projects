#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>


#define NUM_CHARS 1000000

void initialize(char src[]);
void copy_with_loop(char dst[],char src[]);
void copy_with_memcpy(char dst[],char src[]);


int main(void)
{
    char src[NUM_CHARS];
    char dst[NUM_CHARS];
    // initialize source string with random characters
    initialize(src);
    //copy source string to destination string using loop & print the time needed
    copy_with_loop(dst,src);
    //copy source string to destination string using memcpy & print the time needed
    copy_with_memcpy(dst,src);
    return 0;
}


void initialize(char src[])
{
    for(int i = 0; i < NUM_CHARS; i++)
    {
        src[i] = 'a' + rand() %26;
    }
}


void copy_with_memcpy(char dst[],char src[])
{
    clock_t start, end;

    start = clock();
    memcpy(dst, src, sizeof(char));
    end = clock();
    printf("Time taken to copy string using memcpy: %7f seconds.\n", ((double) (end - start)) / CLOCKS_PER_SEC);
}


void copy_with_loop(char dst[],char src[])
{
    clock_t start, end;

    start = clock();
    for (int i = 0; i < NUM_CHARS; i++)
    {
        dst[i] = src[i];
    }
    end = clock();
    printf("Time taken to copy string using loop: %7f seconds.\n", ((double) (end - start)) / CLOCKS_PER_SEC); 
}