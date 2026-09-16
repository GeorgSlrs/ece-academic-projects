/*
 Version 5*/
#include <stdio.h>
#include <stdio.h>
int getchoice(void);
int getsize(void);
void oof(int size,int copies); /* Aυτή η συνάρτηση εκτυπώνει το 1ο σχήμα το τραπέζιο-δεν την ονόμασα printtrapezoid διότι δε δούλευε και δεν είχα το επιθυμητό αποτέλεσμα */
void printrhombus(int size,int copies);
void printrighttriangle(int size,int copies);
void printisoscelestriangle(int size,int copies);
void printspace(void);
void printsymbol(void);
void printnewline(void);
void printrowno(int i);
int getcopies(void);



int main(void)
{
    int choice = 0;
    int size;
    int copies;
    for(; (choice = getchoice()) != -1 ;)
    {
        size = getsize();
        copies = getcopies();


        if(choice == 0)
        {
            oof(size,copies);
        }


        else if(choice == 1)
        {
            printrhombus(size,copies);
        }


        else if(choice == 2)
        {
            printrighttriangle(size,copies);
        }


        else if (choice == 3)
        {
            printisoscelestriangle(size,copies);
        }



    }

    return 0;

}



int getchoice(void)
{
    int choice;
    printf("Please enter which shape you want to be printed (0-3):\n");
    scanf("%d",&choice);
    printf("Your choice is %d\n",choice);
    return choice;
}




int getsize(void)
{
    int size;
    printf("Please enter the number of rows-the size of your shape:\n");
    scanf("\n%d",&size);
    printf("Your size is %d\n",size);
    return size;

}

void oof(int size,int copies) /* εκτυπώνει το 1ο σχήμα -το τραπέζιο*/
{
    int i,j,k,l;
    for(i = 0; i< size; i++)
    {
        for(l = 0; l<copies; l++)
        {


                    for(j = 0;j<i;j++)
                    {
                       printsymbol();
                    }


                for(k =0;k<size;k++)
                {
                    if(k == 0 || i == 0 ||  k == size-1 || i == size-1)
                    {
                        printrowno(i+1);

                    }
                    else  printsymbol();
                }

                for(k =0; k<size - i; k++)  /*¶μα θέλω τα αντίγραφα να είναι κολλητά πολύ απλά γράφω k<size-i-1 */
                {
                    printspace();
                }


        }
        printnewline();
    }

}







void printrhombus(int size,int copies)
{

   int i,j,k,l,m,z,rows1; /* Μπορώ να έχω ρόμβο μόνο με περιττό αριθμό γραμμών,δουλεύει και για άρτιο αλλά δε δίνει το επιθυμητό αποτέλεσμα */
   rows1 = (size/2)+1;
   for(i = 1;i<=rows1;i++)
   {
       for(k = 0; k<copies; k++)
       {

           for(j = 1;j<=((2*rows1)-1);j++)
           {
               if((j==(rows1+(i-1))) || j==(rows1-(i-1)))
                  {
                      printrowno(i);
                  }
                else if(j>rows1+i-1)
                {
                    printspace();
                }
                else if(j<rows1+i-1 && j!= rows1+1-i)
                {
                   printsymbol();
                }

           }



           for( l = 0; l<(size/2);l++)
           {
               printspace();
           }
       }

       printnewline();
   }

   for(z = rows1-1;z>=1;z--)
   {
       for(k = 0; k<copies; k++)
       {


           for(j=1;j<=((2*rows1)-1);j++)
           {
               if((j==(rows1+(z-1))) || j==(rows1-(z-1)))
                  {
                      printrowno(size-z+1);
                  }
                else if(j>rows1+z-1)
                {
                    printspace();
                }
                else if(j<rows1+z-1 && j!= (rows1+1-z))
                {
                    printsymbol();
                }




           }
           for(m = 0; m<size/2; m++)
           {
               printspace();
           }

       }
           printnewline();

   }

}



void printrighttriangle(int size,int copies)
{

   int rowno,colno,k,l;
   for(rowno = 1; rowno<=size; rowno++)
   {
       for(k = 0; k<copies; k++)
       {

           for(colno = 1; colno<= rowno; colno++)
           {
               if ((colno==1) || (rowno == size) || colno == rowno)
               {
                   printrowno(rowno);
               }
               else if(colno>rowno)
               {
                  printspace();
               }
               else
               {
                   printsymbol();

               }
           }
           for(l = 0; l<size-rowno+1; l++)
           {
               printspace();
           }
        }
       printnewline();
   }
}




void printisoscelestriangle(int size,int copies)
{
    int i,j,k,l;
    for(i = 1; i<= size; i++)
    {
        for(k = 0; k<copies; k++)
        {


            for(j = 1;j<= ((2*size)-1);j++)
            {
                if(j ==(size-(i-1)) ||j == (size+(i-1))|| i == size)
                {
                    printrowno(i);
                }
                 if (j<size-(i-1))
                {
                    printspace();
                }
                if(j>(size-(i-1)) && j<(size +(i-1))&& i!= size)
                {
                    printsymbol();
                }
            }
            for(l = 0; l<size-i+1; l++)
            {
                printspace();
            }

        }
        printnewline();

    }
}





void printspace(void)
{
    printf(" ");
    return;
}



void printsymbol(void)
{
    printf("-");
    return;
}



void printrowno(int i)
{

    printf("%d",i);
    return;
}



void printnewline(void)
{
    printf("\n");
    return;
}

int getcopies(void)
{
    int copies;
    printf("Please enter number of copies:\n");
    scanf("\n%d",&copies);
    return copies;
}
