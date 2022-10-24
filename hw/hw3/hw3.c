#include <pthread.h>
#include <string.h>
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>


// Global variable
extern int next_thread_id;
extern int max_squares;
extern int total_tours;
#define MAX_THREAD 9999
int num_col,num_row;
pthread_t pthread[MAX_THREAD];         
// helper struct to save information about position

struct Arg
{
    int step;
    int thread_id;
    int pre_id;
    int *board;
};

int possible_move(int step,int* point_list,int* board);
void * process_move(void* p_args);
int valid_move(int* board, int point, int step);
int simulate(int argc, char** argv)
{
	setvbuf(stdout, NULL, _IONBF, 0);


	pthread_mutex_t mutex;          
	int p_m = 0;
    if (p_m) {
        pthread_mutex_lock(&mutex);
    } 

	// save the information about board
	int m = atoi(argv[1]);
	int n = atoi(argv[2]);
	int x = atoi(argv[3]);
	int y = atoi(argv[4]);

	num_row = m;
	num_col = n;

	// check the basic condition
	if( m <= 2 || n <= 2 || x < 0 || x > m-1 || y <0 || y >n-1)
	{
		fprintf(stderr, "ERROR: Invalid argument(s)\n");
		return EXIT_FAILURE;
	}

	// if the parameter good, create the board.
    // board is one dimentional array to save location by step;
    // board[0] is start point, board[1] save next position.
    // eg: point(1,2) will save as 1*3 + 2 = 5
	int board[m*n];
    int *pre_board = calloc(num_col*num_row,sizeof(int));
	int curr_pos = x*num_col + y;
	board[0] = curr_pos;
	int step = 1;

	struct Arg args = {step,0,0,board};

    
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
        if(max_squares == 1)
            printf("MAIN: Search complete; best solution(s) visited %d square out of %d\n", 
             max_squares, num_col * num_row);
        else{
            printf("MAIN: Search complete; best solution(s) visited %d squares out of %d\n", 
             max_squares, num_col * num_row);
        }
    	
	}
   	free(pre_board);
   	
   
    return EXIT_SUCCESS;
}



void* process_move(void* p_args){

    struct Arg args = *(struct Arg *)p_args;
    
    int* board = args.board;
    int step = args.step;
    int thread_id = args.thread_id;
    int pre_id = args.pre_id;
    
    if (step == num_row * num_col)
    {
            max_squares = num_row * num_col;
            if (thread_id == 0)
                printf("MAIN: Sonny found a full knight's tour; incremented total_tours\n");
            else
                printf("T%d: Sonny found a full knight's tour; incremented total_tours\n", thread_id);
            total_tours +=1;
            return NULL;
    }
    int temp_num_moves = 0; 
    int point_list[8];
    
    temp_num_moves = possible_move( step, point_list, board);
   
    
    //printf("NUM: %d\n" , temp_num_moves);
    if (temp_num_moves == 0){
        if (step > max_squares){
                
            if (thread_id == 0)
                printf("MAIN: Dead end at move #%d; updated max_squares\n", step);
            else
                printf("T%d: Dead end at move #%d; updated max_squares\n", thread_id, step);
                
            max_squares = step;
        }else{
            if (thread_id == 0)
                printf("MAIN: Dead end at move #%d\n", step);
            else
                printf("T%d: Dead end at move #%d\n", thread_id, step);
        }
            
          
    }
    else if (temp_num_moves == 1){

        int point = *point_list;
       
        board[step] =  point;
        struct Arg args = {step+1,thread_id,pre_id,board};
   
        process_move((void *)&args);
    }

    // In the case that there are more than one possible move
    else {
    	
        if(thread_id == 0)
        {
        	printf("MAIN: %d possible moves after move #1; creating %d child threads...\n"
    		,temp_num_moves,temp_num_moves);
        }
        else{
        	printf("T%d: %d possible moves after move #%d; creating %d child threads...\n",
                thread_id,  temp_num_moves, step,temp_num_moves);
        }

        int i = 0;
        for (i = 0; i < temp_num_moves; i++){
			int new_board[num_col*num_row];
            for(int j =0; j< num_row*num_col; j++)
                new_board[j] = board[j];

            int point = point_list[i];
            int curr_thread_id = next_thread_id;

            new_board[step] = point;

            struct Arg args = {step+1,curr_thread_id,thread_id,new_board};
            next_thread_id +=1;
            pthread_create(&pthread[curr_thread_id], NULL, process_move, (void *)&args);
               
            
            #ifdef NO_PARALLEL
                pthread_join(pthread[curr_thread_id],NULL);
                if(thread_id == 0)
                    printf("MAIN: T%d joined\n", curr_thread_id);
                else
                    printf("T%d: T%d joined\n", thread_id, curr_thread_id);
            #else
                pthread_join(pthread[curr_thread_id],NULL);
                if(thread_id == 0)
                    printf("MAIN: T%d joined\n", curr_thread_id);
                else
                    printf("T%d: T%d joined\n", thread_id, curr_thread_id);
            #endif
            
        }
    }
    
    return NULL;
}


int possible_move( int step,int* point_list,int* board)
{

    int possible_x[8] = {-2, -1, 1, 2, 2, 1, -1, -2};
    int possible_y[8] = {-1, -2, -2, -1, 1, 2, 2, 1};
    int count = 0;
    int temp_x,temp_y;
    int x = board[step-1]/num_col;
    int y = board[step-1]%num_col;
        
    for(int i =0; i< 8; i++)
    {  
             
        temp_x = x + possible_x[i];
        temp_y = y + possible_y[i];
        // Verify and count the valid move;
        if(temp_x >= 0 && temp_x < num_row && temp_y >= 0 && temp_y < num_col )
        { 
            if(!valid_move(board,temp_x*num_col +temp_y, step))
            {
                point_list[count] = temp_x * num_col + temp_y;
                count ++;
            }
        }
    }
    return count;

}

int valid_move(int *board, int point, int step){
    int i = 0;
    for (i = 0; i < step; i++){
        if (*(board + i) == point){
            return 1;
        }
    }
    return 0;
}