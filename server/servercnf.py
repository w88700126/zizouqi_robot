# -*- coding: utf-8 -*-
import os
if os.environ.get("DOCKER"):	#docker部署
	MY_SERVER_IP_IN = "0.0.0.0"
	MY_SERVER_IP_EX = "47.107.228.44"
	MY_SERVER_NUM = int(os.environ["SERVERID"])
	MY_DB_NAME = os.environ.get("DBNAME","dv")
	MY_DB_HOST = os.environ.get("DBHOST","172.17.0.1")
	MY_DB_PWD = os.environ.get("DBPWD","testman")
else:
	MY_SERVER_IP_IN = "192.168.1.7"	#内网IP
	MY_SERVER_IP_EX = "192.168.1.7"	#外网IP
	MY_SERVER_NUM = 3			#服务器消息队列集群限制必须在1-999内,端口分配完全不重合必须限制在1-780内
	MY_DB_NAME = "dv"
	MY_DB_HOST = "127.0.0.1"
	MY_DB_PWD = "testman"
SN = MY_SERVER_NUM

ServerCnf={
	"Num"	:			SN,
	"Player2GatePort":	10000+SN*50,
	"GS2DBPort":		10001+SN*50,
	"GS2GatePort":		10002+SN*50,
	"AOI2GSPort":		10003+SN*50,
	"Proxy2GSPort":		10004+SN*50,
	"ES2GSPort":		10007+SN*50,
	"DataBaseName":		MY_DB_NAME,
	"DataBaseHost":		MY_DB_HOST,
	"DataBasePwd":		MY_DB_PWD,
	"WGSHttpPort":		10011+SN*50,
	"CSHttpPort":		10010+SN*50,
	"ClientPbPort":		10012+SN*50,
	"ApkClientPbPort":	10013+SN*50,
	"GS2Gate2Port":		10014+SN*50,
	"FRS2FMSHost":		"localhost",
	"FRS2FMSPort":		10015+SN*50,
	"FRS2CHost":		MY_SERVER_IP_EX,
	"FRS2CPort":		10016+SN*50,#占用了至10049+SN*50

	"WGS"	:	False,
	"GS"	:	True,
	"AS"	:	False,		#可能会被shell脚本传递的参数替换

	"IsPfEdit":False,  #是不是编辑器模式
	"IsDemo":False,  #是不是Demo版
	"Shape":30030,  #编辑器模式角色造型
	"DieType":0, #扣血类型 0 表示正常, 1表示无敌, 2表示一招必死, 3表示每次只扣1滴血
	"FullXP":True, #编辑器满XP
	"Friend":[30041, 30040, 30041], #战斗中的队友
	"MustBiSha":False , #必定暴击
	"servername":"内服1",

	"IsSpEdit":False,  #是不是剧情编辑器模式
	"BirthScene":1010, #一开始的场景
	"BirthX":30, #一开始的位置X
	"BirthY":70, #一开始的位置X
	"SpIdx":1001,#默认自动播放的剧情
	"PlayerSID":[50001,50002],
	"Version":"1.0.0",
	
	"Internal":True,
}
