#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <math.h>
#include <ctype.h>
#include <string.h>
#include <sys/types.h>
#include <sys/wait.h>

int main(int argc, char** argv)
{	
	setvbuf(stdout, NULL, _IONBF, 0);

	//create pipe
	
	int *pipefd = calloc(2,sizeof(int));

  	int rc = pipe( pipefd );
  	if ( rc == -1 )
  	{
	    perror( "pipe() failed" );
	    return EXIT_FAILURE;
 	}

	printf( "PARENT: Created pipe successfully\n" );
	printf( "PARENT: Calling fork() to create child process to execute hw2-cache.out...\n");
	for(int i = 1; i<argc; ++i)
	{
		printf( "PARENT: Calling fork() to create child process for \"%s\" file...\n",*(argv+i) );
	}

	pid_t* arr_pid = calloc(argc-1, sizeof(pid_t));
	pid_t fork_0 = fork();

	if(fork_0 == 0)
	{

		char* str = calloc(128,sizeof(char));
		sprintf(str, "%d\n",*(pipefd+0));
		close(*(pipefd +1));
		execl( "hw2-cache.out", "./hw2-cache.out", str ,   NULL  );
		free(str);
		

	}
	else
	{
		
		for(int i =1; i < argc; ++i)
		{
			pid_t p = fork();
			*(arr_pid + i -1) = p;
			if ( p == -1 )
		    {
			    perror( "fork() failed" );
			    return EXIT_FAILURE;
			}
		    else if ( p == 0 )
		    {
			    /* CHILD PROCESS read file*/
			    
			    char* fname = *(argv+i);
				FILE* fp;
			    fp = fopen(fname, "r");
			   // printf("%s || %d\n",fname,i);
				if(fp == NULL)
				{
					perror("ERROR: <File not found.>");
					return 2;
				}
				int count = 0;
				char temp_c;
				char* word = calloc(128,sizeof(char));

				while((temp_c = fgetc(fp))!= EOF)
				{
					int n_count = 0;
					
					if(isalnum(temp_c))
					{
						int len = strlen(word);
						*(word+len) = temp_c;
						*(word+len+1) = '\0';
						n_count +=1;
						
						
					}
					else
					{
						n_count = 0;

						if(strlen(word) >=2)
						{	
							// append '.' to the end of word
							char tmp = '.';
							int len = strlen(word);
							*(word+len) = tmp;
							*(word+len+1) = '\0';
							//printf("%s || %ld\n" , word , strlen(word));
							write(*(pipefd+1),word,strlen(word));
							count +=1;
							//printf("%s  ",word);
							memset(word,0,128);
						}
						else
						{
							memset(word,0,128);
						}
								
						

					}


				}
				//while(fscanf(fp,"%s",word) != EOF){}
				free(word);
				free(pipefd);
				free(arr_pid);

				printf("CHILD: Successfully wrote %d words on the pipe\n",count);
				if(count == 0)
				{
					return 3;
				}
				return 0;

		    }
		   
		  
	    }
			
		for(int i =0; i<argc-1;i++)
		{
			int status;
		    waitpid( *(arr_pid+i), &status, 0 );  
		    //printf( "PARENT: my PID is %d.\n", getpid() );
		  	
		    //close(*(pipefd +0));
		    
		      //int exit_status = WEXITSTATUS( status );
		    int exit_status = WEXITSTATUS( status );
		    printf( "PARENT: Child process terminated with exit status %d\n", exit_status );
		    printf( "PARENT: Child running hw2-cache.out terminated with exit status 0\n" );
	        
		}   
		  		

			    
		

	}
	

	close(*(pipefd+0));
	free(arr_pid); 
	free(pipefd);
	

	return EXIT_SUCCESS;
}