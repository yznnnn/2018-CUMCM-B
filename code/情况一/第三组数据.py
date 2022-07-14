import copy
import xlwt
import math



####################
######全局参数定义######
####################

#RGV 移动 1 个单位所需时间
T_move1=18
#RGV 移动 2 个单位所需时间
T_move2=32
#RGV 移动 3 个单位所需时间
T_move3=46
#CNC 加工完成一个一道工序的物料所需时间
T_process_A=545
#CNC 加工完成一个两道工序物料的第一道工序所需时间
T_process_B1=455
#CNC 加工完成一个两道工序物料的第二道工序所需时间
T_process_B2=182
#RGV 为 CNC1#，3#，5#，7#一次上下料所需时间
T_IO_odd=27
#RGV 为 CNC2#，4#，6#，8#一次上下料所需时间
T_IO_even=32
#RGV 完成一个物料的清洗作业所需时间
T_clean=25





#################
######类定义######
#################



#物料类
class PRODUCT:
    #构造函数
    def __init__(self,num,CNC_num,start_time):
        self.num=num#物料序号
        self.CNC_num=CNC_num#加工物料的CNC序号
        self.start_time=start_time#上料开始时刻
        self.finish_time=-1#下料开始时刻

    #显示该物料的资料
    def print_data(self):
        st='\t'+str(self.num)+'\t'+str(self.CNC_num)+'\t'+str(self.start_time)+'\t'+str(self.finish_time)+'\t'
        return st


#任务类
class PROJECT:
    #构造函数
    def __init__(self,Type,num,Initiator_CNC_num,Initiator_CNC_postion,initial_time,work_time):
        self.type=Type#任务类型
        self.num=num#任务序号
        self.Initiator_CNC_num=Initiator_CNC_num#任务发出者CNC编号
        self.Initiator_CNC_postion=Initiator_CNC_postion#任务发出者位置
        self.initial_time=initial_time#任务发出时刻
        self.wait_time=0#等待时间
        self.move_time=0#需要移动时间
        self.start_time=0#任务开始时刻
        self.work_time=work_time#工作时间
        self.priority=0#任务优先级

    def print_data(self):
        st=str(self.type)+'\t'+str(self.num)+'\t'+str(self.Initiator_CNC_num)+'\t'+str(self.Initiator_CNC_postion)+'\t'+str(self.initial_time)+'\t'+str(self.Response_ratio)+'\t'+str(self.work_time)
        return st

    #优先级计算函数
    def priority_generate(self,robot_position):
        k=abs(robot_position-self.Initiator_CNC_postion)
        if k==1:
            self.move_time=T_move1
        if k==2:
            self.move_time=T_move2
        if k==3:
            self.move_time=T_move3

        a=0.5
        b=1-a

        #print("移动时间："+str(self.move_time))

        #self.priority=self.move_time  


        #self.priority=(self.wait_time+1)/(self.move_time+1)


        #self.priority=(a+1)**self.wait_time+b**self.move_time
        
        self.priority=a*self.wait_time+b*(1/(self.move_time+1))  #390
        #self.priority=(self.wait_time+self.work_time)/self.work_time
        #self.priority=(self.wait_time+self.move_time+self.work_time)/self.work_time  #355
        #self.priority=(self.wait_time+self.move_time+1)/(self.move_time+1)   ##367

#RGV机器人类
class RGV_ROBOT:
    #构造函数
    def __init__(self):
        self.current_PROJECT=-1#当前执行的任务数据
        self.current_position=1#当前位置
        self.next_position=1#下次位置
        self.PROJECT_remaining_time=0#任务剩余时间
        self.Moving_remaining_time=0#移动剩余时间
    
    
    #接受任务函数
    def Accept_PROJECT(self,choosed_PROJECT,TIME):
        #获得当前执行的任务数据
        self.current_PROJECT=copy.deepcopy(choosed_PROJECT)
        #获取任务目标位置
        self.next_position=choosed_PROJECT.Initiator_CNC_postion
        #获取任务剩余时间
        self.PROJECT_remaining_time=choosed_PROJECT.move_time+choosed_PROJECT.work_time
        #获取任务移动剩余时间
        self.Moving_remaining_time=choosed_PROJECT.move_time
        #定义任务开始时间
        self.current_PROJECT.start_time=TIME

#CNC工作台类
class CNC_WORKBENCH:
    #构造函数
    def __init__(self,num):
        self.num=num#CNC 工作台编号
        self.status=0#状态码 0等待上料  1工作中 2等待下料
        #CNC工作台位置
        if num%2==0:
            self.position=int(num/2)
        else:
            self.position=int((num+1)/2)

        self.current_PRODUCT_num=-1#CNC工作台当前加工物料序号
        self.Processing_time_remaining=0#CNC工作台加工剩余时间
        self.send_PROJECT=0#CNC工作台是否已经发出任务 0为未发出 1为已发出
    #计算任务工作时间函数
    def calculate_workTime(self):
        if self.num%2==0:
            return T_IO_even
        else:
            return T_IO_odd


def saveDATA(position_list,Product_list):
    '''
    f=open("坐标.txt",'w+')
    for i in position_list:
        f.write(str(i)+"\n")
    f.close()
    '''
    workbook = xlwt.Workbook(encoding = 'ascii')
    worksheet = workbook.add_sheet('My Worksheet')
    worksheet.write(0, 0, label = '加工物料序号')
    worksheet.write(0, 1, label = '加工CNC编号')
    worksheet.write(0, 2, label = '上料开始时间')
    worksheet.write(0, 3, label = '下料开始时间')


    length=len(Product_list)
    for i in range(length):
        worksheet.write(i+1, 0, label = Product_list[i].num)
        worksheet.write(i+1, 1, label = Product_list[i].CNC_num)
        worksheet.write(i+1, 2, label = Product_list[i].start_time)
        worksheet.write(i+1, 3, label = Product_list[i].finish_time)

    
    workbook.save('第三组数据.xls')

    




##主体函数

def main():
    TIME=0#全局时间
    STOP_TIME=8*60*60
    #初始化CNC序列
    CNC_list=[]
    for i in range(8):
        CNC_list.append(CNC_WORKBENCH(i+1))
    #初始化一个机器人
    ROBOT=RGV_ROBOT()

    #初始化任务等待队列
    Waitting_PROJECT_list=[]
    #初始化物料列表
    Product_list=[]

    #任务序号累积
    project_num=0
    #物料序号累积
    product_num=0

    #完成物料数
    complete_num=0
    #RGV位置
    position_list=[]

    #工作台累积工作时间
    work_time_list=[0,0,0,0,0,0,0,0]
    

    #开始进行时间推演
    while TIME<=STOP_TIME:

        #遍历所有CNC工作台，判断是否需要发出任务
        for i in range(len(CNC_list)):
            #如果CNC工作台正在等待上料且未发出任务请求，发出任务1请求
            if CNC_list[i].status==0 and CNC_list[i].send_PROJECT==0:
                project_num=project_num+1
                work_time=CNC_list[i].calculate_workTime()
                Waitting_PROJECT_list.append(PROJECT(1,project_num,CNC_list[i].num,CNC_list[i].position,TIME,work_time))
                CNC_list[i].send_PROJECT=1
        #如果CNC工作台正在等待下料且未发出任务请求，发出任务2请求
            if CNC_list[i].status==2 and CNC_list[i].send_PROJECT==0:
                project_num=project_num+1
                work_time=CNC_list[i].calculate_workTime()+T_clean
                Waitting_PROJECT_list.append(PROJECT(2,project_num,CNC_list[i].num,CNC_list[i].position,TIME,work_time))
                CNC_list[i].send_PROJECT=1
        
        #开始考虑RGV的情况
        #RGV已完成任务，等待任务队列中有任务，开始进行任务决策
        
        if ROBOT.PROJECT_remaining_time==0 and len(Waitting_PROJECT_list)>0:
            position_list.append(ROBOT.current_position)
            #遍历任务等待序列，计算优先级
            max_priority=-100
            max_order=-100
            for i in range(len(Waitting_PROJECT_list)):
                Waitting_PROJECT_list[i].priority_generate(ROBOT.current_position)
				

                #
                #print(str(Waitting_PROJECT_list[i].num)+"\t"+str(Waitting_PROJECT_list[i].priority))
                #





				
                if Waitting_PROJECT_list[i].priority>=max_priority:
                    max_priority=Waitting_PROJECT_list[i].priority
                    max_order=i
            #接受最大优先级任务
            ROBOT.Accept_PROJECT(Waitting_PROJECT_list[max_order],TIME)
            '''
            print("##########################")
            print("任务"+str(ROBOT.current_PROJECT.num)+"的移动时间为"+str(ROBOT.Moving_remaining_time)+",总剩余时间为"+str(ROBOT.PROJECT_remaining_time)+",等待时间为"+str(ROBOT.current_PROJECT.wait_time))
            print("任务目标："+str(ROBOT.current_PROJECT.Initiator_CNC_num))
            '''
            #在等待任务序列中删除该任务
            del Waitting_PROJECT_list[max_order]

            #如果RGV无需移动，立即开始上下料
            if ROBOT.Moving_remaining_time==0:
                #如果RGV恰好移动结束
                #if ROBOT.PROJECT_remaining_time==ROBOT.current_PROJECT.work_time:
                #修改机器人当前位置
                ROBOT.current_position=ROBOT.next_position
                #如果任务是单纯上料任务
                if ROBOT.current_PROJECT.type==1:
                    #生成一个物料 
                    product_num=product_num+1
                    cnc_num=ROBOT.current_PROJECT.Initiator_CNC_num
                    Product_list.append(PRODUCT(product_num,cnc_num,TIME))

                    '''
                    print("##########################")
                    print("时间："+str(TIME)+'s')
                    print("任务号："+str(ROBOT.current_PROJECT.num))
                    print("CNC编号："+str(cnc_num))
                    print("上料："+str(product_num))
                    '''
                    

                    #更新CNC工作台信息
                    CNC_list[cnc_num-1].status=1
                    CNC_list[cnc_num-1].current_PRODUCT_num=product_num
                    CNC_list[cnc_num-1].send_PROJECT=0
                    CNC_list[cnc_num-1].Processing_time_remaining=T_process_A

                #如果是 下料-上料-清洗 任务
                if ROBOT.current_PROJECT.type==2:
                    cnc_num=ROBOT.current_PROJECT.Initiator_CNC_num#获取CNC工作台编号
                    pro_num=CNC_list[cnc_num-1].current_PRODUCT_num#获取被下料编号

                    #更新被下料信息
                    Product_list[pro_num-1].finish_time=TIME

                    #生成一个物料
                    product_num=product_num+1
                    Product_list.append(PRODUCT(product_num,cnc_num,TIME))

                    '''
                    print("##########################")
                    print("时间："+str(TIME)+'s')
                    print("任务号："+str(ROBOT.current_PROJECT.num))
                    print("CNC编号："+str(cnc_num))
                    print("下料："+str(pro_num))
                    print("上料："+str(product_num))
                    '''

                    
                    #更新CNC工作台信息
                    CNC_list[cnc_num-1].status=1
                    CNC_list[cnc_num-1].current_PRODUCT_num=product_num
                    CNC_list[cnc_num-1].send_PROJECT=0
                    CNC_list[cnc_num-1].Processing_time_remaining=T_process_A

        #RGV未完成任务
        else:
            if ROBOT.Moving_remaining_time>0:
                position_list.append(0)
            if ROBOT.Moving_remaining_time<0:
                position_list.append(ROBOT.current_position)
            #如果RGV恰好移动结束
            if ROBOT.Moving_remaining_time==0:
                #如果RGV恰好移动结束
                #if ROBOT.PROJECT_remaining_time==ROBOT.current_PROJECT.work_time:
                #修改机器人当前位置
                ROBOT.current_position=ROBOT.next_position
                #记录位置
                position_list.append(ROBOT.current_position)
                #如果任务是单纯上料任务
                if ROBOT.current_PROJECT.type==1:
                    #生成一个物料 
                    product_num=product_num+1
                    cnc_num=ROBOT.current_PROJECT.Initiator_CNC_num
                    Product_list.append(PRODUCT(product_num,cnc_num,TIME))

                    '''
                    print("##########################")
                    print("时间："+str(TIME)+'s')
                    print("任务号："+str(ROBOT.current_PROJECT.num))
                    print("CNC编号："+str(cnc_num))
                    print("上料："+str(product_num))
                    '''
                    

                    #更新CNC工作台信息
                    CNC_list[cnc_num-1].status=1
                    CNC_list[cnc_num-1].current_PRODUCT_num=product_num
                    CNC_list[cnc_num-1].send_PROJECT=0
                    CNC_list[cnc_num-1].Processing_time_remaining=T_process_A

                #如果是 下料-上料-清洗 任务
                if ROBOT.current_PROJECT.type==2:
                    cnc_num=ROBOT.current_PROJECT.Initiator_CNC_num#获取CNC工作台编号
                    pro_num=CNC_list[cnc_num-1].current_PRODUCT_num#获取被下料编号

                    #更新被下料信息
                    Product_list[pro_num-1].finish_time=TIME
                    #生成一个物料
                    product_num=product_num+1
                    Product_list.append(PRODUCT(product_num,cnc_num,TIME))
                    '''
                    print("##########################")
                    print("时间："+str(TIME)+'s')
                    print("任务号："+str(ROBOT.current_PROJECT.num))
                    print("CNC编号："+str(cnc_num))
                    print("下料："+str(pro_num))
                    print("上料："+str(product_num))
                    '''

                    #更新CNC工作台信息
                    CNC_list[cnc_num-1].status=1
                    CNC_list[cnc_num-1].current_PRODUCT_num=product_num
                    CNC_list[cnc_num-1].send_PROJECT=0
                    CNC_list[cnc_num-1].Processing_time_remaining=T_process_A
    
        #开始进行时间推移
        TIME=TIME+1#全局时间加1秒
        #遍历工作台，若工作台在工作中，则剩余时间减1秒
        for i in range(len(CNC_list)):
            if CNC_list[i].status==1:
                work_time_list[i]=work_time_list[i]+1
                CNC_list[i].Processing_time_remaining=CNC_list[i].Processing_time_remaining-1
                if CNC_list[i].Processing_time_remaining==0:
                    CNC_list[i].status=2
                    
        #遍历任务等待队列，等待时间加1秒
        for i in range(len(Waitting_PROJECT_list)):
            Waitting_PROJECT_list[i].wait_time=Waitting_PROJECT_list[i].wait_time+1
        #讨论RGV机器人时间变化
        if ROBOT.PROJECT_remaining_time>0:
            ROBOT.PROJECT_remaining_time=ROBOT.PROJECT_remaining_time-1
            #if ROBOT.Moving_remaining_time>0:
            ROBOT.Moving_remaining_time=ROBOT.Moving_remaining_time-1
    
    #显示结果
    print('\t'+"加工物料序号"+'\t'+'加工CNC编号'+'\t'+'上料开始时间'+'\t'+'下料开始时间'+'\t')
    for i in range(len(Product_list)):
        print(Product_list[i].print_data())
        if Product_list[i].finish_time!=-1:
            complete_num=complete_num+1
    
    print("8小时产量："+str(complete_num))

    print(len(position_list))
    saveDATA(position_list,Product_list)

    all=0
    for i in range(len(work_time_list)):
        work_time_list[i]=work_time_list[i]/TIME
        all=all+work_time_list[i]
    print(all/8)


main()
