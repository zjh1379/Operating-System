/* server-select.c */

#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <stdio.h>
#include <unistd.h>
#include <string.h>
#include <strings.h>
#include <stdlib.h>
#include <arpa/inet.h>

#include <sys/select.h>      /* <===== */

#define BUFFER_SIZE 1024
#define MAX_CLIENTS 5      /* <===== */


int main(int argc, char** argv)
{
  setvbuf( stdout, NULL, _IONBF, 0 );
  /* ====== */
  fd_set readfds;
  int client_sockets[ MAX_CLIENTS ]; /* client socket fd list */
  int client_socket_index = 0;  /* next free spot */
  /* ====== */

  int seed = atoi(argv[1]);
  srand((unsigned) seed);
  unsigned short server_port = (unsigned short)atoi(argv[2]);
  int longest_word_length = atoi(argv[4]);
  int num_client = 0;
  // read the text file and save it in array
  char line[50000][longest_word_length];
  char* fname = argv[3];
  FILE *fp;
  int k =0;

  fp = fopen(fname,"r");
  while(fgets(line[k],longest_word_length+2,fp))
  {
    line[k][strlen(line[k])-1] = '\0';
    k++;
  }

  char* secret_word = line[rand()%k];
  secret_word[strlen(secret_word)] = '\0';
  int word_length = strlen(secret_word)-1;

  /* Create the listener socket as TCP socket */
  /*   (use SOCK_DGRAM for UDP)               */
  int sock = socket( PF_INET, SOCK_STREAM, 0 );
    /* note that PF_INET is protocol family, Internet */

  if ( sock < 0 )
  {
    perror( "socket()" );
    exit( EXIT_FAILURE );
  }

  /* socket structures from /usr/include/sys/socket.h */
  struct sockaddr_in server;
  struct sockaddr_in client;

  server.sin_family = PF_INET;
  server.sin_addr.s_addr = INADDR_ANY;

  unsigned short port = server_port;

  /* htons() is host-to-network-short for marshalling */
  /* Internet is "big endian"; Intel is "little endian" */
  server.sin_port = htons( port );
  int len = sizeof( server );

  if ( bind( sock, (struct sockaddr *)&server, len ) < 0 )
  {
    perror( "bind()" );
    exit( EXIT_FAILURE );
  }

  listen( sock, 5 );  /* 5 is number of waiting clients */
  //printf( "Listener bound to port %d\n", port );

  int fromlen = sizeof( client );

  char buffer[ BUFFER_SIZE ];
  char username[5][1024];
  int get_name[5]={0};
  int welcome[5] ={0};
  int i, n;




  while ( 1 )
  {
#if 0
    struct timeval timeout;
    timeout.tv_sec = 2;
    timeout.tv_usec = 500;  /* 2 seconds AND 500 microseconds */
#endif

    FD_ZERO( &readfds );
    FD_SET( sock, &readfds );   /* listener socket, fd 3 */
    //printf( "Set FD_SET to include listener fd %d\n", sock );

    /* initially, this for loop does nothing; but once we have */
    /*  client connections, we will add each client connection's fd */
    /*   to the readfds (the FD set) */
    for ( i = 0 ; i < client_socket_index ; i++ )
    {
      FD_SET( client_sockets[ i ], &readfds );
      //printf( "Set FD_SET to include client socket fd %d\n",
      //        client_sockets[ i ] );
    }

#if 0
    /* This is a BLOCKING call, but will block on all readfds */
    int ready = select( FD_SETSIZE, &readfds, NULL, NULL, NULL );
#endif

#if 1
    int ready = select( FD_SETSIZE, &readfds, NULL, NULL, NULL );

    if ( ready == 0 )
    {
      printf( "No activity (yet)...\n" );
      continue;
    }
#endif

    /* ready is the number of ready file descriptors */
    //printf( "select() identified %d descriptor(s) with activity\n", ready );


    /* is there activity on the listener descriptor? */
    if ( FD_ISSET( sock, &readfds ) )
    {
      int newsock = accept( sock,
                            (struct sockaddr *)&client,
                            (socklen_t *)&fromlen );
             /* this accept() call we know will not block */
      //printf( "Accepted client connection\n" );
      printf("UNNAMED CLIENT: connected to (server, 9000)\n");
      
      //int fd = client_sockets[client_socket_index];
      client_sockets[ client_socket_index++ ] = newsock;
      //printf("%d\n",client_sockets[0]);
    
      num_client ++;

     
    }


    /* is there activity on any of the established connections? */
    for ( i = 0 ; i < client_socket_index ; i++ )
    {
      int fd = client_sockets[ i ];

      char* msg1 = "Welcome to Guess the Word, please enter your username.\n";
      if(welcome[i] == 0)
      {
        n = send(fd,msg1,strlen(msg1),0);
        welcome[i] = 1;
      }

      
      if ( FD_ISSET( fd, &readfds ) )
      {
        /* can also use read() and write() */
        n = recv( fd, buffer, BUFFER_SIZE - 1, 0 );
            /* we know this recv() call will not block */

        if ( n < 0 )
        {
          perror( "recv()" );
        }
        else if ( n == 0 )
        {
          int k;
          printf( "Client on fd %d closed \n", fd );
          num_client--;
          get_name[i] = 0;
          strcpy(username[i] , "null");
          close( fd );

          /* remove fd from client_sockets[] array: */
          for ( k = 0 ; k < client_socket_index ; k++ )
          {
            if ( fd == client_sockets[ k ] )
            {
              /* found it -- copy remaining elements over fd */
              int m;
              for ( m = k ; m < client_socket_index - 1 ; m++ )
              {
                client_sockets[ m ] = client_sockets[ m + 1 ];
              }
              client_socket_index--;
              break;  /* all done */
            }
          }
        }
        else
        {
          buffer[n] = '\0';
          buffer[n-1] = '\0';
          
         // printf("Let's start playing, %sThere are %d player(s) playing. The secret word is %d letter(s).",buffer,num_client,word_length);
          /* send message back to client */
          char msg[4096];
          if(get_name[i] == 0)
          {
            sprintf(msg,"Let's start playing, %s\nThere are %d player(s) playing. The secret word is %d letter(s).\n" 
                   ,buffer,num_client,word_length);
           
            strcpy(username[i] , buffer);
            n = send(fd, msg, strlen(msg), 0 );
            get_name[i] = 1;
          }
          else
          {
            int num_cor =0;
            int poi_cor =0;
            int* num_secret_word[24] = {0};
            int* num_guess_word[24] = {0};
            for(int j =0; j< strlen(secret_word); j++)
            {
              int asc = secret_word[j];
              int asc2 = buffer[j];
              num_secret_word[asc- 97] +=1;
              if(asc == asc2 || (asc == asc2-32) || (asc == asc2 +32) )
              {
                poi_cor +=1;
              }
            }
            for(int j =0; j< strlen(buffer); j++)
            {
              int asc2 = buffer[j];
              if(num_guess_word[asc2-97] < num_secret_word[asc2-97])
              {
                num_guess_word[asc2-97] +=1;
                num_cor +=1;
              }
            }
            if(poi_cor == strlen(secret_word)-1)
            {
              int temp_client = num_client;
              sprintf(msg, "%s has correctly guessed the word %s\n",username[i],secret_word);
              for(int k =0; k< temp_client;k++)
              {
                int temp_fd = client_sockets[ k ];
                n=send(temp_fd,msg,strlen(msg),0);
                num_client--;
                get_name[k] = 0;
                strcpy(username[k] , "null");
                close( temp_fd );
              }
              
            }
            else if(strlen(buffer) != (strlen(secret_word)-1))
            {
              sprintf(msg,"Invalid guess length. The secret word is %ld letter(s).",strlen(secret_word)-1);
              n = send(fd, msg,strlen(msg),0);
            }
            else
            {
              sprintf(msg,"%s guessed %s: %d letter(s) were correct and %d letter(s) were correctly placed.\n"
                ,username[i],buffer,num_cor,poi_cor );
              for(int k =0; k< num_client;k++)
              {
                int temp_fd = client_sockets[ k ];
                n=send(temp_fd,msg,strlen(msg),0);
              }
            }
          }
          
          
        }
      }
    }
  }

  return EXIT_SUCCESS; /* we never get here */
}

/*
listen() number of connect

*/
