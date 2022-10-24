#include <pthread.h>
#include <string.h>
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>


// Global variable
extern int next_thread_id;
extern int max_squares;
extern int total_tours;
int num_col,num_row;
int dead_end;
pthread_t pthread;                     
int pthread_size = 0; 

// helper struct to save information about position

struct Position
{
	int num_moves;
	struct Point* next_point;
};

struct Arg
{
    //int step;
    int seen;
    int thread_id
    int father_id
    int *board;
};

struct Position possible_move(struct Point curr_pos, struct Point* point_list,int** board);
void * process_move(void* p_args);
void * whattodo( void * w_arg );
int ** copy_board(int** board);
void print_board(int** board);

#if 0
int simulate(int argc, char** argv)
{
	setvbuf(stdout, NULL, _IONBF, 0);


	pthread_mutex_t mutex;          
	int p_m = 0;
    if (p_m) {
        pthread_mutex_lock(&f_lock);
    } 

	// save the information about board
	int m = atoi(argv[1]);
	int n = atoi(argv[2]);
	int row = atoi(argv[3]);
	int col = atoi(argv[4]);

	num_row = m;
	num_col = n;
	dead_end =0;

	// check the basic condition
	if( m <= 2 || n <= 2 || row < 0 || row > m-1 || col <0 || col >n-1)
	{
		fprintf(stderr, "ERROR: Invalid argument(s)\n");
		return EXIT_FAILURE;
	}

	// if the parameter good, create the board.
	int ** board = calloc(m, sizeof(int*));
	for(int i =0; i < m; i++)
	{
		board[i] = calloc(n, sizeof(int));
	}

	struct Point curr_pos;
	curr_pos.x = row;
	curr_pos.y = col; 
	board[row][col] = 1;

	struct Arg* args = calloc(1,sizeof(struct Arg));
	args->board = board;
    args->step = 1;
    args->point.x = curr_pos.x;
    args->point.y = curr_pos.y;
    args->seen = 1;

    pthread = pthread_self();
    process_move(args);

    if(max_squares == num_col * num_row)
    {
    	printf("MAIN: Search complete; found %d possible paths to achieving a full knight's tour\n",total_tours);
    }
    else
    {
    	printf("MAIN: Search complete; best solution(s) visited %d squares out of %d\n", 
	    	 max_squares, num_col * num_row);
	}
   	
   	
   	for (int i = 0; i < m; i++){
        free(board[i]);
    }
    free(board);
    return EXIT_SUCCESS;
}

#endif

#if 1
int simulate(int argc, char** argv)
{
	setvbuf(stdout, NULL, _IONBF, 0);


	pthread_mutex_t mutex;          
	int p_m = 0;
    if (p_m) {
        pthread_mutex_lock(&f_lock);
    } 

	// save the information about board
	int m = atoi(argv[1]);
	int n = atoi(argv[2]);
	int x = atoi(argv[3]);
	int y = atoi(argv[4]);

	num_row = m;
	num_col = n;
	dead_end =0;

	// check the basic condition
	if( m <= 2 || n <= 2 || x < 0 || x > m-1 || y <0 || y >n-1)
	{
		fprintf(stderr, "ERROR: Invalid argument(s)\n");
		return EXIT_FAILURE;
	}

	// if the parameter good, create the board.
	int board[m*n] = {0};
	int curr_pos = x*num_col + y;
	board[curr_pos] = 1;
	int seen = 1;

	struct Arg args = {seen,0,0,board};

    
    printf("MAIN: Solving Sonny's knight's tour problem for a %dx%d board\n", num_row, num_col);
   	printf("MAIN: Sonny starts at row %d and column %d (move #1)\n", x, y);
    

    //pthread = pthread_self();
    process_move((void *)&args);

    if(total_tours > 0)
    {
    	if(total_tours == 1)
    		printf("MAIN: Search complete; found %d possible path to achieving a full knight's tour\n", total_tours);
    	else
    		printf("MAIN: Search complete; found %d possible paths to achieving a full knight's tour\n",total_tours);
    }
    else
    {	
    	printf("MAIN: Search complete; best solution(s) visited %d squares out of %d\n", 
	    	 max_squares, num_col * num_row);
	}
   	
   	
   
    return EXIT_SUCCESS;
}
#endif

// help function to check possible moves in next move
struct Position possible_move(struct Point curr_pos, struct Point* point_list, int** board)
{
	int count=0;
	struct Position next_position;

	// List all the possible move ,then check it.
	// up_l,up_r,down_l,down_r, left_u,left_d,right_u,right_d;
	point_list[0].x = curr_pos.x -1; //7
	point_list[0].y = curr_pos.y -2;
	point_list[1].x = curr_pos.x +1; //6
	point_list[1].y = curr_pos.y -2;

	point_list[5].x = curr_pos.x -1; //2
	point_list[5].y = curr_pos.y +2;
	point_list[4].x = curr_pos.x +1; //3
	point_list[4].y = curr_pos.y +2;

	point_list[6].x = curr_pos.x -2; //0
	point_list[6].y = curr_pos.y -1;
	point_list[7].x = curr_pos.x -2; //1
	point_list[7].y = curr_pos.y +1;

	point_list[3].x = curr_pos.x +2; //4
	point_list[3].y = curr_pos.y +1;
	point_list[2].x = curr_pos.x +2; //5
	point_list[2].y = curr_pos.y -1;
	

	// put the number of possible moves into struct position
	for(int i =0; i< 8; i++)
	{
		if(point_list[i].x >= 0 && point_list[i].x < num_row 
			&& point_list[i].y >= 0 && point_list[i].y < num_col 
			&& board[point_list[i].x][point_list[i].y] == 0)
		{
			count +=1;
		}else{
			point_list[i].x = 0;
			point_list[i].y = 0;
		}
	}


	next_position.num_moves = count;
	if(count == 0)
		return next_position;

	return next_position;
}


int **copy_board(int **board)
{
    int **temp = calloc(num_row, sizeof(int *));
    for (int i = 0; i < num_row; i++)
    {
    	temp[i] = calloc(num_col, sizeof(int));
        for (int j = 0; j < num_col; j++)
            temp[i][j] = board[i][j];
    }
        
    return temp;
}

// the function for thread, clculate the proper route and print the information.


void* process_move(void* p_args){

    struct Arg* args = p_args;
    int** board;
    int curr_step; 
    struct Point curr_point;
    int seen;
    int highest;
    int curr_thread_id = next_thread_id;

    board = args->board;
    curr_step = args->step;
    curr_point.x = args->point.x;
    curr_point.y = args->point.y;
    seen = args->seen; 
    highest = curr_step;

    int* return_size = calloc(1,sizeof(int));
    *return_size = 0;

    int temp_num_moves = 0; 

    struct Point point_list[8]; 
    struct Position next_position;
    next_position = possible_move(curr_point, point_list, board);
    temp_num_moves = next_position.num_moves;
    print_board(board);
    if (temp_num_moves == 1){

        free(args);
        free(return_size);

        struct Point nextPoint;
        
        for(int i = 0; i < 8; i++)
        {
            if (!(point_list[i].x == 0 && point_list[i].y == 0)){
                nextPoint.x = point_list[i].x;
                nextPoint.y = point_list[i].y;
                break;
            }
        }

        board[nextPoint.x][nextPoint.y] = curr_step + 1;

        struct Arg* args = calloc(1,sizeof(struct Arg));
        args->board = board;
        args->step = curr_step + 1;
        args->point.x = nextPoint.x;
        args->point.y = nextPoint.y;
        args->seen = seen + 1;

        process_move(args);
    }

    // In the case that there are more than one possible move
    else if (temp_num_moves > 1){
    	
        free(args);
        if(curr_step == 1)
        {
        	printf("MAIN: %d possible moves after move #1; creating %d child threads...\n"
    		,temp_num_moves,temp_num_moves);
        }
        else
        	printf("T%d: %d moves possible after move #%d; creating threads...\n",curr_thread_id,  temp_num_moves, curr_step);


        pthread_t tid[8];

        int i;
        for (i = 0; i < 8; i++){
            if (!(point_list[i].x == 0 && point_list[i].y == 0)){
				int** newBoard = copy_board(board);
                newBoard[point_list[i].x][point_list[i].y] = curr_step + 1;
            	//board[point_list[i].x][point_list[i].y] = curr_step + 1;
                struct Point curr_point;
                curr_point.x = point_list[i].x;
                curr_point.y = point_list[i].y;

                struct Arg* args = calloc(1,sizeof(struct Arg));
                args->board = newBoard;
                args->step = curr_step + 1;
                args->point.x = curr_point.x;
                args->point.y = curr_point.y;
                args->seen = seen + 1;

                pthread_create(&tid[i], NULL, &process_move, args);
                next_thread_id +=1;
                #ifdef NO_PARALLEL 
                void* returnValue = calloc(0,sizeof(void*)); 
                free(returnValue);

                pthread_join(tid[i], (void**) &returnValue);

                if (*(int*) returnValue > highest){
                    highest = *(int*) returnValue;
                }   

                printf("MAIN: T%d joined\n", next_thread_id-1);
                free(returnValue);
                #endif


            }
        }

        #ifndef NO_PARALLEL
            // Wait for all children to be processed
        	int pid = next_thread_id-dead_end-1;
            for (i = 0; i < 8; i++){
                if (point_list[i].x != 0 && point_list[i].y != 0){
                    
                    void* returnValue = calloc(0,sizeof(void*)); 
                    free(returnValue);

                    pthread_join(tid[i], (void**) &returnValue);        
                    
                    if (*(int*) returnValue > highest){
                        highest = *(int*) returnValue;
                    }           

                    printf("MAIN: T%d joined\n", pid);
                    pid++;
                    free(returnValue);
                }
            }
    
        #endif
    }

    else if (temp_num_moves == 0){

        free(args);
        if (seen == num_row * num_col){
        	max_squares = num_row * num_col;
            printf("T%d: Sonny found a full knight's tour; incremented total_tours\n", curr_thread_id);
            total_tours +=1;

            for (int i = 0; i < num_row; i++){
                free(board[i]);
            }
            free(board);
        }
        else if (seen < num_row * num_col){
        	dead_end +=1;
        	if (curr_step > max_squares){
            	max_squares = curr_step;
            	printf("T%d: Dead end at move #%d; updated max_squares\n", curr_thread_id-1, curr_step);
            	
            	
        	}else{
        		printf("T%d: Dead end at move #%d\n", curr_thread_id-1, curr_step);
        	}
            
            
        }
        *return_size = curr_step;
        pthread_exit(return_size);
    }

    if (pthread_self() != pthread){

        *return_size = curr_step;
        if (highest > *return_size){
            *return_size = highest;
        }
/*
        for (int i = 0; i < num_row; i++){
            free(board[i]);
        }
        free(board);
*/
        pthread_exit(return_size);
    }

    free(return_size);
    return return_size;
}


void print_board(int** board)
{
	printf("\n_________\n");
	for(int i =0; i< num_col;i++)
	{
		for(int j =0; j< num_row;j++)
		{	
			if(j==0)
				printf("|");

			printf("%d|",board[i][j]);
		}
		printf(" \n");
	}
	printf("---------\n");
}





