import queue
from functools import cmp_to_key

allProcesses = []
terminated = []
straightLine = ""
pLine = ""
numLine = ""

main_counter = -1
dispatcher_temp = 0
is_CpuUsed = False
talaf = 0



class Burst():
    def __init__(self,_IsCpu,_BurstTime) -> None:
        self.IsCpu = _IsCpu
        self.BurstTime = _BurstTime

    def __str__(self) -> str:
        v = "cpu" if self.IsCpu else "io"
        return f"{v} {self.BurstTime}"
    
class Process():
    def __init__(self) -> None:
        self.Name ="nsame"
        self.Prio = 0
        self.Bursts = []
        self.AllBs = []
        self.Arrival = 0
        self.WaitingTime = 0
        self.LastArrival = 0
        self.Preempted = 0
        self.HasCPU = False
        self.Terminate = None
        self.HasTerminated = None
        self.FirstIo = -1

    def __str__(self) -> str:
        return f"{self.Name} a:{self.Arrival} la:{self.Arrival} prio:{self.Prio} pr:{self.Preempted} W:{self.WaitingTime} B:{self.AllBs}"
        
    def GoForIo(self,now):
        if self.FirstIo == -1:
            self.FirstIo = now
        if len(self.Bursts)==0:
            self.HasTerminated = True
            self.Terminate = now
            terminated.append(self)
            print(f"{self.Name} is Terminated")
            return
        item = self.Bursts.pop(0)
        if item.IsCpu:
            raise TypeError()
        else:
            print(f"{self.Name} is going for Io and returns at {now + item.BurstTime}")
            self.LastArrival = now + item.BurstTime
            self.Preempted = 0
            # print(self)
            allProcesses.append(self)
        
    # def GoForIo(self,now):
    #     print(f"{self.Name} is going for Io")
    #     item = self.Bursts.pop(0)
    #     if item.IsCpu:
    #         raise TypeError()
    #     else:
    #         self.LastArrival = now + item.BurstTime
    #         self.Preempted = 0
    #         allProcesses.append(self)

def HRRNcompare(p1 :Process, p2 :Process):
    burst1 :Burst = p1.Bursts[0]
    R1 = (main_counter-p1.LastArrival + p1.WaitingTime) / burst1.BurstTime
    burst2 :Burst = p2.Bursts[0]
    R2 = (main_counter-p2.LastArrival + p2.WaitingTime) / burst2.BurstTime
    if R1 < R2:
        return -1
    elif R1 > R2:
        return 1
    else:
        if p1.Name > p2.Name:
            return -1
        else : return 1
    
def SJFCompare(p1 :Process, p2 :Process):
    item1 :Burst = p1.Bursts[0]
    item2 :Burst = p2.Bursts[0]
    if item1.BurstTime < item2.BurstTime:
        return -1
    elif item1.BurstTime > item2.BurstTime:
        return 1
    else:
        if p1.Name < p2.Name:
            return -1
        else : return 1
    
#priority queue structure handler
class Prio():
    def __init__(self) -> None:
        self.items = []
        self.itemsCount = 0

    def get(self):
        self.itemsCount-=1
        return self.items.pop()

    def put(self,item):
        self.items.append(item)
        self.itemsCount+=1
        self.items = sorted(self.items,key = lambda x : (x.Prio,x.Name),reverse=True)
        
    def empty(self):
        return self.itemsCount == 0

class PrioHRRN():
    def __init__(self) -> None:
        self.items = []
        self.itemsCount = 0

    def get(self):
        self.items = sorted(self.items,key =cmp_to_key(HRRNcompare))
        self.itemsCount-=1
        return self.items.pop()

    def put(self,item):
        self.items.append(item)
        self.itemsCount+=1

    def empty(self):
        return self.itemsCount == 0

class PrioSJF():
    def __init__(self) -> None:
        self.items = []
        self.itemsCount = 0

    def get(self):
        self.itemsCount-=1
        return self.items.pop()

    def put(self,item):
        self.items.append(item)
        self.itemsCount+=1
        self.items = sorted(self.items,key =cmp_to_key(SJFCompare),reverse=True)

    def empty(self):
        return self.itemsCount == 0
    
def ConvertProcess(st):
    pr = Process()
    m = st.split(":")
    pr.Name = m[0]
    m = m[1].split(",")
    pr.Arrival = int(m[0])
    pr.LastArrival = int(m[0])
    m.pop(0)
    pr.Prio = int(m[0])
    m.pop(0)
    bursts = []
    cnt = 0
    for b in m:
        if cnt%2 ==0:
            n = Burst(True,int(b))
        else:
            n = Burst(False,int(b))
        bursts.append(n)
        cnt+=1
    pr.Bursts = bursts
    pr.AllBs = [int(b) for b in m]
    return pr

f = open("input.txt","r")
a = f.read()
a = a.split("\n")
dl = int(a[0])
quantum = int(a[1])
a.pop(0)
a.pop(0)
allProcesses = []

allProcesses = []
arrivals = []
for item in a:
    pr = ConvertProcess(item)
    arrivals.append(pr.Arrival)
    allProcesses.append(pr)


virtual_zero = min(arrivals)
for n in allProcesses:
    n.Arrival-= virtual_zero
    n.LastArrival -= virtual_zero
    print(n)

class MLFQ():
    def __init__(self) -> None:
        self.counter = 0
        self.Queues = []
        self.IsInProcess = False

    def insert(self,item):
        item.Id = self.counter
        self.Queues.append(item)
        self.counter+=1

    def summary(self):
        print("-"*50)
        for i in self.Queues:
            print(i)
        print("-"*50)

    def isAnyOneHaveProcess(self):
        for i in self.Queues:
            if i.IsAnyOneHere() == True:
                return True
            if i.itemInProcess != None:
                return True
        return False

class ParentQueue:
    def __init__(self,_Name :str,_Id :int) -> None:
        self.Name = _Name
        self.Id = _Id

    def __str__(self) -> str:
        return f"| {self.Id} | {self.Name} |"

class PriorityQueueF(ParentQueue):
    def __init__(self) -> None:
        super().__init__("PriorityQueue",0)
        self.items = Prio()
        self.timeLeft = 0
        self.itemInProcess = None

    def IsAnyOneHere(self) ->bool:
        return self.items.itemsCount!=0

    def __str__(self) -> str:
        return super().__str__()

    def ChooseProcess(self,now):
        global pLine,straightLine,numLine
        self.itemInProcess = self.items.get()
        self.itemInProcess.WaitingTime += (now - self.itemInProcess.LastArrival)
        item = self.itemInProcess.Bursts.pop(0)
        self.timeLeft = item.BurstTime
        print(f"{self.itemInProcess.Name} is selected from PRQ")



    def DoProcess(self,now):
        print(f"{self.itemInProcess.Name} is running")
        self.timeLeft-=1
        # self.itemInProcess.Bursts[0].BurstTime-=1
        self.itemInProcess.HasCPU = True
        if self.timeLeft == 0:
            # self.itemInProcess.Bursts.pop(0)
            self.itemInProcess.GoForIo(now)
            self.itemInProcess = None

class RoundRobin(ParentQueue):
    def __init__(self,_q) -> None:
        super().__init__("RoundRobin",0)
        self.items = queue.SimpleQueue()
        self.q = _q
        self.timeLeft = 0
        self.quantumLeft = _q
        self.itemInProcess = None
    
    def IsAnyOneHere(self) ->bool:
        return (not self.items.empty())
    
    def __str__(self) -> str:
        return super().__str__()
    
    def ChooseProcess(self,now):
        global pLine,straightLine,numLine
        self.quantumLeft = self.q
        self.itemInProcess = self.items.get()
        self.itemInProcess.WaitingTime += now - self.itemInProcess.LastArrival
        item = self.itemInProcess.Bursts.pop(0)
        self.timeLeft = item.BurstTime
        print(f"{self.itemInProcess.Name} is selected from RRQ")

    def DoProcess(self,now):
        print(f"{self.itemInProcess.Name} is running")
        self.timeLeft-=1
        # self.itemInProcess.Bursts[0].BurstTime-=1
        self.itemInProcess.HasCPU = True
        self.quantumLeft-=1
        if self.timeLeft == 0:
            # self.itemInProcess.Bursts.pop(0)
            self.itemInProcess.GoForIo(now)
            self.itemInProcess = None
        elif self.quantumLeft == 0:
            self.itemInProcess.Preempted += 1
            self.itemInProcess.LastArrival = now
            self.itemInProcess.Bursts.insert(0,Burst(True,self.timeLeft))
            print(f"{self.itemInProcess.Name} Has been preempted")
            allProcesses.append(self.itemInProcess)
            self.itemInProcess = None
            self.quantumLeft = self.q

class HRRN(ParentQueue):
    def __init__(self) -> None:
        super().__init__("PriorityQueue",0)
        self.items = PrioHRRN()
        self.timeLeft = 0
        self.itemInProcess = None

    def IsAnyOneHere(self) ->bool:
        return (not self.items.empty())
    
    def __str__(self) -> str:
        return super().__str__()
    
    def ChooseProcess(self,now):
        global pLine,straightLine,numLine
        self.itemInProcess = self.items.get()
        self.itemInProcess.WaitingTime += (now - self.itemInProcess.LastArrival)
        item = self.itemInProcess.Bursts.pop(0)
        self.timeLeft = item.BurstTime
        print(f"{self.itemInProcess.Name} is selected from HRRN")


    def DoProcess(self,now):
        print(f"{self.itemInProcess.Name} is running")
        self.timeLeft-=1
        self.itemInProcess.HasCPU = True
        if self.timeLeft == 0:
            self.itemInProcess.GoForIo(now)
            self.itemInProcess = None

class SJF(ParentQueue):
    def __init__(self) -> None:
        super().__init__("PriorityQueue",0)
        self.items = PrioSJF()
        self.timeLeft = 0
        self.itemInProcess = None
        
    def IsAnyOneHere(self) ->bool:
        return (not self.items.empty())
    
    def __str__(self) -> str:
        return super().__str__()
    
    def ChooseProcess(self,now):
        global pLine,straightLine,numLine
        self.itemInProcess = self.items.get()
        self.itemInProcess.WaitingTime += (now - self.itemInProcess.LastArrival)
        item = self.itemInProcess.Bursts.pop(0)
        self.timeLeft = item.BurstTime
        print(f"{self.itemInProcess.Name} is selected from SJF")

    def DoProcess(self,now):
        print(f"{self.itemInProcess.Name} is running")
        self.timeLeft-=1
        self.itemInProcess.HasCPU = True
        if self.timeLeft == 0:
            self.itemInProcess.GoForIo(now)
            self.itemInProcess = None

ml = MLFQ()

ml.insert(RoundRobin(6))
ml.insert(PriorityQueueF())

ml.summary()


dispatcher_temp = 0
is_CpuUsed = False
talaf = 0
add_in = []
all_process_count = len(allProcesses)
for m in range(all_process_count):add_in.append([])
cpu = None

while len(allProcesses)!=0 or ml.isAnyOneHaveProcess():
# while len(allProcesses)!=0:
    print("-"*100)
    main_counter+=1
    print(main_counter)
    print(f"talaf shode:{talaf}")
    # arrival list
    # print("in arrive list")
    # for m in allProcesses:print(m)
    # print("*"*20)

    #region arrival handling
    arrivals = []
    for m in allProcesses:
        if m.LastArrival == main_counter:
            arrivals.append(m)
    for m in arrivals:
        allProcesses.remove(m)
    # adding to queues 
    for m in arrivals:
        print(m.Preempted)
        add_in[m.Preempted].append(m)

    print(add_in)
    for m in add_in:
        m = sorted(m,key = lambda x : (x.HasCPU,x.Name))

    for m in ml.Queues:
        for n in add_in[m.Id]:
            # print(f"{n} added to {m.Name}")
            m.items.put(n)

    add_in = []
    for m in range(all_process_count):add_in.append([])
    #endregion

    #region appointment 

    process_appointment = None

    # print(f"appontment : {process_appointment}")
    # print("items in queues")
    # print(f"pq: {PQ.items.itemsCount}")
    # print(f"rr: {RR.items.qsize()}")
    cont = False
    if dispatcher_temp == 0:
        for q in ml.Queues:
            if q.itemInProcess != None:
                process_appointment=q.Id
            
        if process_appointment==None:
            for q in ml.Queues:
                print(q)
                if not q.items.empty():
                    q.ChooseProcess(main_counter)
                    if is_CpuUsed:
                        dispatcher_temp = dl
                        process_appointment = "dl"
                        cont = True
                        break
                        
                    else:
                        is_CpuUsed = True
    else:
        process_appointment = "dl"

    print(f"appontment : {process_appointment}")
    if (process_appointment == None or process_appointment== "dl") and main_counter!=0:
        talaf+=1

    if cont==True:
        continue
    #endregion


    if process_appointment == "dl" and dispatcher_temp ==dl:
        if is_CpuUsed:
            cpu = "id"
            pLine += "|dl\t"
            numLine +=f"{main_counter-1}\t"
            straightLine += ("-"*8)

    for q in ml.Queues:
        if process_appointment == q.Id and cpu!=q.itemInProcess.Name:
            cpu = q.itemInProcess.Name
            pLine += f"|{q.itemInProcess.Name}\t"
            numLine +=f"{main_counter-1}\t"
            straightLine += ("-"*8)

    if process_appointment == None and cpu != None:
        cpu = None
        pLine += f"|id\t"
        numLine +=f"{main_counter-1}\t"
        straightLine += ("-"*8)
 
    if dispatcher_temp!=0:
        print("Dispatcher Time")
        dispatcher_temp-=1
        continue


    for q in ml.Queues:
        if q.Id == process_appointment:
            q.DoProcess(main_counter)
    
    #region arrival handling
    arrivals = []
    for m in allProcesses:
        if m.LastArrival == main_counter:
            arrivals.append(m)
    for m in arrivals:
        allProcesses.remove(m)
    # adding to queues 
    for m in arrivals:
        print(m.Preempted)
        add_in[m.Preempted].append(m)

    print(add_in)
    for m in add_in:
        m = sorted(m,key = lambda x : (x.HasCPU,x.Name))

    for m in ml.Queues:
        for n in add_in[m.Id]:
            # print(f"{n} added to {m.Name}")
            m.items.put(n)

    add_in = []
    for m in range(all_process_count):add_in.append([])
    #endregion


    if dispatcher_temp == 0:
        t= True
        for q in ml.Queues:
            if q.itemInProcess != None:
                t = False
                break
        if t:
            print("dl2")
            for q in ml.Queues:
                if q.itemInProcess != None:
                    process_appointment=q.Id
                
            # if process_appointment==None:
            for q in ml.Queues:
                print(q.items)
                print(q.items.empty())
                if not q.items.empty():
                    q.ChooseProcess(main_counter)
                    if is_CpuUsed:
                        dispatcher_temp = dl
                        break
                    else:
                        is_CpuUsed = True


# printing file
import os 
from pathlib import Path
ends = []
turnArounds = []
responses = []
watings = []

terminated = sorted(terminated,key = lambda x : (x.Name))
for t in terminated:
    print(t)
    print(f"ta {t.Terminate-t.Arrival}")
    watings.append(t.WaitingTime)
    ends.append(t.Terminate)
    turnArounds.append(t.Terminate-t.Arrival)
    responses.append(t.FirstIo)


straightLine+="-"
pLine+= "|"
numLine += str(max(ends))
file_path = Path('output.txt')
if file_path.exists():
    os.remove("output.txt")
out = open("output.txt","a")
out.write(f"{straightLine}\n")
out.write(f"{pLine}\n")
out.write(f"{straightLine}\n")
out.write(f"{numLine}\n")
out.write(f"cpu utilization : {(max(ends)-talaf)/max(ends) * 100} %\n")
out.write(f"AWT : {sum(watings)/len(watings)}\n")
out.write(f"ATT : {sum(turnArounds)/len(turnArounds)}\n")
out.write(f"ART : {sum(responses)/len(responses)}\n")
out.close()