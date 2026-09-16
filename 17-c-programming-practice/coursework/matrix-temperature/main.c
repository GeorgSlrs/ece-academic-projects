/*Version 3 */
/*Stable condition = when the sum of the ablsolute values of 2 consecutive arrays is less than 1 */


#include <stdio.h>
#define N 10
#define M 20

void loadmatrix(float matrix[N][M]);
void printspace();
void printnewline(void);
void printmatrix(const float matrix[N][M]);
void changematrix(float matrix [N][M],int time);
float findmax(const float matrix [N][M]);
float findmin(const float matrix [N][M]);
void changematrix_again(float matrix [N][M],float min,float max);
void printnewmatrix(const float matrix[N][M]);
void loadmatrix_again(float matrix [N][M]);
void makeistogram(const float matrix[N][M]);
void printnum_same_temp(int x,int y);
float absolute_value(float x,float y);
int stable_condition(const float matrix[N][M], const float newmatrix[N][M]);
void findwhenstable_condition(float matrix[N][M],float newmatrix[N][M]);







int main()
{

    int time = 0;

    float newmatrix[N][M] = {{}};



    float matrix[N][M] = {{}};
    loadmatrix(matrix);
    loadmatrix_again(matrix);
    loadmatrix(newmatrix);
    loadmatrix_again(newmatrix);  /*Για να βρω πότε έχω σταθερή κατάσταση δημιουργώ ένα νέο πίνακα αρχικά ίδιο με τον αυθεντικό.Στη συνέχεια θα τον τροποποιήσω με βάση τη συνάρτηση changematrix αλλά αντί για
                                    time θα βάλω time +1 για να πάρω την αμέσως επόμενη κατάσταση της πλάκας και με βάση εκείνη και εκείνη που θέλει ο χρήστης να δω αν έχω σταθερή κατάσταση */
    printf("Time = 0\n");
    printmatrix(matrix);
    printnewline();
    printnewline();
    printnewline();


    /*time = -1 -> termination */
    while(time!= -1)
    {
        int c;
        float max;
        float min;
        printf("Please enter time in seconds(Enter -1 to exit the program):\n");
        scanf("\n%d",&time);
        if(time = -1)
        {
            break;
        }
        else
        {
            findwhenstable_condition(matrix,newmatrix);
            changematrix(matrix,time);
            changematrix(newmatrix,time+1);


            c = stable_condition(matrix,newmatrix);
            if(c == 0)
            {
                printf("\n Not a stable condition \n");
            }

            else if(c == 1)
            {
                printf("\n Stable condition \n");
            }

            changematrix(matrix,time);


            max = findmax((const float (*)[M])  matrix);
            min = findmin((const float (*)[M]) matrix);
            changematrix_again(matrix,min,max);


            printf("\nThe normalised temperatures: \n");
            printf("\nTime = %d\n",time);
            printnewmatrix(matrix);
            makeistogram(matrix);
            loadmatrix(matrix);
            loadmatrix_again(matrix);
            loadmatrix(newmatrix);
            loadmatrix_again(newmatrix);
        }


    }
    printf("End of the program");

return 0;


}



void printspace(void) /*Aυτή και η επόμενη δεν είναι και τόσο απαραίτητες */
{
    printf(" ");
}



void printnewline(void)
{
    printf("\n");
    return;
}



void loadmatrix(float matrix [N][M]) /*Δημιουργώ μία συνάρτηση η οποία αρχικοποιεί τα μη γωνιακά στοιχεία της πλάκας
                                       Για να αρχικοποιήσω τα γωνιακά στοιχεία της πλάκας χρησιμοποιώ τη συνάρτηση                                       loadmatrix_again */
{
    int i,j;

    for(i = 0; i < N; i++)
    {
        for(j = 0; j < M; j++)
        {
            if((i == 0 && j == 0) || (i == 0 && j == M-1) || (i == N-1 && j == 0) || (i == N-1 && j == M-1))
            {
                matrix[i][j] = 0.00;
            }



            else if(i == 0 && j > 0 && j < M-1)
            {
                matrix[i][j] = 2.00;
            }

            else if(i == N-1 && j > 0  &&  j < M-1)
            {

                matrix[i][j] = 3.00;
            }


            else if (j == 0 && i!= 0 && i!= N-1)
            {
                matrix[i][j] = 4.00;
            }


            else if (j == M-1 && i!= 0 && i!= N-1)
            {
                matrix[i][j] = -5.00;
            }

            else
            {
                matrix[i][j] = 1.00;
            }

        }
    }
    return;
}



void printmatrix(const float matrix[N][M])
{
    int i,j;
    for(i = 0; i < N; i++)
    {
        for(j = 0; j < M; j++)
        {

            if(matrix[i][j] >0)

            {
                printf("  %.2f",matrix[i][j]);

            }

            else if(matrix[i][j] < 0)
            {
                printf(" %.2f",matrix[i][j]);
            }
        }

        printnewline();
    }

    return;
}



void changematrix(float matrix [N][M],int time)
{


    if(time == 0)
    {
        loadmatrix(matrix);
    }
    else
    {   int t;

        for(t = 0; t < time; t++)
        { int i,j;


               for(i = 1; i < N; i++)
               {
                   for(j = 1; j < M; j++)
                   {

                    if( i!= N-1 && j!= M-1)
                    matrix[i][j] = 0.1*(matrix[i-1][j-1] + matrix[i-1][j] + matrix[i-1][j+1] + matrix[i][j-1] + 2*(matrix[i][j]) + matrix[i][j+1] + matrix[i+1][j-1] + matrix[i+1][j] + matrix[i+1][j+1]);

                   }
               }
        }
    }
  return;
}



float findmax(const float matrix[N][M])
{
    float max = 0.00;
    int i,j;
    for(i = 0 ; i < N; i++)
    {
        for(j = 0 ; j < M; j++)
        {
            if(max <= matrix[i][j])
            {
                max = matrix[i][j];
            }
        }
    }

    return max;
}



float findmin(const float matrix[N][M])
{
    int i,j;
    float min = 5.00;
    for(i = 0; i < N; i++)
    {
        for(j = 0; j < M; j++)
        {
            if(matrix[i][j] <= min)
            {
                min = matrix[i][j];
            }
        }
    }
    return min;
}



void changematrix_again(float matrix [N][M],float min,float max)
{
    int k,l;
    for(k = 0; k < N; k++)
    {
        for( l = 0; l < M; l++)
        {


            if( matrix[k][l] >= min && matrix[k][l] < ((float) (9*min + max) / 10))
            {
                matrix[k][l] = 0;
                continue;
            }

            if( matrix[k][l] >=((float) (9*min + max) / 10) && matrix[k][l] < ((float) (8*min + 2*max) / 10))
            {
                matrix[k][l] = 1;
                continue;
            }
            if( matrix[k][l] >= ((float) (8*min + 2*max) / 10) && matrix[k][l] < ((float) (7*min + 3*max) / 10))
            {
                matrix[k][l] = 2;
                continue;
            }
            if(matrix[k][l] >= ((float) (7*min + 3*max) / 10) && matrix[k][l] < ((float) (6*min + 4*max) / 10))
            {
                matrix[k][l] = 3;
                continue;
            }
            if(matrix[k][l] >= ((float) (6*min + 4*max) / 10) && matrix[k][l] < ((float) (5*min + 5*max) / 10))
            {
                matrix[k][l] = 4;
                continue;
            }
            if(matrix[k][l] >= (float) (5*min + 5*max) / 10 && matrix[k][l] < (float) (4*min + 6*max) / 10)
            {
                matrix[k][l] = 5;
                continue;
            }
            if(matrix[k][l] >= (float) (4*min + 6*max) / 10 && matrix[k][l] < (float) (3*min + 7*max) / 10)
            {
                matrix[k][l] = 6;
                continue;
            }
            if(matrix[k][l] >= (float) (3*min + 7*max) / 10 && matrix[k][l] < (float) (2*min + 8*max) / 10)
            {
                matrix[k][l] = 7;
                continue;
            }
            if(matrix[k][l] >= (float) (2*min + 8*max) / 10 && matrix[k][l] < (float) (min + 9*max) / 10)
            {
                matrix[k][l] = 8;
                continue;
            }
            if(matrix[k][l] >= (float) (min + 9*max) / 10 && matrix[k][l] <= max)
            {
                matrix[k][l] = 9;
                continue;
            }

        }

    }
    return;
}



void printnewmatrix(const float matrix[N][M])
{
    int i,j;
    for(i = 0; i < N; i ++)
    {
        for(j = 0; j < M; j++)
        {
          printf("%g",matrix[i][j]);
          printspace();
        }
        printnewline();
    }

    return;
}


void loadmatrix_again(float matrix [N][M])
{
    int i,j;
    for(i = 0; i < N; i++)
    {
        for(j = 0; j < M; j++)
        {
            if(i == 0 && j == 0)
            {
                matrix[i][j] = (float)((matrix[0][1] + matrix[1][0]) / 2);
            }


            if( i == 0 && j == M-1)
            {
                matrix[i][j] = (float) ((matrix[0][18] + matrix[1][19]) /2);
            }


            if( i == N -1 && j == 0)
            {
                matrix[i][j] = (float) ((matrix[8][0] + matrix[9][1]) / 2);
            }


            if( i == N-1 && j == M-1)
            {
                matrix[i][j] = (float) ((matrix[9][18] + matrix[8][19]) / 2);
            }

        }
    }
    return;
}



void makeistogram(const float matrix[N][M])
{
    int i,j;
    int a = 0,b = 0,c = 0,d = 0,e = 0,f = 0,g = 0,h = 0,k = 0,l = 0;

    for(i = 0; i < N; i++)
    {
        for(j = 0; j < M; j++)
        {
            if(matrix[i][j] == 0)
            {
                a++;
                continue;
            }

            if(matrix[i][j] == 1)
            {
                b++;
                continue;
            }

            if(matrix[i][j] == 2)
            {
                c++;
                continue;
            }

            if(matrix[i][j] == 3)
            {
                d++;
                continue;
            }

            if(matrix[i][j] == 4)
            {
                e++;
                continue;
            }
            if(matrix[i][j] == 5)
            {
                f++;
                continue;
            }

            if(matrix[i][j] == 6)
            {
                g++;
            }

            if(matrix[i][j] == 7)
            {
                h++;
                continue;
            }


            if(matrix[i][j] == 8)
            {
                k++;
                continue;
            }

            if(matrix[i][j] == 9)
            {
                l++;
                continue;
            }

        }
    }

    printnum_same_temp(a,0);
    printf("\n"); /*Δημιουργεί το ιστόγραμμα */
    printnum_same_temp(b,1);
    printf("\n");
    printnum_same_temp(c,2);
    printf("\n");
    printnum_same_temp(d,3);
    printf("\n");
    printnum_same_temp(e,4);
    printf("\n");
    printnum_same_temp(f,5);
    printf("\n");
    printnum_same_temp(g,6);
    printf("\n");
    printnum_same_temp(h,7);
    printf("\n");
    printnum_same_temp(k,8);
    printf("\n");
    printnum_same_temp(l,9);
    printf("\n");
    return;
}





void printnum_same_temp(int x,int y) /*Τυπώνει το ιστόγραμμα */
{
    int i;

    printf("\n");

    printf("%d : ",y);
    for(i = 0 ; i < x; i++)
    {
        printf("*");
    }
    printf(" (%d) ",x);
    return;

}



float absolute_value(float x,float y)
{
    if(x-y >= 0)
    {
        return x-y;
    }
    else
    {
        return y-x;
    }
}



int stable_condition(const float matrix[N][M],const float newmatrix[N][M])
{
    int i,j;
    float sum = 0.000000;
    for(i = 0; i < N; i++)
    {
        for(j = 0; j < M; j++)
        {
            sum = sum + absolute_value(matrix[i][j],newmatrix[i][j]);
        }

    }

    if(sum > 1.00)
    {


        return 0;

    }

    else
    {

        return 1;
    }
}



void findwhenstable_condition(float matrix[N][M],float newmatrix[N][M])
{
    int t = 0;
    int j = 0;
    for(t = 0; t<1000; t++)
    {
        loadmatrix(matrix);
        loadmatrix_again(matrix);
        loadmatrix(newmatrix);
        loadmatrix_again(newmatrix);
        changematrix(matrix,t);
        changematrix(newmatrix,t+1);
        if(stable_condition(matrix,newmatrix) == 0)
        {
            continue;

        }

        if(stable_condition(matrix,newmatrix) == 1)
        {
            printf("\nStable condtition for time = %d seconds\n",t);
            printmatrix(matrix);


            printnewline();
            break;
        }
    }


    return;

}
