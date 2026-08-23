#include <stdio.h>
#include <stdlib.h>

#define SIZE 150

#define TRUE 1
#define FALSE 0

int check_string(char *str);
int mystrcmp(char *str1, char *str2);

main()
{
	char str1[SIZE], str2[SIZE];
	int x;
	
	printf("Please enter the 1st string: \n");
	gets(str1);
	if (check_string(str1)==FALSE)
	{
		printf("Wrong input");
		exit(0);
	}
	
	printf("Please enter the 2nd string: \n");
	gets(str2);
	if (check_string(str2)==FALSE)
	{
		printf("Wrong input!");
		exit(0);
	}
	
	x=mystrcmp(str1,str2);
	
	if (x==-1)
		printf("\nWe have that: %s < %s", str1, str2);
	else if (x==0)
		printf("\nWe have that: %s = %s", str1, str2);
	else 
		printf("\nWe have that: %s < %s", str2, str1);		
}

int check_string(char *str)
{
	int i;
	
	i=0;
	while(str[i]!='\0')
	{
		if (!(str[i]>='a' && str[i]<='z'))
		{
			return FALSE;
		}
		
		i++;
	}
	
	return TRUE;	
}

/* returns
	-1: if str1 < str2
	 0: if str1==str2
	 1: ifstr1 > str2
 */
int mystrcmp(char *str1, char *str2)
{
	int i;
	
	i=0;	
	while(1)
	{
		if (str1[i]=='\0' && str2[i]!='\0')
			return -1;
		else if (str2[i]=='\0' && str1[i]!='\0')
			return 1;
		else if (str1[i]=='\0' && str1[i]=='\0')
			return 0;
		
		
		if (str1[i]<str2[i])
			return -1;
		else if (str1[i]>str2[i])
			return 1;
		
		i++;
	}
}