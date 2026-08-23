int main(void)
{

    char msg[10]="Hello";
    char* ptr = msg;
    printf("this is the value of msg : %p\n",(void *) msg);
    printf("this is the address of msg : %p\n",(void *) &msg);
    printf("this is the value of ptr : %p\n",(void *) ptr);
    printf("this is the address of ptr : %p\n",(void *) &ptr);
    printf("this is the value is : %c\n",* (msg+3)); 
 
    return 0;
}