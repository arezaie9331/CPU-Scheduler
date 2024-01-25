import queue

f = open("input.txt","r")
a = f.read()
a = a.split("\n")
dl = int(a[0])
quantum = int(a[1])
a.pop(0)
a.pop(0)
allProcesses = []
terminated = []
straightLine = ""
pLine = ""
numLine = ""

class Burst():
    def __init__(self,_IsCpu,_BurstTime) -> None:
        self.IsCpu = _IsCpu
        self.BurstTime = _BurstTime

    def __str__(self) -> str:
        v = "cpu" if self.IsCpu else "io"
        return f"{v} {self.BurstTime}"
    
class Process():
    def __init__(self) -> None:
        self.Name =" nsame"
        self.Prio = 0
        self.Bursts = []
        self.AllBs = []
        self.Arrival = 0
        self.WaitingTime = 0
        self.LastArrival = 0
        self.Preempted = False
        self.HasCPU = False
        self.Terminate = None
        self.HasTerminated = None
        self.FirstIo = -1

    def __str__(self) -> str:
        lastBus = ""
        for b in self.Bursts:
            lastBus+=str(b.BurstTime)
            lastBus+=","
        # return f"{self.Name} a:{self.Arrival} la:{self.LastArrival} prio:{self.Prio} pr:{self.Preempted} ter:{self.Terminate} cpu?:{self.HasCPU} B:{self.AllBs} rbs:{lastBus}"
        return f"{self.Name} a:{self.Arrival} wait:{self.WaitingTime} ter:{self.Terminate} turn:{self.Terminate-self.Arrival} resp:{self.FirstIo-self.Arrival}"
        
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
            self.Preempted = False
            # print(self)
            allProcesses.append(self)
        
#priority queue structure handler
class Prio():
    def __init__(self) -> None:
        self.items = []
        self.itemsCount = 0

    def get(self):
        self.itemsCount-=1
        return self.items.pop()

    def push(self,item):
        self.items.append(item)
        self.itemsCount+=1
        self.items = sorted(self.items,key = lambda x : (x.Prio,x.Name),reverse=True)

class PriorityQueueF():
    def __init__(self) -> None:
        self.items = Prio()
        self.timeLeft = 0
        self.itemInProcess = None

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

class RoundRobin():
    def __init__(self,_q) -> None:
        self.items = queue.SimpleQueue()
        self.q = _q
        self.timeLeft = 0
        self.quantumLeft = _q
        self.itemInProcess = None
    
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
            self.itemInProcess.Preempted = True
            self.itemInProcess.LastArrival = now
            self.itemInProcess.Bursts.insert(0,Burst(True,self.timeLeft))
            print(f"{self.itemInProcess.Name} Has been preempted")
            allProcesses.append(self.itemInProcess)
            self.itemInProcess = None
            self.quantumLeft = self.q

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

main_counter = -1
dispatcher_temp = 0
is_CpuUsed = False
talaf = 0
RR = RoundRobin(quantum)
PQ = PriorityQueueF()

add_to_first = []
add_to_second = []

cpu = None

while len(allProcesses)!=0 or (not RR.items.empty()) or (PQ.items.itemsCount!=0) or (RR.itemInProcess!= None) or (PQ.itemInProcess!=None):
# while len(allProcesses)!=0:
    print("-"*100)
    main_counter+=1
    print(main_counter)

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

    # print(arrivals)
    # adding to queues 
    for m in arrivals:
        if m.Preempted == False:
            add_to_first.append(m)
        else:
            add_to_second.append(m)
   
    add_to_first = sorted(add_to_first,key = lambda x : (x.HasCPU,x.Name))
    for m in add_to_first:RR.items.put(m)
    add_to_first = []
    for m in add_to_second:PQ.items.push(m)
    add_to_second = []
    #endregion


    process_appointment = None

    # print(f"appontment : {process_appointment}")
    # print("items in queues")
    # print(f"pq: {PQ.items.itemsCount}")
    # print(f"rr: {RR.items.qsize()}")

    if dispatcher_temp == 0:
        # print("dl1")
        if RR.itemInProcess != None:
            process_appointment = 1
        elif PQ.itemInProcess!=None:
            process_appointment = 2
        elif not RR.items.empty():
            RR.ChooseProcess(main_counter)
            if is_CpuUsed:
                dispatcher_temp = dl
                continue
            else :
                is_CpuUsed = True
        elif PQ.items.itemsCount!=0 :
            PQ.ChooseProcess(main_counter)
            process_appointment = "dl"
            if is_CpuUsed:
                dispatcher_temp = dl
                continue
            else :
                is_CpuUsed = True

    else:
        process_appointment = "dl"

    print(f"appontment : {process_appointment}")
    if process_appointment == None or process_appointment== "dl":
        talaf+=1

    if process_appointment == "dl" and dispatcher_temp ==dl:
        if is_CpuUsed:
            cpu = "id"
            pLine += "|dl\t"
            numLine +=f"{main_counter-1}\t"
            straightLine += ("-"*8)

    if process_appointment ==1 and cpu!=RR.itemInProcess.Name:
        cpu = RR.itemInProcess.Name
        pLine += f"|{RR.itemInProcess.Name}\t"
        numLine +=f"{main_counter-1}\t"
        straightLine += ("-"*8)

    if process_appointment ==2 and cpu!=PQ.itemInProcess.Name:
        cpu = PQ.itemInProcess.Name
        pLine += f"|{PQ.itemInProcess.Name}\t"
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


    if process_appointment == 1 :
        RR.DoProcess(main_counter)
    
    if process_appointment == 2:
        PQ.DoProcess(main_counter)


    
    #region arrival handling
    arrivals = []
    for m in allProcesses:
        if m.LastArrival == main_counter:
            # m.LastArrival = None
            arrivals.append(m)
    for m in arrivals:
        allProcesses.remove(m)
    # adding to queues 
    for m in arrivals:
        if m.Preempted == False:
            add_to_first.append(m)
        else:
            add_to_second.append(m)
   
    add_to_first = sorted(add_to_first,key = lambda x : (x.HasCPU,x.Name))
    for m in add_to_first:RR.items.put(m)
    # for m in  add_to_first:print(m)
    add_to_first = []
    # print("PQ")
    for m in add_to_second:PQ.items.push(m)
    # for m in add_to_second:print(m)
    add_to_second = []
    #endregion




    if dispatcher_temp == 0 and RR.itemInProcess== None and PQ.itemInProcess==None:
        # print("dl2")
        # if RR.itemInProcess != None:
        #     process_appointment = 1
        # elif PQ.itemInProcess!=None:
            # process_appointment = 2
        if not RR.items.empty():
            RR.ChooseProcess(main_counter)
            if is_CpuUsed:
                dispatcher_temp = dl
                continue
            else :
                is_CpuUsed = True
        elif PQ.items.itemsCount!=0 :
            PQ.ChooseProcess(main_counter)
            process_appointment = "dl"
            if is_CpuUsed:
                dispatcher_temp = dl
                continue
            else :
                is_CpuUsed = True
    else:
        process_appointment = "dl"


print()
print()
print("-"*100)
print("terminateds")
ends = []
turnArounds = []
responses = []
watings = []

terminated = sorted(terminated,key = lambda x : (x.Name))
for t in terminated:
    print(t)
    # print(f"ta {t.Terminate-t.Arrival}")
    watings.append(t.WaitingTime)
    ends.append(t.Terminate)
    turnArounds.append(t.Terminate-t.Arrival)
    responses.append(t.FirstIo)



import os 
straightLine+="-"
pLine+= "|"
numLine += str(max(ends))
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