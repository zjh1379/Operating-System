def shortest_remaining_time(procsList, f):

    # analysis variable
    count_context_switch = 0
    cpu_burst_time = [0, 0]
    wait_time = 0
    useful_time = 0
    count_preemptions = 0

    print("time 0ms: Simulator started for SRT [Q empty]")

    arrival_time_map = {}
    procs_map = {}
    ready_queue = []
    for thread in procsList:
        arrival_time_map[thread.get()[1]] = thread.get()
        procs_map[thread.get()[0]] = [*thread.get()]

    time = 0

    # running[0] -- whether CPU is in use
    # running[1] -- if running[0], then this represents the start time of this running
    # running[2] -- if running[0], then this represents the end time of this running
    # running[3] -- if running[0], then this represents the process name of this running
    running = [False, '', '', '']

    # when a process is blocked, add to this map with its time
    block_map = {}

    while True:

        old_read_queue = ready_queue

        curr_proc = ''

        # no processes left
        if len(procs_map.keys()) == 0:
            print(f"time {time + 1}ms: Simulator ended for SRT [Q empty]")
            break

        # print(time, running[0], running[1], running[2], running[3])

        # start running a process -- time == start time of the process
        if running[0]:
            if time == running[1]:
                curr_proc = running[3]
                cpu_burst_time[0] += running[2] - running[1]
                useful_time += running[2] - running[1]
                cpu_burst_time[1] += 1
                if time <= 1000:
                    print(
                        f'time {time}ms: Process {procs_map[running[3]][0]} '
                        f'(tau {procs_map[running[3]][5]}ms) started using the CPU '
                        f'for {running[2] - running[1]}ms burst',
                        print_ready_Q(ready_queue))

        # end running a process -- time == end time of the process
        if running[0]:
            if time == running[2]:
                curr_proc = running[3]

                # check if the process reaches the end -- cpu burst time list is empty
                if len(procs_map[running[3]][3]) == 0:
                    print(f'time {time}ms: Process {running[3]} terminated',
                          print_ready_Q(ready_queue))
                    del procs_map[running[3]]
                else:
                    if procs_map[running[3]][2] > 1:
                        if time <= 1000:
                            print(
                                f'time {time}ms: Process {procs_map[running[3]][0]} '
                                f'(tau {procs_map[running[3]][5]}ms) '
                                f'completed a CPU burst; '
                                f'{procs_map[running[3]][2]} bursts to go',
                                print_ready_Q(ready_queue))
                    else:
                        if time <= 1000:
                            print(
                                f'time {time}ms: Process {procs_map[running[3]][0]} '
                                f'(tau {procs_map[running[3]][5]}ms) '
                                f'completed a CPU burst; '
                                f'{procs_map[running[3]][2]} burst to go',
                                print_ready_Q(ready_queue))
                    block = procs_map[running[3]][0]
                    block_time = procs_map[running[3]][4][0] + 2

                    procs_map[running[3]][4].pop(0)

                    # update tau <- alpha * burst time + (1 - alpha) * tau
                    tau = math.ceil(alpha * (running[2] - running[1]) +
                                    (1 - alpha) * procs_map[running[3]][5])
                    if time <= 1000:
                        print(
                            f'time {time}ms: Recalculated tau from '
                            f'{procs_map[running[3]][5]}ms to {tau}ms '
                            f'for process {procs_map[running[3]][0]}',
                            print_ready_Q(ready_queue))
                    procs_map[running[3]][5] = tau

                    if time <= 1000:
                        print(
                            f'time {time}ms: Process {procs_map[running[3]][0]} '
                            f'switching out of CPU; will block on I/O '
                            f'until time {time + block_time}ms',
                            print_ready_Q(ready_queue))
                    block_map[procs_map[running[3]][0]] = \
                        time + block_time, procs_map[running[3]][0]

        # wait for another 2ms for cpu to be reused
        if running[0]:
            if time == running[2] + 2:
                running[0] = False

        for v in block_map.values():
            if time == v[0]:
                ready_queue.append(v[1])
                ready_queue.sort(key=lambda x: (procs_map[x][5], x))
                if time <= 1000:
                    print(
                        f'time {time}ms: Process {v[1]} (tau {procs_map[v[1]][5]}ms) '
                        f'completed I/O; added to ready queue',
                        print_ready_Q(ready_queue))

        # check if there is a process coming at this time
        if time in arrival_time_map.keys():
            ready_queue.append(arrival_time_map[time][0])
            ready_queue.sort(key=lambda x: (procs_map[x][5], x))
            if time <= 1000:
                print(
                    f'time {time}ms: Process {arrival_time_map[time][0]} '
                    f'(tau {arrival_time_map[time][5]}ms) arrived; '
                    f'added to ready queue', print_ready_Q(ready_queue))
                    

        # no process is running and there is at least one ready process
        if not running[0] and len(ready_queue) > 0:
            next_proc = ready_queue[0]
            ready_queue.pop(0)
            running[0] = True
            running[1] = time + 2  # start
            running[2] = time + procs_map[next_proc][3][0] + 2  # end
            procs_map[next_proc][3].pop(0)
            procs_map[next_proc][2] -= 1
            running[3] = next_proc

            # context switch
            count_context_switch += 1

            if curr_proc != '' and next_proc != curr_proc:
                # print(next_proc, curr_proc)
                running[1] += 2
                running[2] += 2

        for p in set(old_read_queue).intersection(ready_queue):
            wait_time += 1

        time += 1

    average_cpu_burst_time = cpu_burst_time[0] / cpu_burst_time[1]
    average_wait_time = wait_time / sum([p.get()[2] for p in procsList])
    average_turnaround_time = average_cpu_burst_time + average_wait_time + 4
    CPU_utilization = round(100 * useful_time / (time + 1), 3)

    f.write('Algorithm SRT\n')
    f.write(f'-- average CPU burst time: {"%.3f" % round(average_cpu_burst_time, 3)} ms\n')
    f.write(f'-- average wait time: {"%.3f" % round(average_wait_time, 3)} ms\n')
    f.write(f'-- average turnaround time: {"%.3f" % round(average_turnaround_time, 3)} ms\n')
    f.write(f'-- total number of context switches: {count_context_switch}\n')
    f.write(f'-- total number of preemptions: {count_preemptions}\n')
    f.write(f'-- CPU utilization: {"%.3f" % CPU_utilization}%\n')

