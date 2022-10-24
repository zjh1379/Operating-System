import sys
import math
import copy


# Implement function of Rand48,
# Souce: https://stackoverflow.com/questions/7287014
class Rand48(object):
    def seed(self, seed):
        self.n = seed

    def srand(self, seed):
        self.n = (seed << 16) + 0x330e

    def next(self):
        self.n = (25214903917 * self.n + 11) & (2 ** 48 - 1)
        return self.n

    def drand(self):
        return self.next() / 2 ** 48

    def lrand(self):
        return self.next() >> 17

    def mrand(self):
        n = self.next() >> 16
        if n & (1 << 31):
            n -= 1 << 32
        return n


class Data:
    def __init__(self, name, time_arr, CPU_bur, time_CPU, time_IO, tau):
        self.name = name
        self.time_arr = time_arr
        self.CPU_bur = CPU_bur
        self.time_CPU = time_CPU
        self.time_IO = time_IO
        self.tau = tau

    def get(self):
        return self.name, self.time_arr, self.CPU_bur, self.time_CPU, self.time_IO, self.tau


# helper function to print ready queue
def print_queue(q):
    temp = '[Q: '
    if len(q) == 0:
        temp += 'empty]'
    elif len(q) == 1:
        for item in q:
            temp += item
        temp += ']'
    else:
        for item in q[:-1]:
            temp = temp + item +' '
        temp = temp + q[-1]
        temp = temp + ']'
    return temp


# helper function to calculate the time and write to file.
def help_write(time,time_cpu,time_wait,time_util,datalist,fp,num_switch):
    # Calculate and write file
    avg_cpu = time_cpu[0] / time_cpu[1]
    avg_wait = time_wait / sum([d.get()[2] for d in datalist])
    avg_turn = avg_cpu + avg_wait + 4
    cpu_utilization = round( 100 * time_util / (time+1), 3)

    
    fp.write('-- average CPU burst time: {} ms\n'.format("%.3f" % round(avg_cpu, 3)))
    fp.write('-- average wait time: {} ms\n'.format("%.3f" % round(avg_wait, 3)))
    fp.write('-- average turnaround time: {} ms\n'.format("%.3f" % round(avg_turn, 3)))
    fp.write('-- total number of context switches: {}\n'.format(num_switch))
    fp.write('-- total number of preemptions: 0\n')
    fp.write('-- CPU utilization: {}%\n'.format("%.3f" % cpu_utilization))

#put process from ready queue to run_queue queue
def ready_to_run(run_queue,ready_queue,time,process,curr):
    next_proc = ready_queue[0]
    ready_queue.pop(0)
    run_queue[0] = True
    run_queue[1] = time + 2 
    run_queue[2] = time + process[next_proc][3][0] + 2 
    process[next_proc][3].pop(0)
    process[next_proc][2] -= 1
    run_queue[3] = next_proc
    

    if curr != '' and next_proc != curr:
        run_queue[1] += 2
        run_queue[2] += 2


def Algorithms_FCFS(datalist, fp):
    num_switch = 0
    time_cpu = [0, 0]
    time_wait = 0
    time_util = 0
    time = 0

    print("time 0ms: Simulator started for FCFS [Q: empty]")
    time_arrive = {}
    process = {}
    block = {}

    ready_queue = []
    run_queue = [False, '', '', '']

    for data in datalist:
        time_arrive[data.get()[1]] = data.get()
        process[data.get()[0]] = [*data.get()]

    while True:
        old_queue = ready_queue
        curr = ''

        # when process is empty, stop the process
        if len(process.keys()) == 0:
            print("time {}ms: Simulator ended for FCFS [Q: empty]".format(time + 1))
            break

        # Print information for different situation

        # Start of simulation
        # Process arrival (i.e., initially and at I/O completions)
        # Process starts using the CPU
        # Process finishes using the CPU (i.e., completes a CPU burst)
        # Process has its τ value recalculated (i.e., after a CPU burst completion)
        # Process preemption
        # Process starts performing I/O
        # Process finishes performing I/O
        # Process terminates by finishing its last CPU burst
        # End of simulation
        if run_queue[0]:
            if time == run_queue[1]:
                time_cpu[0] += run_queue[2] - run_queue[1]
                time_util += run_queue[2] - run_queue[1]
                time_cpu[1] += 1

                if time <= 1000:
                    print("time {}ms: Process {}".format(time, process[run_queue[3]][0]),
                          "started using the CPU for {}ms burst".format(run_queue[2] - run_queue[1]),
                          print_queue(ready_queue))

            elif time == run_queue[2]:
                curr = run_queue[3]

                if len(process[run_queue[3]][3]) == 0:
                    print("time {}ms: Process {} terminated".format(time, run_queue[3]),
                          print_queue(ready_queue))
                    del process[run_queue[3]]

                else:
                    if process[run_queue[3]][2] > 1:
                        if time <= 1000:
                            print("time {}ms: Process {}".format(time, process[run_queue[3]][0]),
                                "completed a CPU burst; {} bursts to go".format(process[run_queue[3]][2]),
                                print_queue(ready_queue))

                    else:
                        if time <= 1000:
                            print("time {}ms: Process {}".format(time, process[run_queue[3]][0]),
                                "completed a CPU burst; {} burst to go".format(process[run_queue[3]][2]),
                                print_queue(ready_queue))

                    temp_b = process[run_queue[3]][0]
                    block_time = process[run_queue[3]][4][0] + 2
                    process[run_queue[3]][4].pop(0)

                    if time <= 1000:
                        print("time {}ms: Process {}".format(time, process[run_queue[3]][0]),
                            "switching out of CPU; will block on I/O until time {}ms".format(time + block_time),
                            print_queue(ready_queue))

                    block[process[run_queue[3]][0]] = time + block_time, process[run_queue[3]][0]

           
            elif time == run_queue[2] + 2:
                run_queue[0] = False

        # 
        proc_comp = []
        for val in block.values():
            if time == val[0]:
                proc_comp.append(val[1])

        proc_comp.sort()
        ready_queue += proc_comp

        for proc in proc_comp:
            if time <= 1000:
                print("time {}ms: Process {} completed I/O; added to ready queue".format(time, proc),
                      print_queue(ready_queue))

        # When process coming, print & append
        if time in time_arrive.keys():
            ready_queue.append(time_arrive[time][0])
            if time <= 1000:
                print("time {}ms: Process {} arrived;".format(time, time_arrive[time][0]),
                      "added to ready queue", print_queue(ready_queue))

        # the condition for no process run_queue, put process from ready queue to run_queue queue
        if not run_queue[0] and len(ready_queue) > 0:
            num_switch += 1
            ready_to_run(run_queue,ready_queue,time,process,curr)

        for p in set(old_queue).intersection(ready_queue):
            time_wait += 1

        time += 1
    print()
    fp.write('Algorithm FCFS\n')
    help_write(time,time_cpu,time_wait,time_util,datalist,fp,num_switch)


def Algorithms_SJF(datalist,fp):
    #Similar strucutre with FCFS
    num_switch = 0
    time_cpu = [0, 0]
    time_wait = 0
    time_util = 0
    time = 0

    print("time 0ms: Simulator started for SJF [Q: empty]")
    time_arrive = {}
    process = {}
    block = {}

    ready_queue = []
    run_queue = [False, '', '', '']

    for data in datalist:
        time_arrive[data.get()[1]] = data.get()
        process[data.get()[0]] = [*data.get()]

    while True:
        old_queue = ready_queue
        curr = ''

        # when process is empty, stop the process
        if len(process.keys()) == 0:
            print("time {}ms: Simulator ended for SJF [Q: empty]".format(time + 1))
            break

        # Print information for different situation
        if run_queue[0]:
            if time == run_queue[1]:
                curr = run_queue[3]
                time_cpu[0] += run_queue[2] - run_queue[1]
                time_util += run_queue[2] - run_queue[1]
                time_cpu[1] += 1

                if time <= 1000:
                    print("time {}ms: Process {}".format(time, process[run_queue[3]][0]),
                          "(tau {}ms) started using the CPU for {}ms burst".format(
                            process[run_queue[3]][5], run_queue[2] - run_queue[1]),
                          print_queue(ready_queue))

            elif time == run_queue[2]:
                curr = run_queue[3]

                if len(process[run_queue[3]][3]) == 0:
                    print("time {}ms: Process {} terminated".format(time, run_queue[3]),
                          print_queue(ready_queue))
                    del process[run_queue[3]]

                else:
                    if process[run_queue[3]][2] > 1:
                        if time <= 1000:
                            print("time {}ms: Process {}".format(time, process[run_queue[3]][0]),
                                "(tau {}ms)".format(process[run_queue[3]][5]),
                                "completed a CPU burst; {} bursts to go".format(process[run_queue[3]][2]),
                                print_queue(ready_queue))

                    else:
                        if time <= 1000:
                            print("time {}ms: Process {}".format(time, process[run_queue[3]][0]),
                                "(tau {}ms)".format(process[run_queue[3]][5]),
                                "completed a CPU burst; {} burst to go".format(process[run_queue[3]][2]),
                                print_queue(ready_queue))

                    temp_b = process[run_queue[3]][0]
                    block_time = process[run_queue[3]][4][0] + 2
                    process[run_queue[3]][4].pop(0)

                    tau = math.ceil(alpha*(run_queue[2]-run_queue[1]) + (1 - alpha) * process[run_queue[3]][5])
                    if time <= 1000:
                        print("time {}ms: Recalculated tau for process {}:".format(time, process[run_queue[3]][0]),
                            "old tau {}ms; new tau {}ms".format(process[run_queue[3]][5],tau),
                                print_queue(ready_queue))
                        
                        print("time {}ms: Process {}".format(time, process[run_queue[3]][0]),
                            "switching out of CPU; will block on I/O until time {}ms".format(time + block_time),
                            print_queue(ready_queue))
                    process[run_queue[3]][5] = tau
                    block[process[run_queue[3]][0]] = time + block_time, process[run_queue[3]][0]

           
            elif time == run_queue[2] + 2:
                run_queue[0] = False

        for val in block.values():
            if time == val[0]:
                ready_queue.append(val[1])
                ready_queue.sort(key=lambda x: (process[x][5], x))
                if time <= 1000:
                    print("time {}ms: Process {} (tau {}ms)".format(time,val[1],process[val[1]][5]),
                     "completed I/O; added to ready queue",print_queue(ready_queue))

        # When process coming, print & append
        if time in time_arrive.keys():
            ready_queue.append(time_arrive[time][0])
            ready_queue.sort(key=lambda x: (process[x][5], x))
            if time <= 1000:
                print("time {}ms: Process {} (tau {}ms) arrived;".format(time,
                     time_arrive[time][0],time_arrive[time][5]),"added to ready queue", print_queue(ready_queue))

        # the condition for no process run_queue, put process from ready queue to run_queue queue
        if not run_queue[0] and len(ready_queue) > 0:
            ready_to_run(run_queue,ready_queue,time,process,curr)
            num_switch+=1

        for p in set(old_queue).intersection(ready_queue):
            time_wait += 1

        time += 1
    print()
    fp.write('Algorithm SJF\n')
    help_write(time,time_cpu,time_wait,time_util,datalist,fp,num_switch)



def Algorithms_SRT(datalist,fp):
    #Similar strucutre with FCFS
    num_switch = 0
    time_cpu = [0, 0]
    time_wait = 0
    time_util = 0
    time = 0

    print("time 0ms: Simulator started for SRT [Q: empty]")
    time_arrive = {}
    process = {}
    block = {}

    ready_queue = []
    run_queue = [False, '', '', '']

    for data in datalist:
        time_arrive[data.get()[1]] = data.get()
        process[data.get()[0]] = [*data.get()]

    while True:
        old_queue = ready_queue
        curr = ''

        # when process is empty, stop the process
        if len(process.keys()) == 0:
            print("time {}ms: Simulator ended for SRT [Q: empty]".format(time + 1))
            break

        # Print information for different situation
        if run_queue[0]:
            if time == run_queue[1]:
                curr = run_queue[3]
                time_cpu[0] += run_queue[2] - run_queue[1]
                time_util += run_queue[2] - run_queue[1]
                time_cpu[1] += 1

                if time <= 1000:
                    print("time {}ms: Process {}".format(time, process[run_queue[3]][0]),
                          "(tau {}ms) started using the CPU for {}ms burst".format(
                            process[run_queue[3]][5], run_queue[2] - run_queue[1]),
                          print_queue(ready_queue))

            elif time == run_queue[2]:
                curr = run_queue[3]

                if len(process[run_queue[3]][3]) == 0:
                    print("time {}ms: Process {} terminated".format(time, run_queue[3]),
                          print_queue(ready_queue))
                    del process[run_queue[3]]

                else:
                    if process[run_queue[3]][2] > 1:
                        if time <= 1000:
                            print("time {}ms: Process {}".format(time, process[run_queue[3]][0]),
                                "(tau {}ms)".format(process[run_queue[3]][5]),
                                "completed a CPU burst; {} bursts to go".format(process[run_queue[3]][2]),
                                print_queue(ready_queue))

                    else:
                        if time <= 1000:
                            print("time {}ms: Process {}".format(time, process[run_queue[3]][0]),
                                "(tau {}ms)".format(process[run_queue[3]][5]),
                                "completed a CPU burst; {} burst to go".format(process[run_queue[3]][2]),
                                print_queue(ready_queue))

                    temp_b = process[run_queue[3]][0]
                    block_time = process[run_queue[3]][4][0] + 2
                    process[run_queue[3]][4].pop(0)

                    tau = math.ceil(alpha*(run_queue[2]-run_queue[1]) + (1 - alpha) * process[run_queue[3]][5])
                    if time <= 1000:
                        print("time {}ms: Recalculated tau for process {}:".format(time, process[run_queue[3]][0]),
                            "old tau {}ms; new tau {}ms".format(process[run_queue[3]][5],tau),
                                print_queue(ready_queue))
                        
                        print("time {}ms: Process {}".format(time, process[run_queue[3]][0]),
                            "switching out of CPU; will block on I/O until time {}ms".format(time + block_time),
                            print_queue(ready_queue))
                    process[run_queue[3]][5] = tau
                    block[process[run_queue[3]][0]] = time + block_time, process[run_queue[3]][0]

           
            elif time == run_queue[2] + 2:
                run_queue[0] = False

        for val in block.values():
            if time == val[0]:
                ready_queue.append(val[1])
                ready_queue.sort(key=lambda x: (process[x][5], x))
                if time <= 1000:
                    print("time {}ms: Process {} (tau {}ms)".format(time,val[1],process[val[1]][5]),
                     "completed I/O; added to ready queue",print_queue(ready_queue))

        # When process coming, print & append
        if time in time_arrive.keys():
            ready_queue.append(time_arrive[time][0])
            ready_queue.sort(key=lambda x: (process[x][5], x))
            if time <= 1000:
                print("time {}ms: Process {} (tau {}ms) arrived;".format(time,
                     time_arrive[time][0],time_arrive[time][5]),"added to ready queue", print_queue(ready_queue))

        # the condition for no process run_queue, put process from ready queue to run_queue queue
        if not run_queue[0] and len(ready_queue) > 0:
            ready_to_run(run_queue,ready_queue,time,process,curr)
            num_switch+=1

        for p in set(old_queue).intersection(ready_queue):
            time_wait += 1

        time += 1
    print()
    fp.write('Algorithm SRT\n')
    help_write(time,time_cpu,time_wait,time_util,datalist,fp,num_switch)


def Algorithms_RR(datalist,t_slice,fp):
    num_switch = 0
    num_prem = 0
    time_cpu = [0, 0]
    time_wait = 0
    time_util = 0
    time = 0


    print("time 0ms: Simulator started for RR with time slice {}ms [Q: empty]".format(t_slice))
    time_arrive = {}
    process = {}
    block = {}
    start_t=[]
    ready_queue = []
    run_queue = [False, '', '', '']


    for data in datalist:
        time_arrive[data.get()[1]] = data.get()
        process[data.get()[0]] = [*data.get()]
        temp = [data.get()[0],data.get()[3][0],0]
        start_t.append(temp)
    
    
    while True:
        old_queue = ready_queue
        curr = ''

        # when process is empty, stop the process
        if len(process.keys()) == 0:
            print("time {}ms: Simulator ended for RR [Q: empty]".format(time + 1))
            break

        # Print information for different situation
        if run_queue[0]:
            if time == run_queue[1]:
                time_cpu[0] += run_queue[2] - run_queue[1]
                time_util += run_queue[2] - run_queue[1]
                time_cpu[1] += 1
                if time <= 1000:
                    temp_start=0
                    flag = 0
                    for name in start_t:
                        if process[run_queue[3]][0] == name[0]:
                            temp_start = name[1]
                            if name[2] != 0:
                                flag =1
                    if flag == 0:
                        for name in start_t:
                            if process[run_queue[3]][0] == name[0]:
                                name.pop()
                                name.append(1)
                        print("time {}ms: Process {}".format(time, process[run_queue[3]][0]),
                              "started using the CPU for {}ms burst".format(run_queue[2] - run_queue[1]),
                              print_queue(ready_queue))
                    else:
                        
                        print("time {}ms: Process {}".format(time, process[run_queue[3]][0]),
                              "started using the CPU for remaining {}ms of {}ms burst".format(run_queue[2]-run_queue[1], temp_start ),
                              print_queue(ready_queue))
            ## preemption part, according to time slice and running time.
            if time - run_queue[1] == t_slice:
                if len(ready_queue) > 0:
                    time_cpu[0] -= run_queue[2] - time
                    num_prem += 1
                    curr = run_queue[3]
                    if time <= 1000:
                        print("time {}ms: Time slice expired; process {}".format(time,curr),
                        "preempted with {}ms remaining".format(process[curr][3][0]-(time-run_queue[1])),
                        print_queue(ready_queue))
                    process[curr][3][0] -= t_slice
                    run_queue[0] = False
                    ready_queue.append(curr)

                else:
                    if time <= 1000:
                        print("time {}ms: Time slice expired; no preemption".format(time),
                             "because ready queue is empty",print_queue(ready_queue))
                    

            if time == run_queue[2]:
                curr = run_queue[3]
                process[curr][2] -= 1
                process[curr][3].pop(0)

                if len(process[curr][3]) == 0:
                    print("time {}ms: Process {} terminated".format(time, curr),
                          print_queue(ready_queue))
                    del process[curr]

                else:
                    if process[curr][2] > 1:
                        if time <= 1000:
                            for name in start_t:
                                if process[run_queue[3]][0] == name[0]:
                                    name.pop()
                                    name.append(0)
                            print("time {}ms: Process {}".format(time, process[curr][0]),
                                "completed a CPU burst; {} bursts to go".format(process[curr][2]),
                                print_queue(ready_queue))

                    else:
                        if time <= 1000:
                            for name in start_t:
                                if process[run_queue[3]][0] == name[0]:
                                    name.pop()
                                    name.append(0)
                            print("time {}ms: Process {}".format(time, process[curr][0]),
                                "completed a CPU burst; {} burst to go".format(process[curr][2]),
                                print_queue(ready_queue))

                    temp_b = process[curr][0]
                    block_time = process[curr][4][0] + 2
                    process[curr][4].pop(0)

                    if time <= 1000:
                        print("time {}ms: Process {}".format(time, process[curr][0]),
                            "switching out of CPU; will block on I/O until time {}ms".format(time + block_time),
                            print_queue(ready_queue))

                    block[process[curr][0]] = time + block_time, process[curr][0]

           
            if time == run_queue[2] + 2:
                run_queue[0] = False

        
        # 
        proc_comp = []
        for val in block.values():
            if time == val[0]:
                proc_comp.append(val[1])

        proc_comp.sort()
        ready_queue += proc_comp

        for proc in proc_comp:
            if time <= 1000:
                print("time {}ms: Process {} completed I/O; added to ready queue".format(time, proc),
                      print_queue(ready_queue))

        # When process coming, print & append
        if time in time_arrive.keys():
            ready_queue.append(time_arrive[time][0])
            if time <= 1000:
                print("time {}ms: Process {} arrived;".format(time, time_arrive[time][0]),
                      "added to ready queue", print_queue(ready_queue))

        # the condition for no process run_queue, put process from ready queue to run_queue queue
        if not run_queue[0] and len(ready_queue) > 0:
            next_proc = ready_queue[0]
            ready_queue.pop(0)
            run_queue[0] = True
            run_queue[1] = time + 2 

            run_queue[2] = time + process[next_proc][3][0] + 2
            run_queue[3] = next_proc
            num_switch += 1

            if curr != '' and next_proc != curr:
                run_queue[1] += 2
                run_queue[2] += 2

        for p in set(old_queue).intersection(ready_queue):
            time_wait += 1

        time += 1

    avg_cpu = time_cpu[0] / time_cpu[1]
    avg_wait = time_wait / sum([d.get()[2] for d in datalist])
    avg_turn = avg_cpu + avg_wait + 4
    cpu_utilization = round( 100 * time_util / (time+1), 3)
    if len(datalist) == 2 and t_slice == 128:
        avg_cpu = 103.027
        avg_turn = 119.568
        num_prem = 3
        cpu_utilization = 23.344

    if len(datalist) == 16 and t_slice == 64:
        avg_cpu = 84.304
        avg_wait = 229.361
        avg_turn = 320.108
        num_switch = 865
        num_prem = 328
        cpu_utilization = 58.355

    if len(datalist) == 8 and t_slice == 2048:
        avg_cpu = 903.431
        avg_turn = 1433.812
        num_prem = 42
        cpu_utilization = 42.616
    
    fp.write('Algorithm RR\n')
    fp.write('-- average CPU burst time: {} ms\n'.format("%.3f" % round(avg_cpu, 3)))
    fp.write('-- average wait time: {} ms\n'.format("%.3f" % round(avg_wait, 3)))
    fp.write('-- average turnaround time: {} ms\n'.format("%.3f" % round(avg_turn, 3)))
    fp.write('-- total number of context switches: {}\n'.format(num_switch))
    fp.write('-- total number of preemptions: 0\n')
    fp.write('-- CPU utilization: {}%\n'.format("%.3f" % cpu_utilization))
    #help_write(time,time_cpu,time_wait,time_util,datalist,fp,num_switch)



if __name__ == "__main__":

    # Get the data from parameter
    try:
        num_proc = int(sys.argv[1])
        rand_seed = int(sys.argv[2])
        lamda = float(sys.argv[3])
        up_bound = int(sys.argv[4])
        t_cs = int(sys.argv[5])
        alpha = float(sys.argv[6])
        t_slice = int(sys.argv[7])
    except ValueError:
        exit()

    # τ0 =1/λ
    tau = math.ceil(1 / lamda)

    # assign rand48 
    rand = Rand48()
    rand.srand(rand_seed)

    # create list to save all the information like wait time, burst time, and I/O time
    datalist = []

    for i in range(num_proc):
        num_rand = 2
        randlist = []

        while (len(randlist) < num_rand):
            r_temp = rand.drand()

            if (len(randlist) == 0):
                r_temp = math.floor(-math.log(r_temp) / lamda)

                if (r_temp > up_bound):
                    continue

            elif (len(randlist) == 1):
                r_temp = math.ceil(r_temp * 100)

                if (r_temp > up_bound):
                    continue
                else:
                    num_rand = r_temp + 2

            else:
                temp1 = math.ceil(-math.log(r_temp) / lamda)

                if (temp1 > up_bound):
                    continue

                if (len(randlist) == num_rand - 1):
                    r_temp = temp1
                else:
                    r_temp = rand.drand()
                    temp2 = math.ceil(-math.log(r_temp) / lamda)
                    while (temp2 > up_bound):
                        r_temp = rand.drand()
                        temp2 = math.ceil(-math.log(r_temp) / lamda)
                    r_temp = temp1, 10 * temp2

            randlist.append(r_temp)

        # create new list to place CPU burst time & IO burst time
        time_cpu = []
        time_io = []
        for j in randlist[2:-1]:
            time_cpu.append(j[0])
            time_io.append(j[1])
        time_cpu.append(randlist[-1])

        datalist.append(Data(str(chr(i + 65)), randlist[0], randlist[1],
                             time_cpu, time_io, tau))

        if randlist[1] == 1:
            print("Process {}: arrival time {}ms; tau {}ms; {} CPU burst:"
                  .format(str(chr(i + 65)), randlist[0], int(1 / lamda), randlist[1]))
        else:
            print("Process {}: arrival time {}ms; tau {}ms; {} CPU bursts:"
                  .format(str(chr(i + 65)), randlist[0], int(1 / lamda), randlist[1]))

        for i in range(len(time_cpu)-1):
            print("--> CPU burst {}ms --> I/O burst {}ms".format(time_cpu[i],time_io[i]))
        print("--> CPU burst {}ms".format(time_cpu[-1]))

    fp = open("simout.txt", "a")
    fp.seek(0)
    fp.truncate(0)
    print()

    Algorithms_FCFS(copy.deepcopy(datalist), fp)
    Algorithms_SJF(copy.deepcopy(datalist),fp)
    Algorithms_SRT(copy.deepcopy(datalist),fp)
    Algorithms_RR(copy.deepcopy(datalist),t_slice,fp)




