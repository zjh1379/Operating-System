#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/types.h>
#include <sys/wait.h>
#include <sys/stat.h>

int main(int argc, char **argv)
{
    setvbuf(stdout, NULL, _IONBF, 0); // disable buffered output

    /* start of shell */
    int *(p +2);
    while (1)
    {
        printf("$ ");

        char *newline = malloc(1024);

        /* read command */
        fgets(newline, 1024, stdin);

        /* parse command */
        if (strlen(newline) == 0) // empty line, go to next line
        {
            free(newline);
            continue;
        }
#ifdef DEBUG_MODE
        printf("newline is %s", newline);
#endif
        argc = 0;
        char **commands = malloc(16 * sizeof(char *));
        char *ptr = strtok(newline, " "); // split by space
        int i = 0;
        while (ptr != NULL)
        {
            *(commands + i) = malloc(64 * sizeof(char));
            strcpy(*(commands + i), ptr);
            argc++;
#ifdef DEBUG_MODE
            printf("*(commands + %d) is: %s\n", i, *(commands + i));
#endif
            i++;
            ptr = strtok(NULL, " ");
        }

        free(newline);

        if (strcmp(*(commands + 0), "exit\n") == 0)
        {
            printf("bye\n");
            for (int j = 0;j < argc;j++)
            {
                free(*(commands+j));
            }
            free(commands);
            return EXIT_SUCCESS;
        }
        pid_t pid = fork();
        if (pid == -1)
        {
            perror("fork failed");
            return EXIT_FAILURE;
        }
        else if (pid == 0) // child process
        {
            /* execute command */
        }
        else // parent process
        {
            /* locate command executable */
            struct stat file_info;
            char *MYPATH = getenv("MYPATH");
            char *command_dir = strcat("/usr/local/bin/", *(commands));
            int rc = lstat(command_dir, &file_info);
            printf("MYPATH = %s\n", MYPATH);
            printf("rc = %d\n", rc);
#ifdef DEBUG_MODE
            printf("MYPATH = %s\n", MYPATH);
            printf("rc = %d\n", rc);
#endif
        }

        

        
    }

    return EXIT_SUCCESS;
}