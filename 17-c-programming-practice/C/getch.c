#include <stdio.h>
#include <conio.h>

int main()
{
   char c;

   c=getch();
   while(c!='x')
   {
      printf("%c,",c);
      c=getch();
   }
   printf("%c.",c);

   return 0;
}
