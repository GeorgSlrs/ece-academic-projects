#include <stdio.h>
#include <stdlib.h>
#include <stdio.h>
#include <stdlib.h>

typedef struct data
{
    int value;
    struct data * next;
} Data;
typedef Data * DataList;
int myandlst(DataList );

Data * createData( int value)
{
    Data * dataptr;
    dataptr = malloc(sizeof (Data));
    dataptr->value = value;
    dataptr->next = NULL;
    return dataptr;
}
void appendData(DataList *lstptr, Data *newptr)
{
    if (*lstptr==NULL)
    {
        *lstptr = newptr;
        return;
    }
    appendData( &((*lstptr)->next), newptr);
    return;
}





int myandlst(DataList dl);
int myorlst(DataList dl);
typedef int (*CallBack)(DataList dl);
int report(CallBack f,int t);

int myandlst (DataList dl)
{
    int result=1;
    int item;
    Data *cur=dl;
    while(cur!=NULL)
    {

        /*  printf("%d \n",cur->value);*/
        item=cur->value;
        cur=cur->next;

        result=result*item;
    }

    return result;
}
int mynandlst (DataList dl)
{
    int result=1;
    int item;
    Data *cur=dl;
    while(cur!=NULL)
    {

        /*  printf("%d \n",cur->value);*/
        item=cur->value;
        cur=cur->next;

        result=result*item;
    }

    return !result;


}
int myorlst (DataList dl)
{
    int result=0;
    int item;
    Data *cur=dl;
    while(cur!=NULL)
    {

        /*  printf("%d \n",cur->value);*/
        item=cur->value;
        cur=cur->next;

        result=result+item>0;
    }

    return result;
}

int myxorlst (DataList dl)
{
    int result=0;
    int counts=0;
    int res=0;
    int item;
    Data *cur=dl;
    while(cur!=NULL)
    {

        /*  printf("%d \n",cur->value);*/
        item=cur->value;
        cur=cur->next;

        if (item==1) counts++;
    }

    res=counts%2;

    if (res==0) return 0;
    else return 1;
}

int mynorlst (DataList dl)
{
    int result=0;
    int item;
    Data *cur=dl;
    while(cur!=NULL)
    {

        /*  printf("%d \n",cur->value);*/
        item=cur->value;
        cur=cur->next;

        result=result+item>0;
    }

    return !result;
}

DataList createDatalist(int values[],int no)
{
    int i=0;
    DataList dl=NULL;
    for (i=0; i<no; i++)
    {
        Data *cur=createData(values[i]);
        appendData(&dl,cur);
    }
    return dl;
}

void printTheArray(int arr[], int n)
{
    int i;
    for ( i = 0; i < n; i++)
    {
        printf("%d ",arr[i]);
    }
    printf("\n");
}

void generateAllBinaryStrings(int n, int arr[], int i,int *arrr[200],int *t)
{
    static int co=0;
    int y=0;
    if (i == n)
    {
        /*  printTheArray(arr, n);
         /*  printf("CO %d\n",co);*/
        for ( y = 0; y < n; y++)
        {
            arrr[co][y]=arr[y];
        }
        (*t)++;

        co++;
        return;
    }


    arr[i] = 0;
    generateAllBinaryStrings(n, arr, i + 1,arrr,t);


    arr[i] = 1;
    generateAllBinaryStrings(n, arr, i + 1,arrr,t);
}
void print(int *num, int n)
{
    int i;
    for ( i = 0 ; i < n ; i++)
        printf("%d ", num[i]);
    printf("\n");
}

int report(CallBack f,int counter)
{

    int num[10];
    int *ptr;
    int temp;
    int i,  j;
    int total=0;


    int n=counter;
    int *arrr[1200];
    int *arr;
    DataList    dll ;
    for (i=0; i<1200; i++) arrr[i]=(int*)malloc(n*sizeof(int));
    arr=(int *)malloc(n*sizeof(int));
    ;
    generateAllBinaryStrings(n, arr, 0,arrr,&total);
    printf("JERE\n");
    for (i=0; i<total; i++)
    {
        for (j=0; j<n; j++)
        {
            printf("%d ",arrr[i][j]);
        }
        dll=createDatalist(arrr[i],n);

        printf(" %d\n",f(dll));

        /*  printf("\n");*/

        /*printf("TOTAL %d \n",total);*/



    }
    return 0;
}

typedef struct gate
{
    CallBack f;
    char name[20];
    struct gate **inputs ;
    int calculated;

} Gate;
int getinput()
{
    int x;
    scanf("%d", &x);
    return x;
}

int putinput(int x)
{

    return x;
}


Gate * creategate(CallBack f,int cou,char name[20])
{
    int i;
    Gate * temp ;
    temp = malloc(sizeof (Gate));
    strcpy(temp->name,name);
    temp->f = f;
    temp->inputs=(struct gate **)(malloc(sizeof(struct gate)*cou));
    for (i=0; i<=cou; i++)
    {
        temp->inputs[i]=NULL;
    }
    temp->calculated=-1;
    return temp;
}
int eval(struct gate *x)
{
    int a, b;
    int i;
    int flag;
    int resul[20];
    int total;
    DataList dl;
    struct gate **cur;
    /*
    if (x->in1 != NULL)
    a = eval(x->in1);
    if (x->in2 != NULL)
    b = eval(x->in2);
    */
    total=0;
    cur=x->inputs;
    printf("I EVAL  %s!\n",x->name);
    flag=0;
    ;
    for (i=0; i<24; i++)
    {
        if (cur[i]!=NULL)
        {
            flag=1;
            /*  printf("%d not null! \n",i);*/
            resul[i]=eval(cur[i]);
            total=total+1;
        }
        else break;
    }
    /* printf("TOTAL %d \n",total);*/
    dl=createDatalist(resul,total);
    if (flag==0)
    {
        if (x->calculated==-1)

        {
            x->calculated=(x->f)(dl);
            return  x->calculated;
        }
        else
            printf("ALREADY CALCULATED !\n");

    }

    else
    {
        if (x->calculated==-1)
        {
            x->calculated=(x->f)(dl);
            return (x->f)(dl);
        }

    }

    /*
    if (x->in1==NULL && x->in2 == NULL)
    return (x->f)(0,0);
    else
    return (x->f)(a,b);
    */
}


int main( )
{

    Gate *mynor,*myand,*myor1,*myor2,*mynand,*myor3,*myxor;

    int cou;

/*opws i proigoymenh askhsh apla
    edw h domh gate exei epipleon ena flag calculated poy otan parei timh diafori toy -1 simainei
    pws exei hdh ektimhthei i pylh KAI DEN ksanaypologizetai i timh ths

    */
    cou=2;
    mynor=creategate(mynorlst,cou,"NOR");
    mynor->inputs[0]=creategate(getinput,0,"NOR INPUT1");
    mynor->inputs[1]=creategate(getinput,0,"NOR INPUT2");


    cou=2;
    myand=creategate(myandlst,cou,"AND");
    myand->inputs[0]=creategate(getinput,0,"AND INPUT1");
    myand->inputs[1]=creategate(getinput,0,"AND INPUT2");


    cou=2;
    myor1=creategate(myorlst,cou,"OR1");
    myor1->inputs[0]=creategate(getinput,0,"OR1 INPUT1");
    myor1->inputs[1]=creategate(getinput,0,"OR1 INPUT2");


    cou=2;
    myor2=creategate(myorlst,cou,"OR2");
    myor2->inputs[0]=creategate(getinput,0,"OR2 INPUT1");
    myor2->inputs[1]=creategate(getinput,0,"OR2 INPUT2");


    cou=3;
    mynand=creategate(mynandlst,cou,"NAND");
    mynand->inputs[0]=mynor;
    mynand->inputs[1]=myand;
    mynand->inputs[2]=myor1;

    cou=3;
    myxor=creategate(myxorlst,cou,"XOR");
    myxor->inputs[0]=mynor;
    myxor->inputs[1]=myand;
    myxor->inputs[2]=myor2;


    cou=2;
    myor3=creategate(myorlst,cou,"OR3");
    myor3->inputs[0]=mynand;
    myor3->inputs[1]=myxor;


    printf("\n- %d", eval(myor3));

    printf("ENDSs");
    return 0;
}
