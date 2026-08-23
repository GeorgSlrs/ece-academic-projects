#include <stdio.h>
#include <stdlib.h>

int main(void)
{
    char a = 'A';
    char msg[] = "A";
    char *months[] = {"Jan", "Feb", "Mar"};

    printf("the value of a is: %c\n", a);
    printf("the address of a is: %p\n", &a);
    printf("the size of a is: %zu\n\n\n", sizeof(a));

    printf("the value of msg is: %s\n", msg);
    printf("the first character of msg is: %c\n", msg[0]);
    printf("the address of the first character of msg: %p\n", &msg[0]);
    printf("the size of msg is: %zu\n\n\n", sizeof(msg));

    printf("the value of months is: %p \n", months);
    printf("Jan starts at address: %p\n", months[0]); // Directly use the pointer value
    printf("Feb starts at address: %p\n", months[1]);
    printf("Mar starts at address: %p\n", months[2]);

    printf("the second character of the 2nd string is: %c\n", months[1][1]);
    printf("the second character of the 2nd string (with pointer arithmetic) is: %c\n", *(*(months + 1) + 1));

    printf("the size of the pointer array months is: %zu\n", sizeof(months));
    printf("the size of the element the pointer array points to is: %zu\n", sizeof(months[0]));

    return 0;
}
