#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define SIZE 80
#define BUFFER_SIZE 100  // Define a size for temporary input buffers.

struct person
{
	char *onoma;
	char *diefthinsi;
	char *arithmos;
	char *nomos;
};

typedef struct person RECORD;

void read_record(RECORD *p);
void print_record(RECORD x);
void init_record(RECORD *p);
void free_record(RECORD x);
void copy_record(RECORD *dst, RECORD src);

int main()
{
	RECORD *pinakas, x;
	int i, N, choice;

    printf("Give the amount of records: \n");
    scanf("%d", &N);

    pinakas = malloc(sizeof(RECORD) * N);
    if (!pinakas)
    {
        printf("\nFailed to allocate memory.\n");
        exit(0);
    }

	for (i = 0; i <N; i++)
	{
		init_record(&pinakas[i]);
	}
	
    init_record(&x);
	for (i = 0; i < N; i ++)
	{
		printf("%d atomo: \n", i + 1);
		read_record(&pinakas[i]);
	}

	for (i = 0; i < N; i++)
	{
		print_record(pinakas[i]);
	}

    printf("\n\nChoose record for copying:  0 - %d\n", N - 1);
    scanf("%d", &choice);
    copy_record(&x, pinakas[choice]);

    print_record(x);

	for (i = 0; i < N; i++)
	{
		free_record(pinakas[i]);
	}

    free_record(x);
    free(pinakas);
    return 0;
}

void read_record(RECORD *p)
{
	char buffer[BUFFER_SIZE]; // Temporary buffer

	printf("Dwse to onoma: ");
	scanf("%s", buffer);
	strcpy(p->onoma, buffer);

	printf("Dwse ti diefthinsi: ");
	scanf("%s", buffer);
	strcpy(p->diefthinsi, buffer);

	printf("Dwse ton arithmo: ");
	scanf("%s", buffer);
	strcpy(p->arithmos, buffer);

	printf("Dwse to nomo: ");
	scanf("%s", buffer);
	strcpy(p->nomos, buffer);
}

void print_record(RECORD x)
{
	printf("\n%s: %s %s %s",x.onoma, x.diefthinsi, x.arithmos, x.nomos);
}

void init_record(RECORD *p)
{
	// Similar code for other fields
	p->onoma = malloc(sizeof(char)*SIZE);
	// ... Check for NULL ...
	
	p->diefthinsi = malloc(sizeof(char)*SIZE);
	// ... Check for NULL ...
	
	p->arithmos = malloc(sizeof(char)*SIZE);
	// ... Check for NULL ...
	
	p->nomos = malloc(sizeof(char)*SIZE);
	// ... Check for NULL ...
}

void free_record(RECORD x)
{
	free(x.onoma);
	free(x.diefthinsi);
	free(x.arithmos);
	free(x.nomos);
}

void copy_record(RECORD *dst, RECORD src)
{
    strcpy(dst -> onoma, src.onoma);
    strcpy(dst -> diefthinsi, src.diefthinsi);
    strcpy(dst -> arithmos, src.arithmos);
    strcpy(dst -> nomos, src.nomos);
}
