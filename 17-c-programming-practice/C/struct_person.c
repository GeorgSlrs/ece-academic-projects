#include <stdio.h>

#define SIZE 80

struct person
{
    char name[SIZE];
    char address[SIZE];
    char number[SIZE];
    char district[SIZE];
};

typedef struct person RECORD;

void read_record(RECORD *p);
void print_record(RECORD x);


int main()
{
    RECORD a,b;
    printf("1st person: \n");
    read_record(&a);
    printf("\n2nd person: \n");
    read_record(&b);
    print_record(a);
    print_record(b);
    
    return 0;
}

void read_record(RECORD *p)
{
    printf("\nPlease enter the name: \n");
    scanf("%s", p->name);
    printf("\nPlease enter the address: \n");
    scanf("%s", p->address);
    printf("\nPlease enter the number: \n");
    scanf("%s", p->number);
    printf("\nPlease enter the district: \n");
    scanf("%s", p->district);
}


void print_record(RECORD x)
{
    printf("%s -- %s -- %s -- %s",x.name, x.address, x.number, x.district);
}