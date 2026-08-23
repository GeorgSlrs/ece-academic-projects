#include <stdio.h>
#include <stdlib.h>

#define SIZE 10

void print_memory_size(char* tbl_char, int *tbl_int, double *tbl_double);

int main(void)
{
 char array_char[SIZE];
 int array_int[SIZE];
 double array_double[SIZE];
 print_memory_size(array_char, array_int, array_double);
 return 0;
}

void print_memory_size(char* tbl_char, int * tbl_int, double *tbl_double)
{

 printf("Size in bytes of the different arrays: char %d bytes | int %d bytes | double %d bytes", (int) sizeof(tbl_char[0]) * SIZE,  (int) sizeof(tbl_int[0]) * SIZE, (int) sizeof(tbl_double[0]) * SIZE);
}
