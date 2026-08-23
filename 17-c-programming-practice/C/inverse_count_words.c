#include <stdio.h>
#include <string.h>
#include <stdlib.h>

#define N 1024

void inverse(char *s, char *invs);
int count_words(char *s); 


int main(void)
{
    char text[N+1];
    char inversetext[N+1];
    printf("Please enter text:" );
    scanf("%1024[^\n]",text);
    inverse(text, inversetext);
    printf("Inverse text:%s \n ",inversetext);
    printf("words:%d \n",count_words(text));
}


void inverse(char *s, char *invs)
{
    if (strcmp("",s))
    {
        printf("Cannot inverse <Enter>.\n");
        exit(1);
    }
    else
    {
        for (size_t i = 0; i < strlen(s); i++) 
        {
            invs[i] = s[strlen(s)-i-1];
        }
        invs[strlen(s)] = '\0';
    }
}


int count_words(char *s)
{
    //does not count spaces as words
    // maybe we have to include other types of spaces like "\t"?? IDK

    int number_of_words = 0;
    char* words = strtok(s, " ");
    while (words!= NULL)
    {
        words = strtok(NULL, " ");
        number_of_words++ ;
    }
    return number_of_words;
}
