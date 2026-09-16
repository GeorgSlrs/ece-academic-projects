#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define MAX 100000
#define N 40
/*Version 4 */
/*Notes*/
/*Kάποιες συναρτήσεις δε χρειάζονται..Είναι κατάλοιπα του γράψε-σβήσε κώδικα */
/*Όπως καταλαβαίνετε έχω χρησιμοποιήσει stackoverflow και reddit για αρκετές απορίες που είχα */

int get_choice(void);
int check_word(char *word);
void insert_text(FILE ** p_fp);
char *add_word(char *word);
void add_word_in_dictionary(FILE ** p_fp);
void save_file(FILE **fp);
int count_characters(void);
int count_spaces(void);
void txt_to_array(char x[MAX][N],FILE **fp);
void sort_array_alphabetically(char matrix[MAX][N]);
int count_words_same(char matrix[MAX][N]);
void create_istogram(char matrix[MAX][N]);
void print_symbols(int times,int numch);
void create_file(char matrix[MAX][N]);
int count_words(void);
void init_file(FILE **dfp);
void correction_mode(void);
char* rename_file(char oldname[40]);
void txt_to_array2(char x[MAX][N],FILE **fp);

char matrix[MAX][N] = {" "};

int main()
{
    FILE **fp;
    FILE *fp2;  /*fp for Alice....txt and fp2 for englishWords.txt */
    int choice = 0;
    char matrix[MAX][N] = {" "};
    while(1)
    {
        choice = get_choice();

        if(choice == 0)
        {
            insert_text(fp);

        }

        if(choice == 1)
        {
            add_word_in_dictionary(&fp2);

        }

        if(choice == 2)
        {
            void correction_mode(void);

        }

        if(choice == 3)
        {
            save_file(fp);  /*Δεν καταλαβαίνω τι εννοεί η αποθήκευση αρχείου - απλά κλείνουμε το αρχείο;;; */
            printf("\n The file has been saved \n");

        }

        if(choice == 4)
        {
            printf("The number of character in the file : %d ",count_characters());
            printf("The number of spaces in the file : %d ",count_spaces());
            txt_to_array(matrix,fp); /*Μου πετάει error άμα βάλω &,πάλι μου πεταέι error άμα δε βάλω &....Tι συμβαίνει;;;;;;;;;;;;;;;;;  */
            printf("The number of different words in the file : %d ",count_words()- count_words_same(matrix));
            create_istogram(matrix);
            create_file(matrix);
            printf("\n A file has been created with the statistics of the text \n");
        }

        if(choice == 5)
        {
            break;
        }

    }

    printf("\n The program has ended \n");
    return 0;
}



int get_choice(void) {
    int choice = 0;
    printf("\n Select a choice from  the below \n");
    printf("\n Select 0 to add text \n");
    printf("\n Select 1 to add new words in the dictionary \n");
    printf("\n Select 2 to enter  enter correction mode \n");
    printf("\n Select 3 to save the text \n");
    printf("\n Select 4 to see the statistics about your text \n");
    printf("\n Select 5 to exit the program\n");
    scanf("%d", &choice);
    return choice;
}



int check_word(char *word)
{
    FILE *readfile;
    char name[40] = {" "};

    char word1[40];
    strcpy(name,"englishWords.txt");
    readfile = fopen(name,"r");

    if(!readfile)
    {
        printf("\n There was an error opening the file \n");
        return -1;
    }

    while(fscanf(readfile,"%s",word1) != EOF)
    {
        if(strcmp(word,word1) == 0)
        return 1;

        else
        {
            return 0;
        }
    }

    fclose(readfile);
    return 0;
}



void insert_text(FILE ** p_fp)
{
     char word[100] = {" "};
     char namefile[40] = {" "};
     char name[40] = {" "};
     printf("\n Please enter the name of the file you want to add words \n");
     scanf("\n%s",namefile);
     strcpy(name,namefile);

    *p_fp = fopen(name, "a+");
    if(*p_fp == NULL)
    {
        printf("\n There was an error opening the file or the file does not exist \n");
    }
    else
    {
    fprintf(*p_fp, "%s\n", add_word(word));
    }
    return;
}



char *add_word(char *word)
{
    printf("\n Please enter the word \n");
    scanf(" %100[^\n]", word);
    return word;
}



void add_word_in_dictionary(FILE ** p_fp)
{
    char word[100];
    char  name[40] = {" "};
    char name_file[40] = {" "};
    printf("\n Please enter the name of the file you want to have as dictionary \n");
    scanf("\n%s",name_file);
    strcpy(name,name_file);
    if(*p_fp == NULL)
    {
        printf("\n There was an error opening the file or the file does not exist \n");
    }

    else
    {
        *p_fp = fopen(name,"a+");
        fprintf(*p_fp, "%99s\n",add_word(word));
    }
    return;
}



void save_file(FILE **fp)  /*Προφανώς δε κάνει save αλλά δε μου ήρθε κάτι άλλο */
{
    fclose(*fp);
    return;
}



int count_characters(void)
{
    char ch = ' ';
    int count_ch;
    char name [40] = {" "};
    char name_file[40] = {" "};
    FILE **fp = NULL;
    printf("\n Please enter the file you want to count the characters of it \n");
    scanf("\n%s",name_file);
    strcpy(name,name_file);
    count_ch = 0;
    *fp = fopen(name, "r+");  /*Για κάποιο λόγο δε μπορεί να μου ν ανοίξει αυτό το αρχείο */
    if(fp == NULL)
    {
        printf("\n There was an error opening the file \n");
        return 0;
    }

    while(ch != EOF)
    {
        if(ch != ' '  && ch !=  '\n')
        {
            count_ch++;
        }
        ch=fgetc(*fp);
    }

    fclose(*fp);

    return count_ch;
}



int count_spaces(void)
{
    int count_sp = 0;
    FILE *fp = NULL;
    char c = ' ';
    char name_file[40] = {" "};
    char name[40] = {" "};
    printf("\n Please enter the name of the file you want to count the spaces \n ");
    scanf("\n%s",name_file);
    strcpy(name,name_file);
    fp = fopen(name,"r");

    if(fp == NULL)
    {
        printf("\n There was an error opening the file or the file does not exist \n");
    }
    else
    {

         while ((c = fgetc(fp)) != EOF)
        {
            if (c == ' ')
                count_sp++;
        }

     }

        fclose(fp);

    return count_sp;
}



void txt_to_array(char x[MAX][N],FILE **fp)  /*Προσπαθώ ανεπιτυχώς χωρίς να ξέρω το λόγο βέβαια να μεταφέρω τα περιεχόμενα του αρχείου σε πίνακα για να έχω συγκρίσεις μεταξύ των διάφορων στοιχείων..Θαυμάσια.. */
{
    int i = 0;
    char str[MAX] = {" "};
    char name[40] = {" "};
    strcpy(name,"AlicesAdventuresInWonderland.txt"); /*Nαι λάθος το γνωρίζω αφού θέλουμε ο χρήστης να επιλέγει ποια αρχεία να διαχειρίζαεται..Δηλαδή πρέπει να βάλω 2 δεικτες (σε δείκτες) στη main; Και όσο εκτελείται μία συνάρτηση με ποιο αρχείο θα δουλεύει,πρέπει να το περάσω ως όρισμα; Nα έχω στη main απλώς 2 scanf που να ζητάνε τα ονόματα των 2 αρχείων;Kαι έπειτα μέσα στις συναρτήσεις πώς θα δουλέψω;; */
    *fp = fopen(name,"rt");
    while(!feof(*fp))
    {

            while(fgets(str, sizeof str, *fp))
        {
            strcpy(x[i],str);
            i++;
        }

    }
    sort_array_alphabetically(x);
    fclose(*fp);
    return;
}



void sort_array_alphabetically(char matrix[MAX][N])
{
    int  i = 0;
    int j= 0;
    char s[40] = {" "};
    for(i=0;i<MAX;i++)
        {
        for(j=i+1;j<MAX-1;j++)
            {
                if(strcmp(matrix[i],matrix[j])>0)
                {
                strcpy(s,matrix[i]);
                strcpy(matrix[i],matrix[j]);
                strcpy(matrix[j],s);
                }
            }
        }
        return;
}



int count_words_same(char matrix[MAX][N])
{
    int i;
    int count = 0;
    for(i = 0; i < MAX; i++)
    {
        if(strcmp(matrix[i],matrix[i+1]) == 0)
        {
            count++;
        }
    }

    return count;
}



int count_words(void)
{
    int words = 0;
    char ch;
    FILE **fp = NULL;
    char name[40] = {" "};
    strcpy("AlicesAdventuresInWonderland.txt",name);

    *fp = fopen(name,"r");  /*Tι undeclared;;;;;Aφού το έχω κάνει declare από πάνω */
    while((ch=fgetc(*fp))!=EOF)
    {
        putchar(ch);
        if((ch==' ')||(ch=='\n'))
        {
            words++;
        }
    }
    fclose(*fp);
    return words;
}


void create_istogram(char matrix[MAX][N])
{
   int a =0;
   int b = 0;
   int c = 0;
   int d = 0;
   int e = 0;
   int f = 0;
   int g = 0;
   int h = 0;
   int i = 0;
   int j = 0;
   int k = 0;
   int m = 0;
   for(m = 0 ; m < MAX; m++)
   {
       if((strlen(matrix[m])) == 1)
       {
           a++;
       }

       if((strlen(matrix[m])) == 2)
       {
           b++;
       }

       if((strlen(matrix[m])) == 3)
       {
           c++;
       }

       if((strlen(matrix[m])) == 4)
       {
           d++;
       }

       if((strlen(matrix[m])) == 5)
       {
           e++;
       }

       if((strlen(matrix[m])) == 6)
       {
           f++;
       }

       if((strlen(matrix[m])) == 7)
       {
           g++;
       }

       if((strlen(matrix[m])) == 8)
       {
           h++;
       }

       if((strlen(matrix[m])) == 9)
       {
           i++;
       }

       if((strlen(matrix[m])) == 10)
       {
           j++;
       }

       if((strlen(matrix[m])) == 11)
       {
           k++;
       }

       if((strlen(matrix[m])) > 11)
       {
           k++;
       }


   }
       print_symbols(a-1,1);
       print_symbols(b,2);
       print_symbols(c,3);
       print_symbols(d,4);
       print_symbols(e,5);
       print_symbols(f,6);
       print_symbols(g,7);
       print_symbols(h,8);
       print_symbols(i,9);
       print_symbols(j,10);
       print_symbols(k,11);

       printf("Total number of strings with more than 11 characters : %d\n",k);

    return;
}

void print_symbols(int times,int numch)
{
    int i;
    printf(" %d:  ",numch);
    for(i = 0 ; i < times; i ++)
    {
        printf("*");
    }
    printf(" (%d) ",times);
    printf("\n");
    return;
}

void create_file(char matrix[MAX][N])
{
    int total_ch;
    int total_words;
    int total_ch_wo_sp;
    int total_dif_words;
    FILE **fp = NULL;
    FILE **p_fp = NULL;
    init_file(fp);

    total_ch = count_characters();
    total_words = count_words();
    total_ch_wo_sp =  total_ch - count_spaces();
    total_dif_words = total_words - count_words_same(matrix);
    *p_fp = fopen("data.txt","wt");
    fprintf(*p_fp, "Total number of characters : %d\n",total_ch);
    fprintf(*p_fp,"Total number of words : %d\n",total_words);
    fprintf(*p_fp,"Total number of characters without spaces : %d\n",total_ch_wo_sp);
    fprintf(*p_fp,"Total number of different words : %d\n",total_dif_words);
    return;
}


void init_file(FILE **dfp)
{
    *dfp = fopen("AlicesAdventuresInWonderland.txt", "r");
    return;
}



void correction_mode(void) /*Aς υποθέσουμε ότι περισσότερες από μια λέξεις δεν υπάρχουν στο λεξιλόγιο..Πώς θα επιστρέφονται όλες ;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;; */
{
    FILE *fp;
    FILE **p_fp = NULL;
    int i = 0;
    char word[40] = {" "};
    char name[40] = {" "};
    char matrix[MAX][40] = {" "};
    char matrix_dic[MAX][40] = {" "};
    int choice = 0;
    int j = 0;
    strcpy(name,"AlicesAdventuresInWonderland.txt");
    strcpy(name,rename_file(name));
    fp = fopen(name,"r+");
    *p_fp = fopen("englishWords.txt","r");
    /*Δε γνωρίζω το μήκος της κάθε λέξεης στα 2 αρχείο,άρα η fgets δε μπορεί να χρησιμοποιηθεί  άμεσα.’ρα αναγκαστικά θα δουλέψω με πίνακες */
    txt_to_array(matrix,&fp);
    txt_to_array2(matrix_dic,p_fp);
    if (!fp)
    {
        printf("\n There was an error opening the file \n");
    }

        while((fgets(matrix[i],40,fp)) != NULL)
        {
            for(i = 0; i < MAX; i++)
            {
                for(j = 0; j < MAX; j++)
                {
                    if(strcmp(matrix[i],matrix_dic[j]) != 0)
                    {
                        printf("\n %s was not found in the dictionary " ,matrix[i]);
                        printf("\n Select 0 to replace that word \n ");
                        printf("\n Select 1 to add the word in the dictionary \n");
                        printf("\n Select 2 to continue checking \n");
                        printf("\n Select 3 to exit correction mode \n");
                        scanf("\n%d",&choice);
                        if(choice == 0)           /*Παίρνω τη λέξη που θέλει να αντικαταστήσει ο χρήστης,του ζητάω με ποια θέλει να την αντικαταστήσει,την αντιγράφω στον πίνακα με τα περιεχόμενα του αρχείο,πάω στο αρχείο και γράφω τα περιεχόμενα του καινούργιου πίνακα */
                        {
                            printf("\n Enter the word \n");
                            scanf("\n%s",word);
                        }

                        if(choice == 1)
                        {
                            add_word_in_dictionary(p_fp);
                        }

                        if(choice == 2)
                        {
                            continue;
                        }


                        if(choice == 3)
                        {
                            break;
                        }

                    }
                }

            }
        }

        return;
}



void txt_to_array2(char x[MAX][N],FILE **fp)  /*Προσπαθώ ανεπιτυχώς χωρίς να ξέρω το λόγο βέβαια να μεταφέρω τα περιεχόμενα του αρχείου σε πίνακα για να έχω συγκρίσεις μεταξύ των διάφορων στοιχείων..Θαυμάσια.. */
{
    int i = 0;
    char str[MAX] = {" "};
    char name[40] = {" "};
    *fp = fopen(name,"r");
    while(!feof(*fp))
    {

            while(fgets(str, sizeof str, *fp)) /*Kαι εδώ μου πετάει error χωρίς να καταλαβαίνω γιατί */
        {
            strcpy(x[i],str);
            i++;
        }

    }
    return;
}

void array_to_txt(char matrix [MAX][N]) /*Προφανώς και με αυτό ανεπιτυχώς */
{
    int i = 0;
    char name[40] = {" "};
    FILE *fp;
    fp = fopen(name,"wt");
    for(i = 0; i < MAX; i++)
    {
        fprintf(fp,"%39s",matrix[i]);
    }

    fclose(fp);
    return;
}


char* rename_file(char oldname[40])
{
    char name[N] = {" "};
    int choice = 0;
    printf("\n Select 0 to not rename the file. \n Select 1 to rename the file \n");
    scanf("\n%d",&choice);
    if(choice == 1)
    {
        printf("\n Please enter the new name of the file \n");
        scanf("\n%s",name);
        rename(oldname,name);
        return name;  /*Nαι,καταλαβαίνω η ζωή μίας μεταβλητής σε μία συνάρτηση είναι  όσο διαρκεί η συνάρτηση..Εδώ γιατί μου πετάει warning όμως */
    }

    if(choice == 0)
    {
        rename(oldname,oldname);
        return oldname;
    }

    return oldname;

}
/*Toυλάχιστον από 39 errors που είχε αρχικά  τελειώνει απροσδόκητα ο κώδικας..Καταλαβαίνω ότι πρώτα γράφουμε λίγο κώδικα και μετά βλέπουμε αν τρέχει αλλά με αυτόν τον τρόπο δε θα είχα κάνει και πολλά */
