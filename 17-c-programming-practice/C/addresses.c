#include <stdio.h>


void foo1(void);
void foo2(void);

int g;

int main(void)
{

 printf("foo1 address \t\t %lu \n", (unsigned long) (void*)(foo1) );
 foo1();
 printf("foo2 address \t\t %lu \n", (unsigned long) (void*)(foo2) );
 foo2();
 return 0; 

}


void foo1(void)
{

 int x,y;
 printf("x address \t\t %lu \n", (unsigned long) (void*)(&x) );
 printf("y address \t\t %lu \n", (unsigned long) (void*)(&y) );
 printf("g address \t\t %lu \n", (unsigned long) (void*)(&g) );
 return;

}


void foo2(void)
{

 int x, y;
 printf("x address \t\t %lu \n", (unsigned long) (void*)(&x) );
 printf("y address \t\t %lu \n", (unsigned long) (void*)(&y) );
 printf("g address \t\t %lu \n", (unsigned long) (void*)(&g) );
 return;
 
}