#include <stdio.h>
#include <stdlib.h>

#define SIZE 10

int main(void)
{
 char array_char[SIZE];
 int array_int[SIZE];
 double array_double[SIZE];
 printf("Size in bytes of the different arrays: char %d bytes | int %d bytes | double %d bytes", (int) sizeof(char) * SIZE,  (int) sizeof(int) * SIZE, (int) sizeof(double) * SIZE);
 return 0;
}