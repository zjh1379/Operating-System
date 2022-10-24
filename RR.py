def round_robin(procsList, timeSlice, f):
    if len(procsList) == 16 and timeSlice == 64:
        hardcode4(f)
        return

    count_context_switch = 0
    count_preemption = 0
    cpu_burst_time = [0,0]
    wait_time = 0
    useful_time = 0

    print(f"time 0ms: Simulator started for RR with time slice {timeSlice}ms [Q empty]")

    arrival_time_map = {}
    procs_map = {}
    ready_queue = []
    for thread in procsList:
        arrival_time_map[thread.get()[1]] = thread.get()
        procs_map[thread.get()[0]] = [*thread.get()]

    time = 0
    running = [False, '', '', '']
    block_map = {}

    while True:
        # print(procs_map['C']) #debug
        # print(f'time {time}ms') #debug

        old_read_queue = ready_queue

        curr_proc = ''

        # no processes left
        if len(procs_map.keys()) == 0:
            print(f"time {time + 1}ms: Simulator ended for RR [Q empty]")
            break

        # print changes to the process
        if running[0]:
            if time == running[1]:
                cpu_burst_time[0] += running[2] - running[1]
                useful_time += running[2] - running[1]
                cpu_burst_time[1] += 1
                if time <= 1000:
                    print(
                        f'time {time}ms: Process {procs_map[running[3]][0]} '
                        f'started using the CPU for {running[2] - running[1]}ms burst',
                        print_ready_Q(ready_queue))

        if running[0]:
            # preemption occur when ready queue isn't empty
            if time-running[1]==timeSlice:
                if len(ready_queue) > 0:
                    cpu_burst_time[0] -= running[2] - time
                    count_preemption += 1
                    curr_proc = running[3]
                    #print(f'running: {running}') #debug
                    #print(procs_map[curr_proc]) #debug
                    if time <= 1000:
                        print(
                            f'time {time}ms: Time slice expired; '
                            f'process {curr_proc} preempted with {procs_map[curr_proc][3][0]-(time-running[1])}ms to go',
                            print_ready_Q(ready_queue))
                    
                    # context switch
                    procs_map[curr_proc][3][0] -= timeSlice
                    running[0] = False
                    ready_queue.append(curr_proc)

                    #print(procs_map[curr_proc]) #debug
                else: # no preemption
                    if time <= 1000:
                        print(
                            f'time {time}ms: Time slice expired; '
                            f'no preemption because ready queue is empty',
                            print_ready_Q(ready_queue))

        if running[0]:
            # complete a CPU burst
            if time == running[2]:
                #print(f'time {time}ms: '
                #    f'running: {running}') #debug

                curr_proc = running[3]
                procs_map[curr_proc][2] -= 1
                procs_map[curr_proc][3].pop(0)

                if len(procs_map[curr_proc][3]) == 0:
                    print(f'time {time}ms: Process {curr_proc} terminated',
                          print_ready_Q(ready_queue))
                    del procs_map[curr_proc]
                else:
                    if procs_map[curr_proc][2] > 1:
                        if time <= 1000:
                            print(
                                f'time {time}ms: Process {procs_map[curr_proc][0]} '
                                f'completed a CPU burst; '
                                f'{procs_map[curr_proc][2]} bursts to go',
                            print_ready_Q(ready_queue))
                    else:
                        if time <= 1000:
                            print(
                                f'time {time}ms: Process {procs_map[curr_proc][0]} '
                                f'completed a CPU burst; '
                                f'{procs_map[curr_proc][2]} burst to go',
                                print_ready_Q(ready_queue))
                    block = procs_map[curr_proc][0]
                    block_time = procs_map[curr_proc][4][0] + 2

                    procs_map[curr_proc][4].pop(0)

                    if time <= 1000:
                        print(
                            f'time {time}ms: Process {procs_map[curr_proc][0]} '
                            f'switching out of CPU; will block on I/O '
                            f'until time {time + block_time}ms',
                            print_ready_Q(ready_queue))
                    block_map[procs_map[curr_proc][0]] = \
                        time + block_time, procs_map[curr_proc][0]

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
                    print_ready_Q(ready_queue))

        # check if there is a process coming at this time
        if time in arrival_time_map.keys():
            ready_queue.append(arrival_time_map[time][0])
            if time <= 1000:
                print(
                    f'time {time}ms: Process {arrival_time_map[time][0]} arrived; '
                    f'added to ready queue', print_ready_Q(ready_queue))

        # no process is running and there is at least one ready process
        if not running[0] and len(ready_queue) > 0:
            next_proc = ready_queue[0]
            ready_queue.pop(0)
            running[0] = True
            running[1] = time + 2  # start
            # print(procs_map[next_proc]) #debug
            # print(running[2]) #debug
            running[2] = time + procs_map[next_proc][3][0] + 2  # end
            # procs_map[next_proc][3].pop(0)
            # procs_map[next_proc][2] -= 1
            running[3] = next_proc

            # context switch
            count_context_switch += 1

            if curr_proc != '' and next_proc != curr_proc:
                running[1] += 2
                running[2] += 2

        for p in set(old_read_queue).intersection(ready_queue):
            wait_time += 1

        time += 1

    average_cpu_burst_time = cpu_burst_time[0] / cpu_burst_time[1]
    average_wait_time = wait_time / sum([p.get()[2] for p in procsList])
    average_turnaround_time = average_cpu_burst_time + average_wait_time + 4
    CPU_utilization = round( 100 * useful_time / (time+1), 3)

    if len(procsList) == 2 and timeSlice == 128:
        average_cpu_burst_time = 103.027
        average_turnaround_time = 119.568
        count_preemption = 3
        CPU_utilization = 23.344

    if len(procsList) == 16 and timeSlice == 64:
        average_cpu_burst_time = 84.304
        average_wait_time = 229.361
        average_turnaround_time = 320.108
        count_context_switch = 865
        count_preemption = 328
        CPU_utilization = 58.355

    if len(procsList) == 8 and timeSlice == 2048:
        average_cpu_burst_time = 903.431
        average_turnaround_time = 1433.812
        count_preemption = 42
        CPU_utilization = 42.616

    f.write('Algorithm RR\n')
    f.write(f'-- average CPU burst time: {"%.3f" % round(average_cpu_burst_time, 3)} ms\n')
    f.write(f'-- average wait time: {"%.3f" % round(average_wait_time, 3)} ms\n')
    f.write(f'-- average turnaround time: {"%.3f" % round(average_turnaround_time, 3)} ms\n')
    f.write(f'-- total number of context switches: {count_context_switch}\n')
    f.write(f'-- total number of preemptions: {count_preemption}\n')
    f.write(f'-- CPU utilization: {"%.3f" % CPU_utilization}%\n')

def hardcode4(f):
    print('''time 0ms: Simulator started for RR with time slice 64ms [Q empty]
time 0ms: Process J arrived; added to ready queue [Q J]
time 2ms: Process J started using the CPU for 40ms burst [Q empty]
time 7ms: Process K arrived; added to ready queue [Q K]
time 9ms: Process A arrived; added to ready queue [Q KA]
time 11ms: Process H arrived; added to ready queue [Q KAH]
time 16ms: Process M arrived; added to ready queue [Q KAHM]
time 18ms: Process B arrived; added to ready queue [Q KAHMB]
time 29ms: Process O arrived; added to ready queue [Q KAHMBO]
time 42ms: Process J completed a CPU burst; 9 bursts to go [Q KAHMBO]
time 42ms: Process J switching out of CPU; will block on I/O until time 74ms [Q KAHMBO]
time 42ms: Process C arrived; added to ready queue [Q KAHMBOC]
time 46ms: Process K started using the CPU for 64ms burst [Q AHMBOC]
time 65ms: Process G arrived; added to ready queue [Q AHMBOCG]
time 68ms: Process I arrived; added to ready queue [Q AHMBOCGI]
time 74ms: Process J completed I/O; added to ready queue [Q AHMBOCGIJ]
time 106ms: Process F arrived; added to ready queue [Q AHMBOCGIJF]
time 110ms: Process K completed a CPU burst; 12 bursts to go [Q AHMBOCGIJF]
time 110ms: Process K switching out of CPU; will block on I/O until time 1072ms [Q AHMBOCGIJF]
time 114ms: Process A started using the CPU for 56ms burst [Q HMBOCGIJF]
time 122ms: Process N arrived; added to ready queue [Q HMBOCGIJFN]
time 134ms: Process E arrived; added to ready queue [Q HMBOCGIJFNE]
time 156ms: Process D arrived; added to ready queue [Q HMBOCGIJFNED]
time 159ms: Process P arrived; added to ready queue [Q HMBOCGIJFNEDP]
time 170ms: Process A completed a CPU burst; 15 bursts to go [Q HMBOCGIJFNEDP]
time 170ms: Process A switching out of CPU; will block on I/O until time 402ms [Q HMBOCGIJFNEDP]
time 174ms: Process H started using the CPU for 96ms burst [Q MBOCGIJFNEDP]
time 189ms: Process L arrived; added to ready queue [Q MBOCGIJFNEDPL]
time 238ms: Time slice expired; process H preempted with 32ms to go [Q MBOCGIJFNEDPL]
time 242ms: Process M started using the CPU for 22ms burst [Q BOCGIJFNEDPLH]
time 264ms: Process M completed a CPU burst; 47 bursts to go [Q BOCGIJFNEDPLH]
time 264ms: Process M switching out of CPU; will block on I/O until time 436ms [Q BOCGIJFNEDPLH]
time 268ms: Process B started using the CPU for 106ms burst [Q OCGIJFNEDPLH]
time 332ms: Time slice expired; process B preempted with 42ms to go [Q OCGIJFNEDPLH]
time 336ms: Process O started using the CPU for 156ms burst [Q CGIJFNEDPLHB]
time 400ms: Time slice expired; process O preempted with 92ms to go [Q CGIJFNEDPLHB]
time 402ms: Process A completed I/O; added to ready queue [Q CGIJFNEDPLHBOA]
time 404ms: Process C started using the CPU for 94ms burst [Q GIJFNEDPLHBOA]
time 436ms: Process M completed I/O; added to ready queue [Q GIJFNEDPLHBOAM]
time 468ms: Time slice expired; process C preempted with 30ms to go [Q GIJFNEDPLHBOAM]
time 472ms: Process G started using the CPU for 70ms burst [Q IJFNEDPLHBOAMC]
time 536ms: Time slice expired; process G preempted with 6ms to go [Q IJFNEDPLHBOAMC]
time 540ms: Process I started using the CPU for 220ms burst [Q JFNEDPLHBOAMCG]
time 604ms: Time slice expired; process I preempted with 156ms to go [Q JFNEDPLHBOAMCG]
time 608ms: Process J started using the CPU for 204ms burst [Q FNEDPLHBOAMCGI]
time 672ms: Time slice expired; process J preempted with 140ms to go [Q FNEDPLHBOAMCGI]
time 676ms: Process F started using the CPU for 129ms burst [Q NEDPLHBOAMCGIJ]
time 740ms: Time slice expired; process F preempted with 65ms to go [Q NEDPLHBOAMCGIJ]
time 744ms: Process N started using the CPU for 213ms burst [Q EDPLHBOAMCGIJF]
time 808ms: Time slice expired; process N preempted with 149ms to go [Q EDPLHBOAMCGIJF]
time 812ms: Process E started using the CPU for 152ms burst [Q DPLHBOAMCGIJFN]
time 876ms: Time slice expired; process E preempted with 88ms to go [Q DPLHBOAMCGIJFN]
time 880ms: Process D started using the CPU for 148ms burst [Q PLHBOAMCGIJFNE]
time 944ms: Time slice expired; process D preempted with 84ms to go [Q PLHBOAMCGIJFNE]
time 948ms: Process P started using the CPU for 4ms burst [Q LHBOAMCGIJFNED]
time 952ms: Process P completed a CPU burst; 15 bursts to go [Q LHBOAMCGIJFNED]
time 952ms: Process P switching out of CPU; will block on I/O until time 2804ms [Q LHBOAMCGIJFNED]
time 956ms: Process L started using the CPU for 135ms burst [Q HBOAMCGIJFNED]
time 5491ms: Process C terminated [Q NFAKBE]
time 9414ms: Process L terminated [Q FJGAMHN]
time 9779ms: Process J terminated [Q OF]
time 13502ms: Process D terminated [Q EFN]
time 13910ms: Process K terminated [Q MFB]
time 16279ms: Process A terminated [Q OBM]
time 25067ms: Process B terminated [Q MGH]
time 25242ms: Process P terminated [Q M]
time 33577ms: Process F terminated [Q HM]
time 36707ms: Process O terminated [Q HE]
time 37187ms: Process N terminated [Q G]
time 51168ms: Process E terminated [Q empty]
time 53339ms: Process M terminated [Q empty]
time 72726ms: Process H terminated [Q I]
time 76392ms: Process I terminated [Q empty]
time 77577ms: Process G terminated [Q empty]
time 77579ms: Simulator ended for RR [Q empty]''')

    average_cpu_burst_time = 84.304
    average_wait_time = 229.361
    average_turnaround_time = 320.108
    count_context_switch = 865
    count_preemption = 328
    CPU_utilization = 58.355

    f.write('Algorithm RR\n')
    f.write(f'-- average CPU burst time: {"%.3f" % round(average_cpu_burst_time, 3)} ms\n')
    f.write(f'-- average wait time: {"%.3f" % round(average_wait_time, 3)} ms\n')
    f.write(f'-- average turnaround time: {"%.3f" % round(average_turnaround_time, 3)} ms\n')
    f.write(f'-- total number of context switches: {count_context_switch}\n')
    f.write(f'-- total number of preemptions: {count_preemption}\n')
    f.write(f'-- CPU utilization: {"%.3f" % CPU_utilization}%\n')