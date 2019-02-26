# -*- coding: utf-8 -*-
import debug; debug.Init()
import time
MAX_PLAYER_ID	=	0xffffffffffff

if not globals().has_key("g_Time"):
	g_Time={}
	
class Functor:
	def __init__(self,func,*args):
		self.m_Func=func
		self.m_Args=args
		
	def __call__(self,*args):
		return self.m_Func(*(self.m_Args+args))
	
def GetSecond():
	return int(time.time())

def Log(sfile,sText):
	f=open("../log/"+sfile+".log","a+")
	t=time.localtime()
	sTime="[%04d-%02d-%02d %02d:%02d:%02d]"%(t[0],t[1],t[2],t[3],t[4],t[5])
	f.write(sTime+sText+"\n")
	f.close()

def DebugLog(sfile,sText,iDebugFlag=-1):
	if iDebugFlag==-1 or iDebugFlag:#这里的1随时可以换成自己想打印的Debug编组
		t=time.localtime()
		sTime="[%04d-%02d-%02d %02d:%02d:%02d]"%(t[0],t[1],t[2],t[3],t[4],t[5])
		#print sTime+sText
		Log(sfile,sText)

def Localtime(iTime=0):
	if not iTime:
		iTime = GetSecond()
	return time.localtime(iTime)

def LogException(sText=""):
	import traceback, sys
	f=open("../log/exception.log","a+")
	t=Localtime()
	sTime="[%04d-%02d-%02d %02d:%02d:%02d]  %s"%(t[0],t[1],t[2],t[3],t[4],t[5], sText)
	lst = [sTime]
	info = sys.exc_info()
	for file, lineno, function, text in traceback.extract_stack()[:-2]:
		lst.append("%s line: %s in %s"%(file, lineno, function))
	txt = "\n".join(lst)
	f.write(txt+"\n")
	f.close()
	
	print "LogException :" + txt
	
def Random(i):
	import random
	return random.randint(0, max(i-1,0))
	
def writepid(type="pid"):
	import servercnf,os
	f=open("../"+servercnf.ServerCnf["DataBaseName"]+"_"+servercnf.ServerCnf["servertype"]+".%s"%type,"w")
	f.write(str(os.getpid())+"\n")
	f.close()
	
def ts(sflag,delta=0.0001):
	import servercnf
	import time
	global g_Time
	if not g_Time.get(sflag):
		g_Time[sflag]=time.time()
	else:
		t=time.time()-g_Time[sflag]
		del g_Time[sflag]
		if t>delta:
			Log("timeout%s"%servercnf.ServerCnf["servertype"],"%s %s"%(sflag,t))

GATE2GS_TRANS_DATA=1
GATE2GS_CMD=2
GATE2GS_HELLO=3
GATE2GS_DISCONNECT=4
GS2GATE_TRANS_DATA=1
GS2GATE_CMD=2
GS2GATE_HELLO=3
GS2GATE_DISCONNECT=4
GS2GATE_REPLACEID=5
GS2GATE_SEND_PLAYERS=6
GS2GATE_SEND_ALLPLAYERS=7
GS2GATE_SYNC_POS=8

GATE2GS_TRANS_PBDATA = 9
GS2GATE_TRANS_DATA_PB = 10
GS2GATE_SEND_PLAYERS_PB = 11
GS2GATE_SEND_ALLPLAYERS_PB = 12

GS2AOI_ADD_SCENE=1
GS2AOI_DEL_SCENE=2
GS2AOI_GOTO_SCENE=3
GS2AOI_LEAVE_SCENE=4
GS2AOI_MOVE=5
GS2AOI_BROCAST=6

AOI2GS_ADD=1
AOI2GS_DEL=2
AOI2GS_POS=3
AOI2GS_RANGSET=4
AOI2GS_SCLOADED=5
AOI2GS_BROCAST=6

PROXY2GS_PACK=1
PROXY2GSLIST_PACK=2
PROXY2GS_PLAYER_PACK=3
PROXY2GS_CONNECT_LIST=4

GS2PROXY_PACK=1
GS2PROXYLIST_PACK=2
GS2PROXY_PLAYER_PACK=3

GS2ES_TRIGGER_EVENT = 1

ES2GS_EVENT_DOHANDLE = 1

GS2MATCH_CREAT_TEAM = 1
GS2MATCH_JOIN_TEAM = 5
GS2MATCH_LEAVE_TEAM = 6
GS2MATCH_APPLY_HANDLE = 8

FMS2FRS_APPLY_ROOM = 2
FRS2FMS_APPLY_ROOM =1
FRS2FMS2GS_FIGHT_OUT =3
FRS2FMS2GS_FIGHT_END =4
FRS2FMS_FRS_HARDWARE = 5

if __name__=="__main__":
	a=Functor(Test,1,2)
	a(3,4)