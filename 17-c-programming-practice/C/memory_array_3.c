#include <stdio.h>
#include <stdlib.h>
#include <time.h>

#define SIZE 10

void initialize(char* tbl_char, int * tbl_int, double []);
void print(char [], int [], double []);


int main(void)
{
 char array_char[SIZE];
 int array_int[SIZE];
 double array_double[SIZE];
 initialize(array_char,&array_int[0],&array_double[0]);
 print(array_char,array_int,array_double);
 return 0;
}


void initialize(char* tbl_char, int * tbl_int, double tbl_double[])
{
    srand(time(NULL));
    for(int i = 0; i < SIZE; i++)
    {
        tbl_char[i] = 'a';
        tbl_int[i] = 1;
        tbl_double[i] = 1.00;
    }
}


void print(char tbl_char[], int tbl_int[], double tbl_double[])
{
 int index;
 for (index = 0; index < SIZE; index++) { 
 printf(" %d \t tbl_char value %c \n", index, tbl_char[index]);
 printf(" %d \t tbl_int value %d \n", index, tbl_int[index]);
 printf(" %d \t tbl_double value %.3f \n", index, tbl_double[index]);
 }
}