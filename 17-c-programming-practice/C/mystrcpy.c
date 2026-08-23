#include <stdio.h>
#include <string.h>


#define SIZE 255
char *mystrcpy(char *dest, const char *src);

int main(void)
{
    char string1[SIZE], string2[SIZE];

    printf("Please enter a string!: \n");
    fgets(string1, SIZE, stdin); // This reads the string including the newline

    // Removing the trailing newline character
    size_t len = strlen(string1);
    if (len > 0 && string1[len - 1] == '\n') {
        string1[len - 1] = '\0';
    }

    mystrcpy(string2, string1);
    printf("The given string is: %s. The new copied string is: %s\n", string1, string2);
    return 0;
}

char *mystrcpy(char *dest, const char *src)
{
    int i = 0;

    while (src[i] != '\0')
    {
        dest[i] = src[i];
        i++;
        // If you want to see the copying process in action, uncomment the next line.
        // printf("Test\n"); 
    }

    dest[i] = '\0';
    return dest;
}
