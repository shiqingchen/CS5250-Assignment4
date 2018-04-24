'''
CS5250 Assignment 4, Scheduling policies simulator
Sample skeleton program
Author: Minh Ho
Input file:
    input.txt
Output files:
    FCFS.txt
    RR.txt
    SRTF.txt
    SJF.txt

Apr 10th Revision 1:
    Update FCFS implementation, fixed the bug when there are idle time slices between processes
    Thanks Huang Lung-Chen for pointing out
Revision 2:
    Change requirement for future_prediction SRTF => future_prediction shortest job first(SJF), the simpler non-preemptive version.
    Let initial guess = 5 time units.
    Thanks Lee Wei Ping for trying and pointing out the difficulty & ambiguity with future_prediction SRTF.
'''
import sys
from copy import deepcopy

input_file = 'input.txt'

class Process:
    last_scheduled_time = 0
    def __init__(self, id, arrive_time, burst_time):
        self.id = id
        self.arrive_time = arrive_time
        self.burst_time = burst_time
        self.remaining_time = burst_time
        self.estimated_burst_time = 5
        self.pause_time = arrive_time
    #for printing purpose
    def __repr__(self):
        return ('[id %d : arrive_time %d,  burst_time %d]'%(self.id, self.arrive_time, self.burst_time))

def FCFS_scheduling(process_list):
    #store the (switching time, proccess_id) pair
    schedule = []
    current_time = 0
    waiting_time = 0
    for process in process_list:
        if(current_time < process.arrive_time):
            current_time = process.arrive_time
        schedule.append((current_time,process.id))
        waiting_time = waiting_time + (current_time - process.arrive_time)
        current_time = current_time + process.burst_time
    average_waiting_time = waiting_time/float(len(process_list))
    return schedule, average_waiting_time

#Input: process_list, time_quantum (Positive Integer)
#Output_1 : Schedule list contains pairs of (time_stamp, proccess_id) indicating the time switching to that proccess_id
#Output_2 : Average Waiting Time
def RR_scheduling(process_list, time_quantum):
    schedule = []
    waiting_list = []
    current_time = 0
    waiting_time = 0
    task_list = deepcopy(process_list)
    
    while (len(task_list) > 0):
        current_process = task_list.pop(0)
        if (current_time < current_process.pause_time):
            current_time = current_process.pause_time
        schedule.append((current_time, current_process.id))
        if (current_process.remaining_time <= time_quantum):
            current_time = current_time + current_process.remaining_time
            waiting_time = waiting_time + (current_time - current_process.arrive_time - current_process.burst_time)
        else:
            current_time = current_time + time_quantum
            current_process.pause_time = current_time
            current_process.remaining_time = current_process.remaining_time - time_quantum
            index = len(task_list) - 1
            while (index >= 0):
                if (task_list[index].pause_time <= current_time):
                    task_list.insert((index + 1), current_process)
                    break
                index = index - 1
            if (index < 0):
                task_list.insert(0, current_process)
    
    average_waiting_time = waiting_time/float(len(process_list))
    return schedule, average_waiting_time

def SRTF_scheduling(process_list):
    schedule = []
    waiting_list = []
    current_time = 0
    waiting_time = 0
    task_list = deepcopy(process_list)
    
    current_process = task_list.pop(0)
    schedule.append((current_time, current_process.id))

    for process in task_list:
        if (current_time < process.arrive_time):
            while (current_time < process.arrive_time):
                if (current_process.remaining_time > 0):
                    current_process.remaining_time = current_process.remaining_time - 1
                else:
                    if (len(waiting_list) > 0):
                        current_process = find_next_SRTF_process(waiting_list)
                        schedule.append((current_time, current_process.id))
                        waiting_time = waiting_time + (current_time - current_process.arrive_time)
                        waiting_list.remove(current_process)
                        current_process.remaining_time = current_process.remaining_time - 1
                current_time = current_time + 1
            if (current_process.remaining_time > process.remaining_time):
                waiting_list.append(Process(current_process.id, current_time, current_process.remaining_time))
                current_process = process
                schedule.append((current_time, current_process.id))
            else:
                waiting_list.append(Process(process.id, current_time, process.remaining_time))
        else:
            if (current_process.remaining_time > process.remaining_time):
                waiting_list.append(Process(current_process.id, current_time, current_process.remaining_time))
                current_process = process
                schedule.append((current_time, current_process.id))
            else:
                waiting_list.append(Process(process.id, current_time, process.remaining_time))
    
    while (current_process.remaining_time > 0):
        current_process.remaining_time = current_process.remaining_time - 1
        current_time = current_time + 1

    while (len(waiting_list) != 0):
        current_process = find_next_SRTF_process(waiting_list)
        schedule.append((current_time, current_process.id))
        waiting_list.remove(current_process)
        waiting_time = waiting_time + (current_time - current_process.arrive_time)
        current_time = current_time + current_process.remaining_time

    average_waiting_time = waiting_time/float(len(process_list))
    return schedule, average_waiting_time

def find_next_SRTF_process(waiting_list):
    shortest_next_procecss = waiting_list[0]
    for process in waiting_list:
        if (process.burst_time < shortest_next_procecss.burst_time):
            shortest_next_procecss = process
    return shortest_next_procecss

def find_next_SJF_process(waiting_list, alpha, finished_list):
    shortest_next_procecss = waiting_list[0]
    for p in waiting_list:
        for pp in finished_list:
            if (p.id == pp.id):
                p.estimated_burst_time = alpha * pp.burst_time + (1 - alpha) * pp.estimated_burst_time
    
    for process in waiting_list:
        if (process.estimated_burst_time < shortest_next_procecss.estimated_burst_time):
            shortest_next_procecss = process
    return shortest_next_procecss

def SJF_scheduling(process_list, alpha):
    schedule = []
    waiting_list = []
    finished_list = []
    current_time = 0
    waiting_time = 0
    task_list = deepcopy(process_list)
    
    current_process = task_list.pop(0)
    schedule.append((current_time, current_process.id))
    
    for process in task_list:
        if (current_time < process.arrive_time):
            while (current_time < process.arrive_time):
                if (current_process.remaining_time > 0):
                    current_process.remaining_time = current_process.remaining_time - 1
                else:
                    finished_list.append(current_process)
                    if (len(waiting_list) > 0):
                        current_process = find_next_SJF_process(waiting_list, alpha, finished_list)
                        schedule.append((current_time, current_process.id))
                        waiting_list.remove(current_process)
                        current_process.remaining_time = current_process.remaining_time - 1
                        waiting_time = waiting_time + (current_time - current_process.arrive_time)
                current_time = current_time + 1
            waiting_list.append(process)
        else:
            waiting_list.append(process)

    while (current_process.remaining_time > 0):
        current_process.remaining_time = current_process.remaining_time - 1
        current_time = current_time + 1
    finished_list.append(current_process)

    while (len(waiting_list) != 0):
        current_process = find_next_SJF_process(waiting_list, alpha, finished_list)
        schedule.append((current_time, current_process.id))
        waiting_list.remove(current_process)
        waiting_time = waiting_time + (current_time - current_process.arrive_time)
        current_time = current_time + current_process.burst_time
        finished_list.append(current_process)
    average_waiting_time = waiting_time/float(len(process_list))
    return schedule, average_waiting_time


def read_input():
    result = []
    with open(input_file) as f:
        for line in f:
            array = line.split()
            if (len(array)!= 3):
                print ("wrong input format")
                exit()
            result.append(Process(int(array[0]),int(array[1]),int(array[2])))
    return result
def write_output(file_name, schedule, avg_waiting_time):
    with open(file_name,'w') as f:
        for item in schedule:
            f.write(str(item) + '\n')
        f.write('average waiting time %.2f \n'%(avg_waiting_time))


def main(argv):
    process_list = read_input()
    print ("printing input ----")
    for process in process_list:
        print (process)
    print ("simulating FCFS ----")
    FCFS_schedule, FCFS_avg_waiting_time =  FCFS_scheduling(process_list)
    write_output('FCFS.txt', FCFS_schedule, FCFS_avg_waiting_time )
    print ("simulating RR ----")
    RR_schedule, RR_avg_waiting_time =  RR_scheduling(process_list,time_quantum = 2)
    write_output('RR.txt', RR_schedule, RR_avg_waiting_time )
    print ("simulating SRTF ----")
    SRTF_schedule, SRTF_avg_waiting_time =  SRTF_scheduling(process_list)
    write_output('SRTF.txt', SRTF_schedule, SRTF_avg_waiting_time )
    print ("simulating SJF ----")
    SJF_schedule, SJF_avg_waiting_time =  SJF_scheduling(process_list, alpha = 0.5)
    write_output('SJF.txt', SJF_schedule, SJF_avg_waiting_time )

    for test_time_quantum in range(1, 20):
        test_RR_schedule, test_RR_avg_waiting_time = RR_scheduling(process_list, test_time_quantum)
        print("When time_quantum = %d, average_waiting_time = %f" % (test_time_quantum, test_RR_avg_waiting_time))

    for index in range(1, 11):
        test_alpha = index * 0.1
        test_SJF_schedule, test_SJF_avg_waiting_time =  SJF_scheduling(process_list, test_alpha)
        print("When alpha = %f, average_waiting_time = %f" % (test_alpha, test_SJF_avg_waiting_time))

if __name__ == '__main__':
    main(sys.argv[1:])
