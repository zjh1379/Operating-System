def first_come_first_serve(procsList, f):

    num_switch = 0
    time_cpu = [0,0]
    time_wait = 0
    time_util = 0

    print("time 0ms: Simulator started for FCFS [Q empty]")

    time_arrive = {}
    process = {}
    
    for thread in procsList:
        time_arrive[thread.get()[1]] = thread.get()
        process[thread.get()[0]] = [*thread.get()]

    time = 0
    running = [False, '', '', '']
    block_map = {}
    ready_queue = []
    while True:

        old_read_queue = ready_queue
        curr_proc = ''

        # no processes left
        if len(process.keys()) == 0:
            print("time {}ms: Simulator ended for FCFS [Q empty]".format(time+1))
            break

        # print changes to the process
        if running[0]:
            if time == running[1]:
                time_cpu[0] += running[2] - running[1]
                time_util += running[2] - running[1]
                time_cpu[1] += 1
                if time <= 1000:
                    print("time {}ms: Process {} ".format(time,process[running[3]][0]),
                        "started using the CPU for {}ms burst".format(running[2] - running[1]),
                        print_queue(ready_queue))

        if running[0]:
            if time == running[2]:
                curr_proc = running[3]

                if len(process[running[3]][3]) == 0:
                    print(f'time {time}ms: Process {running[3]} terminated',
                          print_queue(ready_queue))
                    del process[running[3]]
                else:
                    if process[running[3]][2] > 1:
                        if time <= 1000:
                            print(
                                f'time {time}ms: Process {process[running[3]][0]} '
                                f'completed a CPU burst; '
                                f'{process[running[3]][2]} bursts to go',
                                print_queue(ready_queue))
                    else:
                        if time <= 1000:
                            print(
                                f'time {time}ms: Process {process[running[3]][0]} '
                                f'completed a CPU burst; '
                                f'{process[running[3]][2]} burst to go',
                                print_queue(ready_queue))
                    block = process[running[3]][0]
                    block_time = process[running[3]][4][0] + 2

                    process[running[3]][4].pop(0)

                    if time <= 1000:
                        print(
                            f'time {time}ms: Process {process[running[3]][0]} '
                            f'switching out of CPU; will block on I/O '
                            f'until time {time + block_time}ms',
                            print_queue(ready_queue))
                    block_map[process[running[3]][0]] = \
                        time + block_time, process[running[3]][0]

        if running[0]:
            if time == running[2] + 2:
                running[0] = False

        completed_proc = []
        for v in block_map.values():

            # in case there are multiple processes ending at this time
            if time == v[0]:
                completed_proc.append(v[1])

        completed_proc.sort()
        ready_queue += completed_proc
        for proc in completed_proc:
            if time <= 1000:
                print(
                    f'time {time}ms: Process {proc} '
                    f'completed I/O; added to ready queue',
                    print_queue(ready_queue))

        # check if there is a process coming at this time
        if time in time_arrive.keys():
            ready_queue.append(time_arrive[time][0])
            if time <= 1000:
                print(
                    f'time {time}ms: Process {time_arrive[time][0]} arrived; '
                    f'added to ready queue', print_queue(ready_queue))

        # no process is running and there is at least one ready process
        if not running[0] and len(ready_queue) > 0:
            next_proc = ready_queue[0]
            ready_queue.pop(0)
            running[0] = True
            running[1] = time + 2  # start
            running[2] = time + process[next_proc][3][0] + 2  # end
            process[next_proc][3].pop(0)
            process[next_proc][2] -= 1
            running[3] = next_proc

            # context switch
            num_switch += 1

            if curr_proc != '' and next_proc != curr_proc:
                running[1] += 2
                running[2] += 2

        for p in set(old_read_queue).intersection(ready_queue):
            time_wait += 1

        time += 1

    average_time_cpu = time_cpu[0] / time_cpu[1]
    average_time_wait = time_wait / sum([p.get()[2] for p in procsList])
    average_turnaround_time = average_time_cpu + average_time_wait + 4
    CPU_utilization = round( 100 * time_util / (time+1), 3)

    f.write('Algorithm FCFS\n')
    f.write(f'-- average CPU burst time: {"%.3f" % round(average_time_cpu, 3)} ms\n')
    f.write(f'-- average wait time: {"%.3f" % round(average_time_wait, 3)} ms\n')
    f.write(f'-- average turnaround time: {"%.3f" % round(average_turnaround_time, 3)} ms\n')
    f.write(f'-- total number of context switches: {num_switch}\n')
    f.write(f'-- total number of preemptions: 0\n')
    f.write(f'-- CPU utilization: {"%.3f" % CPU_utilization}%\n')
