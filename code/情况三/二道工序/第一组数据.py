import copy
import random
import xlwt

####################
######全局参数定义######
####################

#RGV 移动 1 个单位所需时间
T_move1=20
#RGV 移动 2 个单位所需时间
T_move2=33
#RGV 移动 3 个单位所需时间
T_move3=46
#CNC 加工完成一个一道工序的物料所需时间
T_process_A=560
#CNC 加工完成一个两道工序物料的第一道工序所需时间
T_process_B1=400
#CNC 加工完成一个两道工序物料的第二道工序所需时间
T_process_B2=378
#RGV 为 CNC1#，3#，5#，7#一次上下料所需时间
T_IO_odd=28
#RGV 为 CNC2#，4#，6#，8#一次上下料所需时间
T_IO_even=31
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
        self.CNC_num_process_B1=CNC_num#加工物料工序1的CNC序号
        self.start_time_process_B1=start_time#工序1上料开始时刻
        self.finish_time_process_B1=-1#工序1下料开始时刻

        self.CNC_num_process_B2=-1#加工物料工序1的CNC序号
        self.start_time_process_B2=-1#工序1上料开始时刻
        self.finish_time_process_B2=-1#工序1下料开始时刻

        self.damaged=0 #报废情况 0未报废 1报废

        self.damaged_start_time=-1#故障开始时间
        self.damaged_finish_time=-1#故障结束时间
        self.damaged_CNC=-1#故障时的CNC       
        

    #显示该物料的资料
    def print_data(self):
        st='\t'+str(self.damaged)+'\t'+str(self.num)+'\t'+str(self.CNC_num_process_B1)+'\t'+str(self.start_time_process_B1)+'\t'+str(self.finish_time_process_B1)+'\t'
        st=st+str(self.CNC_num_process_B2)+'\t'+str(self.start_time_process_B2)+'\t'+str(self.finish_time_process_B2)+'\t'
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

        #self.priority=a*(self.wait_time)+b*(1/(self.move_time+1))
        #self.priority=(self.wait_time+self.work_time)/self.work_time
        self.priority=(self.wait_time+self.move_time+self.work_time)/(self.move_time+self.work_time) #250     
        #self.priority=(self.wait_time+self.move_time+self.work_time)/self.work_time


#RGV机器人类
class RGV_ROBOT:
    #构造函数
    def __init__(self):
        self.current_PROJECT=-1#当前执行的任务数据
        self.current_position=1#当前位置
        self.next_position=1#下次位置
        self.PROJECT_remaining_time=0#任务剩余时间
        self.Moving_remaining_time=0#移动剩余时间
        self.have=0 #机器人是否拿着一道料 0未拿  1拿着
        self.product_num=-1#机器人手中拿着的一道工序料的编号
    
    
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
        self.TYPE=0#工作台类型  1为一道工序  2为二道工序
        self.status=0#状态码 0等待上料  1工作中 2等待下料 3修复中
        #CNC工作台位置
        if num%2==0:
            self.position=int(num/2)
            self.TYPE=2
        else:
            self.position=int((num+1)/2)
            self.TYPE=1

        self.current_PRODUCT_num=-1#CNC工作台当前加工物料序号
        self.Processing_time_remaining=0#CNC工作台加工剩余时间
        self.send_PROJECT=0#CNC工作台是否已经发出任务 0为未发出 1为已发出

        self.health_status=0#工作台健康状况 0.健康  1.损坏
        self.repair_remaining_time=0#工作台剩余修复时间

        self.pass_damaged=0#该次加工是否通过损坏测试 0为未通过 1为已通过
    
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
    worksheet.write(0, 1, label = '工序1的CNC编号')
    worksheet.write(0, 2, label = '上料开始时间')
    worksheet.write(0, 3, label = '下料开始时间')
    worksheet.write(0, 4, label = '工序2的CNC编号')
    worksheet.write(0, 5, label = '上料开始时间')
    worksheet.write(0, 6, label = '下料开始时间')


    length=len(Product_list)
    for i in range(length):
        worksheet.write(i+1, 0, label = Product_list[i].num)
        worksheet.write(i+1, 1, label = Product_list[i].CNC_num_process_B1)
        worksheet.write(i+1, 2, label = Product_list[i].start_time_process_B1)
        worksheet.write(i+1, 3, label = Product_list[i].finish_time_process_B1)

        worksheet.write(i+1, 4, label = Product_list[i].CNC_num_process_B2)
        worksheet.write(i+1, 5, label = Product_list[i].start_time_process_B2)
        worksheet.write(i+1, 6, label = Product_list[i].finish_time_process_B2)


    worksheet = workbook.add_sheet('My Worksheet2')
    worksheet.write(0, 0, label = '故障时的物料序号')
    worksheet.write(0, 1, label = '故障CNC编号')
    worksheet.write(0, 2, label = '故障开始时间')
    worksheet.write(0, 3, label = '故障结束时间')

    num=1
    length=len(Product_list)
    for i in range(length):
        if Product_list[i].damaged==1:
            worksheet.write(num, 0, label = Product_list[i].num)
            worksheet.write(num, 1, label = Product_list[i].damaged_CNC)
            worksheet.write(num, 2, label = Product_list[i].damaged_start_time)
            worksheet.write(num, 3, label = Product_list[i].damaged_finish_time)
            num=num+1
    


    workbook.save('第一组数据.xls')






def main():
    TIME=0#全局时间
    STOP_TIME=8*60*60
    damaged_ratio=0.01#损坏概率
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


    #RGV位置
    position_list=[]


        #工作台累积工作时间
    work_time_list=[0,0,0,0,0,0,0,0]
    


    #开始进行时间推演
    while TIME<=STOP_TIME:
        #遍历工作中的工作台，通过概率生成损坏
        for i in range(len(CNC_list)):
            if CNC_list[i].status==1 and CNC_list[i].pass_damaged==0:
                x=random.random()
                if x<damaged_ratio:#该工作台损坏，工作台上的物料报废
                    #print("损坏")
                    CNC_list[i].health_status=1
                    CNC_list[i].status=3
                    CNC_list[i].Processing_time_remaining=0
                    CNC_list[i].send_PROJECT=0
                    #设置修复时间
                    CNC_list[i].repair_remaining_time=random.randint(10*60,20*60)

                    #物料报废
                    pro_num=CNC_list[i].current_PRODUCT_num
                    Product_list[pro_num-1].damaged=1
                    CNC_list[i].current_PRODUCT_num=-1

                    #####################################

                    #记录故障信息
                    Product_list[pro_num-1].damaged_start_time=TIME
                    Product_list[pro_num-1].damaged_finish_time=TIME+CNC_list[i].repair_remaining_time
                    Product_list[pro_num-1].damaged_CNC=CNC_list[i].num
                    

                    ######################################

                    break
                else:
                    CNC_list[i].pass_damaged=1


        #print("/总时间："+str(TIME))
        #遍历所有工作台，判断是否要发出任务
        for i in range(len(CNC_list)):
            #如果CNC工作台正在等待上料且未发出任务请求
            if CNC_list[i].status==0 and CNC_list[i].send_PROJECT==0:
                #如果是一道工序工作台，发出任务1请求
                if CNC_list[i].TYPE==1:
                    project_num=project_num+1
                    work_time=CNC_list[i].calculate_workTime()
                    Waitting_PROJECT_list.append(PROJECT(1,project_num,CNC_list[i].num,CNC_list[i].position,TIME,work_time))
                    CNC_list[i].send_PROJECT=1
                #如果是二道工序工作台，发出任务3请求
                if CNC_list[i].TYPE==2:
                    project_num=project_num+1
                    work_time=CNC_list[i].calculate_workTime()
                    Waitting_PROJECT_list.append(PROJECT(3,project_num,CNC_list[i].num,CNC_list[i].position,TIME,work_time))
                    CNC_list[i].send_PROJECT=1

            #如果CNC工作台正在等待下料且未发出任务请求
            if CNC_list[i].status==2 and CNC_list[i].send_PROJECT==0:
                #如果是一道工序工作台，发出任务2请求
                if CNC_list[i].TYPE==1:
                    project_num=project_num+1
                    work_time=CNC_list[i].calculate_workTime()
                    Waitting_PROJECT_list.append(PROJECT(2,project_num,CNC_list[i].num,CNC_list[i].position,TIME,work_time))
                    CNC_list[i].send_PROJECT=1
                #如果是二道工序工作台，发出任务4请求
                if CNC_list[i].TYPE==2:
                    project_num=project_num+1
                    work_time=CNC_list[i].calculate_workTime()+T_clean
                    Waitting_PROJECT_list.append(PROJECT(4,project_num,CNC_list[i].num,CNC_list[i].position,TIME,work_time))
                    CNC_list[i].send_PROJECT=1

        #开始考虑RGV的情况
        #RGV已完成任务，等待任务队列中有任务，开始进行任务决策
        if ROBOT.PROJECT_remaining_time==0 and len(Waitting_PROJECT_list)>0:
            position_list.append(ROBOT.current_position)
            max_priority=-100
            max_order=-100
            #RGV机器人手中没有物料，挑选任务1和2
            if ROBOT.have==0:
                #遍历任务等待序列，计算优先级
                for i in range(len(Waitting_PROJECT_list)):
                    if Waitting_PROJECT_list[i].type==1 or Waitting_PROJECT_list[i].type==2:
                        Waitting_PROJECT_list[i].priority_generate(ROBOT.current_position)
                        #
                        #print(str(Waitting_PROJECT_list[i].num)+"\t"+str(Waitting_PROJECT_list[i].priority))
                        #
                        if Waitting_PROJECT_list[i].priority>=max_priority:
                            max_priority=Waitting_PROJECT_list[i].priority
                            max_order=i      

            #RGV机器人手中有一道工序物料，挑选任务1 3 4
            if ROBOT.have==1:
                #遍历任务等待序列，计算优先级
                for i in range(len(Waitting_PROJECT_list)):
                    if Waitting_PROJECT_list[i].type==1 or Waitting_PROJECT_list[i].type==3 or Waitting_PROJECT_list[i].type==4:
                        Waitting_PROJECT_list[i].priority_generate(ROBOT.current_position)
                        #
                        #print(str(Waitting_PROJECT_list[i].num)+"\t"+str(Waitting_PROJECT_list[i].priority))
                        #
                        if Waitting_PROJECT_list[i].priority>=max_priority:
                            max_priority=Waitting_PROJECT_list[i].priority
                            max_order=i  
            #接受最大优先级任务
            if max_order>=0:
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
                #修改机器人当前位置
                ROBOT.current_position=ROBOT.next_position 

                #如果是任务1 单纯上生料
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
                    print("上 生料："+str(product_num))
                    '''

                    #更新CNC工作台信息
                    CNC_list[cnc_num-1].status=1
                    CNC_list[cnc_num-1].current_PRODUCT_num=product_num
                    CNC_list[cnc_num-1].send_PROJECT=0
                    CNC_list[cnc_num-1].Processing_time_remaining=T_process_B1

                #如果是任务2 下 一道工序料 上生料
                if ROBOT.current_PROJECT.type==2:
                    cnc_num=ROBOT.current_PROJECT.Initiator_CNC_num#获取CNC工作台编号
                    pro_num=CNC_list[cnc_num-1].current_PRODUCT_num#获取被下一道工序料编号

                    #更新被下 一道工序料 信息
                    Product_list[pro_num-1].finish_time_process_B1=TIME
                    #生成一个物料
                    product_num=product_num+1
                    Product_list.append(PRODUCT(product_num,cnc_num,TIME))

                    '''
                    print("##########################")
                    print("时间："+str(TIME)+'s')
                    print("任务号："+str(ROBOT.current_PROJECT.num))
                    print("CNC编号："+str(cnc_num))
                    print("下 一道工序料："+str(pro_num))
                    print("上 生料："+str(product_num))
                    '''


                    #更新CNC工作台信息
                    CNC_list[cnc_num-1].status=1
                    CNC_list[cnc_num-1].current_PRODUCT_num=product_num
                    CNC_list[cnc_num-1].send_PROJECT=0
                    CNC_list[cnc_num-1].Processing_time_remaining=T_process_B1
                    #更新RGV机器手上的 物料数据
                    ROBOT.have=1
                    ROBOT.product_num=pro_num

                #如果是任务3 单纯上 一道工序料
                if ROBOT.current_PROJECT.type==3:
                    cnc_num=ROBOT.current_PROJECT.Initiator_CNC_num#获取CNC工作台编号
                    pro_num=ROBOT.product_num#获取当前 机器手中的 一道工序物料编号
                    
                    #更新该 一道工序物料 的信息
                    Product_list[pro_num-1].CNC_num_process_B2=cnc_num
                    Product_list[pro_num-1].start_time_process_B2=TIME

                    '''
                    print("##########################")
                    print("时间："+str(TIME)+'s')
                    print("任务号："+str(ROBOT.current_PROJECT.num))
                    print("CNC编号："+str(cnc_num))
                    print("上 一道工序料："+str(pro_num))

                    '''
                    #更新CNC工作台信息
                    CNC_list[cnc_num-1].status=1
                    CNC_list[cnc_num-1].current_PRODUCT_num=pro_num
                    CNC_list[cnc_num-1].send_PROJECT=0
                    CNC_list[cnc_num-1].Processing_time_remaining=T_process_B2

                    #更新RGV机器手上的 物料数据
                    ROBOT.have=0
                    ROBOT.product_num=-1


                #如果是任务4 上 一道工序料 下 熟料 并清洗
                if ROBOT.current_PROJECT.type==4:
                    cnc_num=ROBOT.current_PROJECT.Initiator_CNC_num#获取CNC工作台编号
                    pro_num=ROBOT.product_num#获取当前 机器手中的 一道工序物料编号
                    pro_num2=CNC_list[cnc_num-1].current_PRODUCT_num#获取被下 熟料 编号

                    #更新 一道工序料 信息
                    Product_list[pro_num-1].CNC_num_process_B2=cnc_num
                    Product_list[pro_num-1].start_time_process_B2=TIME

                    #更新 熟料 信息
                    Product_list[pro_num2-1].finish_time_process_B2=TIME

    
                    '''
                    print("##########################")
                    print("时间："+str(TIME)+'s')
                    print("任务号："+str(ROBOT.current_PROJECT.num))
                    print("CNC编号："+str(cnc_num))
                    print("下 熟料："+str(pro_num2))
                    print("上 一道工序料："+str(pro_num))
                    '''


                     #更新CNC工作台信息
                    CNC_list[cnc_num-1].status=1
                    CNC_list[cnc_num-1].current_PRODUCT_num=pro_num
                    CNC_list[cnc_num-1].send_PROJECT=0
                    CNC_list[cnc_num-1].Processing_time_remaining=T_process_B2

                    #更新RGV机器手上的 物料数据
                    ROBOT.have=0
                    ROBOT.product_num=-1








            

        #RGV未完成任务
        else:
            if ROBOT.Moving_remaining_time>0:
                position_list.append(0)
            if ROBOT.Moving_remaining_time<0:
                position_list.append(ROBOT.current_position)                 
            #如果RGV恰好移动结束
            if ROBOT.Moving_remaining_time==0:  
                #修改机器人当前位置
                ROBOT.current_position=ROBOT.next_position
                position_list.append(ROBOT.current_position)

                #如果是任务1 单纯上生料
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
                    print("上 生料："+str(product_num))

                    '''

                    #更新CNC工作台信息
                    CNC_list[cnc_num-1].status=1
                    CNC_list[cnc_num-1].current_PRODUCT_num=product_num
                    CNC_list[cnc_num-1].send_PROJECT=0
                    CNC_list[cnc_num-1].Processing_time_remaining=T_process_B1

                #如果是任务2 下 一道工序料 上生料
                if ROBOT.current_PROJECT.type==2:
                    cnc_num=ROBOT.current_PROJECT.Initiator_CNC_num#获取CNC工作台编号
                    pro_num=CNC_list[cnc_num-1].current_PRODUCT_num#获取被下一道工序料编号

                    #更新被下 一道工序料 信息
                    Product_list[pro_num-1].finish_time_process_B1=TIME
                    #生成一个物料
                    product_num=product_num+1
                    Product_list.append(PRODUCT(product_num,cnc_num,TIME))


                    '''
                    print("##########################")
                    print("时间："+str(TIME)+'s')
                    print("任务号："+str(ROBOT.current_PROJECT.num))
                    print("CNC编号："+str(cnc_num))
                    print("下 一道工序料："+str(pro_num))
                    print("上 生料："+str(product_num))

                    '''


                    #更新CNC工作台信息
                    CNC_list[cnc_num-1].status=1
                    CNC_list[cnc_num-1].current_PRODUCT_num=product_num
                    CNC_list[cnc_num-1].send_PROJECT=0
                    CNC_list[cnc_num-1].Processing_time_remaining=T_process_B1
                    #更新RGV机器手上的 物料数据
                    ROBOT.have=1
                    ROBOT.product_num=pro_num

                #如果是任务3 单纯上 一道工序料
                if ROBOT.current_PROJECT.type==3:
                    cnc_num=ROBOT.current_PROJECT.Initiator_CNC_num#获取CNC工作台编号
                    pro_num=ROBOT.product_num#获取当前 机器手中的 一道工序物料编号
                    
                    #更新该 一道工序物料 的信息
                    Product_list[pro_num-1].CNC_num_process_B2=cnc_num
                    Product_list[pro_num-1].start_time_process_B2=TIME


                    '''
                    print("##########################")
                    print("时间："+str(TIME)+'s')
                    print("任务号："+str(ROBOT.current_PROJECT.num))
                    print("CNC编号："+str(cnc_num))
                    print("上 一道工序料："+str(pro_num))
                    '''


                    #更新CNC工作台信息
                    CNC_list[cnc_num-1].status=1
                    CNC_list[cnc_num-1].current_PRODUCT_num=pro_num
                    CNC_list[cnc_num-1].send_PROJECT=0
                    CNC_list[cnc_num-1].Processing_time_remaining=T_process_B2

                    #更新RGV机器手上的 物料数据
                    ROBOT.have=0
                    ROBOT.product_num=-1


                #如果是任务4 上 一道工序料 下 熟料 并清洗
                if ROBOT.current_PROJECT.type==4:
                    cnc_num=ROBOT.current_PROJECT.Initiator_CNC_num#获取CNC工作台编号
                    pro_num=ROBOT.product_num#获取当前 机器手中的 一道工序物料编号
                    pro_num2=CNC_list[cnc_num-1].current_PRODUCT_num#获取被下 熟料 编号

                    #更新 一道工序料 信息
                    Product_list[pro_num-1].CNC_num_process_B2=cnc_num
                    Product_list[pro_num-1].start_time_process_B2=TIME

                    #更新 熟料 信息
                    Product_list[pro_num2-1].finish_time_process_B2=TIME

                    '''
                    print("##########################")
                    print("时间："+str(TIME)+'s')
                    print("任务号："+str(ROBOT.current_PROJECT.num))
                    print("CNC编号："+str(cnc_num))
                    print("下 熟料："+str(pro_num2))
                    print("上 一道工序料："+str(pro_num))
                    '''


                     #更新CNC工作台信息
                    CNC_list[cnc_num-1].status=1
                    CNC_list[cnc_num-1].current_PRODUCT_num=pro_num
                    CNC_list[cnc_num-1].send_PROJECT=0
                    CNC_list[cnc_num-1].Processing_time_remaining=T_process_B2

                    #更新RGV机器手上的 物料数据
                    ROBOT.have=0
                    ROBOT.product_num=-1
        


        #开始进行时间推移
        TIME=TIME+1#全局时间加1秒
        #遍历工作台，若工作台在工作中，则剩余时间减1秒
        for i in range(len(CNC_list)):
            #若工作台在工作中，则剩余时间减1秒
            if CNC_list[i].status==1:
                work_time_list[i]=work_time_list[i]+1
                CNC_list[i].Processing_time_remaining=CNC_list[i].Processing_time_remaining-1
                if CNC_list[i].Processing_time_remaining==0:#若完成工作，则置为完成态
                    CNC_list[i].status=2    
            #若工作台在修复中，则剩余时间减1秒
            if CNC_list[i].status==3:
                CNC_list[i].repair_remaining_time=CNC_list[i].repair_remaining_time-1
                if CNC_list[i].repair_remaining_time==0:
                    CNC_list[i].status=0
                    CNC_list[i].health_status=0
                    CNC_list[i].pass_damaged=0

        #遍历任务等待队列，等待时间加1秒
        for i in range(len(Waitting_PROJECT_list)):
            Waitting_PROJECT_list[i].wait_time=Waitting_PROJECT_list[i].wait_time+1
        #讨论RGV机器人时间变化
        if ROBOT.PROJECT_remaining_time>0:
            ROBOT.PROJECT_remaining_time=ROBOT.PROJECT_remaining_time-1
            #if ROBOT.Moving_remaining_time>0:
            ROBOT.Moving_remaining_time=ROBOT.Moving_remaining_time-1

    complete_num=0
    #显示结果
    print('\t'+'损坏情况'+'\t'+"加工物料序号"+'\t'+'1道工序加工CNC编号'+'\t'+'1道工序上料开始时间'+'\t'+'1道工序下料开始时间'+'\t'+'2道工序加工CNC编号'+'\t'+'2道工序上料开始时间'+'\t'+'2道工序下料开始时间'+'\t')
    for i in range(len(Product_list)):
        print(Product_list[i].print_data())
    
        if Product_list[i].start_time_process_B1>0 and Product_list[i].finish_time_process_B1>0 and Product_list[i].start_time_process_B2>0 and Product_list[i].finish_time_process_B2>0:
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
