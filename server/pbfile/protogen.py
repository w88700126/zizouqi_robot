# -*- coding: utf-8 -*-
import sys
import os
sys.path.insert(0,"../lib/")
import libprint

def file_name(file_dir,str,sFenGeFu):
	L=[]
	Onceupdate=True
	need_path3= ""
	for root, dirs, files in os.walk(file_dir):
		for file in files:
			if Onceupdate:
				now_path = os.path.realpath(file)
				father_path = os.path.dirname(now_path)
				final_path = os.path.dirname(father_path)
				need_path = final_path.replace("3_server", "2_client\\RedAlertLaya\\laya\\assets\\proto")
				if need_path:
					Onceupdate = False
					need_path2=need_path+str
					need_path3=need_path
			if os.path.splitext(file)[1] == '.proto':
				L.append(file)
	print "===>",need_path2
# 	print "2===>",L
	if "MsgID.proto" in L:
		L.remove("MsgID.proto")
		L.insert(0,"MsgID.proto")
	print "3===>",L
	with open(need_path2, "w+") as fo:
		fo.write('syntax  = "proto3";'+'\n'+'package netPackage;'+'\n'+'\n')
		for i in L:
			with open(i, "a+") as fotest:
				bHaveNosFenGeFu=True
				bIsNull=False
				for j in xrange(100):
					sFile=fotest.readline()
					if sFile.find(sFenGeFu)!=-1:
						bHaveNosFenGeFu=False
						break
				if bHaveNosFenGeFu==True:
					print i+"没有找到分隔符，读取失败"
					break
				else:
					var=fotest.read()
					if not var:
						print i + "内容为空，读取失败"
						bIsNull = True
						break
					fo.write('//============'+i+'开始====================================================================\n')
					fo.write(var)
					fo.write('\n'+'//============'+i+'结束====================================================================\n'+'\n')

	if bHaveNosFenGeFu == True or bIsNull==True:
		os.remove(need_path2)
	else:
		print "proto.proto生成成功"
		os.system("start explorer %s"%need_path3)

def file_name2(file_dir):
	L=[]
	for root, dirs, files in os.walk(file_dir):
		for file in files:
			if os.path.splitext(file)[1] == '.proto':
				L.append(file)
	return L 

if __name__=="__main__":
	print "生成服务端proto开始"
	filelist =  file_name2("./")
	for file in filelist:
		os.system('protoc.exe -I=./   --python_out=../script/proto    ./%s'%file)
	print "生成服务端proto结束"
# 	print "生成客户端proto.proto开始"
# 	sMuBan='//============以上不再客户端导表生成=============='
# 	file_name("./","\proto.proto",sMuBan)
# 	print "生成客户端proto.proto结束"
	
