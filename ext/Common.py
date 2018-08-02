#all flow entry is counted by this variable
COUNTERID=1

#the size of four flow table 
CSIP_SIZE=50000
CSCP_SIZE=50000
PIT_SIZE=50000
CIPT_SIZE=50000

#forwarding_path=[("zuimeishiguang-1",3),("zuimeishiguang-2",3),("zuimeishiguang-3",3),("zuimeishiguang-6",4),("zuimeishiguang-7",4),("zuimeishiguang-8",4)]
forwarding_path=[]

def look_for_path(name):
    port=0
    count=0
    for item in forwarding_path:
        if  item[0]==name:
            port=item[1]
            return port
        else:
            count=count+1
        if  count==len(forwarding_path):
            port=0
            break
    return port

def add_content_arrive_port(name,port):
    ori_port=look_for_path(name)
    if ori_port==0:
        forwarding_path.append((name,port))
    elif ori_port==port:
        print("this content arriving port has exist,ignore it")
    else:
        print("this content comes from different port,record it")
        
def print_route_table():
    for item in forwarding_path:
        print("%s,%d" %(item[0],item[1]))
        
