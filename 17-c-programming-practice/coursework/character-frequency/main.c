#include <stdio.h>
#include <stdlib.h>
#include <string.h>


struct charact
{
    char ch;
    int occurs;
    struct charact *next;
};


typedef struct charact Char;
typedef Char * ListofChar;
typedef Char * CharNode_ptr;
void letters(char name[50], ListofChar * chars_ptr);
void report(ListofChar chars);
Char * createnode(char ch);


int main(void)
{
    char name[50];
    ListofChar chars = NULL;
    scanf("%49s", name);
    letters(name, &chars);
    report(chars);
    return 0;
}


Char * createnode(char ch)
{
    CharNode_ptr newnode_ptr ;
    newnode_ptr = malloc(sizeof (Char));
    newnode_ptr -> ch = ch;
    newnode_ptr -> occurs = 0;
    newnode_ptr -> next = NULL;
    return newnode_ptr;
}


void letters(char name[50], ListofChar * lst_ptr)
{
    int i = 0;
    ListofChar *iterator = NULL;
    ListofChar iterator2 = NULL;
    ListofChar iterator3 = NULL;

    iterator = lst_ptr;

    for(i = 0;  i<strlen(name) ; i++)
    {
        *iterator = createnode(name[i]);
          iterator = &(*iterator)->next;
    }

    for(iterator2 = *lst_ptr ; iterator2!= NULL ; iterator2 = iterator2->next)
    {
        for(iterator3 = *lst_ptr ; iterator3!=NULL ; iterator3 = iterator3->next)
        {
            if(iterator2 ->ch == iterator3->next->ch)
            {
                continue;
            }

            /*’μα ο χαρακτήρας της λέξης που θέλω δεν είναι ίσως με τον επόμενο του αυξάνω την απόσταση κατά 1*/
            /*Αυτό προυποθέτει όμως ότι δεν έχω 2 διαδοχικούς χαρακτήρες είναι ίδιοι και ότι κάθε χαρακτήρας υπάρχει 2η φορά στη συμβολοσειρα*/
            else if(iterator2->ch != iterator3->next->ch)
            {
                iterator2->occurs++;
            }
        }
    }
    return;
}


void report(ListofChar chars)
{
    ListofChar iterator = NULL;

    for(iterator = chars; iterator!= NULL; iterator = iterator->next)
    {
        printf("\n character : %c   occurs = %d",iterator -> ch, iterator->occurs);
    }

    return;
}
