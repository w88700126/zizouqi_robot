# -*- coding: utf-8 -*-
import debug; debug.Init()
import time
import math
import json

MAX_PLAYER_ID=0xffffffffffff
STARTTIME=1409500800 #2014/9/1日星期一零点

if not globals().has_key("g_TestSecond"):
	g_TestSecond=0

if not globals().has_key("g_TestTempSecond"):
	g_TestTempSecond=0
	g_Time={}
	g_CodeObjects={}
#===============================================================================
# 基础功能函数1
#===============================================================================
def eval1(sText,ns):
	# global g_CodeObjects
	# if not g_CodeObjects.get(sText) and sText.isdigit():
	#   	return int(sText)
	return eval2(sText,ns)

def eval2(sText,ns):
	ns.update(g_EvalFunc)
	global g_CodeObjects
	code=g_CodeObjects.get(sText)
	if not code:
		d={}
		code=compile("""
def f(args):
	globals().update(args)
	return %s
"""%sText,"<string>","exec")
		
		if len(g_CodeObjects)%10==0:
			Log("eval","eval list len %s %s"%(len(g_CodeObjects),sText))
		exec code in d
		
		g_CodeObjects[sText]=d["f"]
	
	return g_CodeObjects[sText](ns)

eval=eval1

def Eval(sText):
	if len(sText)>3:
		return eval
	else:
		return int

class Functor:
	def __init__(self,func,*args):
		self.m_Func=func
		self.m_Args=args
		
	def __call__(self,*args):
		return self.m_Func(*(self.m_Args+args))

def Copy(data):
	import copy
	return copy.deepcopy(data)

def MD5Code(sText):
	import md5
	a = md5.md5(sText)
	return a.hexdigest()

def ts(sflag,delta=0.0001):
	import time
	global g_Time
	if not g_Time.get(sflag):
		g_Time[sflag]=time.time()
	else:
		t=time.time()-g_Time[sflag]
		del g_Time[sflag]
		if t>delta:
			if GetServerNum()==1:
				print sflag,t
			Log("timeout","%s %s"%(sflag,t))

#===============================================================================
# 系统时间相关
#===============================================================================
def SetTestSecond(iTime):
	global g_TestSecond,g_TestTempSecond
	g_TestSecond=iTime
	g_TestTempSecond=GetRealSecond()

def GetSecond():
	global g_TestSecond,g_TestTempSecond
	if g_TestSecond>0:
		iTime=g_TestSecond+GetRealSecond()-g_TestTempSecond
	else:
		iTime=time.time()
	return int(iTime)

def GetRealSecond():
	return int(time.time())

def Localtime(iTime=0):
	if not iTime:
		iTime = GetSecond()
	return time.localtime(iTime)
#===============================================================================
# 随机函数相关
#===============================================================================
def Random(i):
	import random
	return random.randint(0, max(i-1,0))

def RanRate(rate, total=100):
	if Random(total) < rate:
		return 1
	else:
		return 0

def RandInt(i, j):#i<= 随机数 <=j
	return i+Random(j-i+1)

def RandList(lst):
	return lst[Random(len(lst))]

def RandDictKey(dct):
	lst = dct.keys()
	return RandList(lst)

def RandDictValue(dct):
	lst = dct.values()
	return RandList(lst)

#example {1:40,7:50,20:10}
def ChooseKey(List,iMaxRate=0):
	Dict={}
	k=0
	allRate=0
	for i, rate in List.items():
		if rate == 0:
			continue
		k+=List[i]
		Dict[k]=i
		if iMaxRate==0:
			allRate+=rate
	newlist=Dict.keys()
	newlist.sort()
	
	if iMaxRate==0:
		iMaxRate=allRate
	val=Random(iMaxRate)
	for i in newlist:
		if i>val:
			return Dict[i]
	return None

#example 
#   lst  = [
#		{"物品id":10000,"数量":1,"权重":100,"显示":1,},
#		{"物品id":10001,"数量":1,"权重":100,"显示":1,},
#		{"物品id":10002,"数量":1,"权重":100,"显示":1,},
#		{"物品id":10003,"数量":1,"权重":100,"显示":1,},]
#  data = ChooseKeyByList(lst, "权重")
def ChooseKeyByList(lst, keyName, iMaxRate=0):
	if not lst:
		LogException("ChooseKeyByList error")
		return
	if iMaxRate == 0:
		allRate = 0
		for d in lst:
			allRate += d[keyName]
		iMaxRate = allRate
	val=Random(iMaxRate)
	for d in lst:
		if d[keyName]>val:
			return d
		else:
			val -= d[keyName]
	return None

"""
dct = {
1:{"名称":"攻击","权重":1,"相关技能ID":43000,"需求数量":2,"效果描述":"齐集套装可增加生命",},
2:{"名称":"体力","权重":1,"相关技能ID":43001,"需求数量":3,"效果描述":"齐集套装可增加攻击",},
3:{"名称":"暴击","权重":1,"相关技能ID":43002,"需求数量":4,"效果描述":"齐集套装可增加暴击",},
}

example1
ansKey = ChooseKeyEx(dct, "权重")       ansKey 可能是 1, 2, 3

def Func(key, data):
	return key >= 2

example2
ansKey = ChooseKeyEx(dct, "权重", Func)       ansKey 可能是2, 3

"""
def ChooseKeyEx(dct, keyName, iMaxRate=0, checkFunc=None):
	List = {}
	for idx, d in dct.items():
		if checkFunc and not checkFunc(idx, d):
			continue
		List[idx] = d[keyName]
	return ChooseKey(List,iMaxRate)

def ShuffleList(list):
	import random
	random.shuffle(list)
	return list

#波动值
def GetWaveVal(iVal,iWave,iRatio=100):
	return iVal *(iRatio + RandInt(-iWave, iWave))/iRatio

def Clamp(a,mina=0,maxa=1):
	if a>maxa:
		return maxa
	if a<mina:
		return mina
	return a

#eval可能用到的函数
g_EvalFunc={}
g_EvalFunc["Random"]=Random
g_EvalFunc["RandList"]=RandList
g_EvalFunc["RandInt"]=RandInt
g_EvalFunc["RanRate"]=RanRate
g_EvalFunc["RandDictKey"]=RandDictKey
g_EvalFunc["RandDictValue"]=RandDictValue
g_EvalFunc["Clamp"]=Clamp
#===============================================================================
# Log函数相关
#===============================================================================
def Log(sfile,sText):
	f=open("../log/"+sfile+".log","a+")
	t=time.localtime(int(time.time()))
	sTime="[%04d-%02d-%02d %02d:%02d:%02d]"%(t[0],t[1],t[2],t[3],t[4],t[5])
	f.write(sTime+sText+"\n")
	f.close()

def DebugLog(sfile,sText,iDebugFlag=-1):
	if iDebugFlag==-1 or iDebugFlag:# == 1:#这里的1随时可以换成自己想打印的Debug编组
		t=time.localtime(int(time.time()))
		sTime="[%04d-%02d-%02d %02d:%02d:%02d]"%(t[0],t[1],t[2],t[3],t[4],t[5])
		#print sTime+sText
		Log(sfile,sText)

def InnerLog(sFile,sText):
	if not IsInternalServer():
		return
	Log(sFile,sText)
	
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
	
#===============================================================================
# 服务器判断相关
#===============================================================================
def GetServerNum():
	import servercnf
	return servercnf.ServerCnf["Num"]

def GetServerName():
	import servercnf
	return servercnf.ServerCnf.get("servername","未知")

def GetServerVersion():
	import servercnf
	return servercnf.ServerCnf.get("Version","1.0.0")
	
def IsGS():
	import servercnf
	return servercnf.ServerCnf.get("servertype")=="gs"
	
def IsInternalServer():#内服
	import servercnf
	return GetServerNum()<100 or servercnf.ServerCnf.get("Internal")
	
def IsProxy():
	import servercnf
	return servercnf.ServerCnf.get("servertype")=="proxy"

#===============================================================================
# 文本格式相关
#===============================================================================
def LenGBK(str1):
	wLen = 0
	for w in list(str1.decode("UTF-8")):
		if ord(w) > 255:
			wLen += 2
		else:
			wLen += 1
	return wLen

def LenUnicode(str1):
	return len(str1.decode("UTF-8"))

def CutUTF8Str(st, iLen):#截取字符串 ,  按照汉字长度为2, 数字英文长度为1 截取
	n = 0
	lst = []
	for w in list(st.decode("UTF-8")):
		if ord(w) > 255:
			wLen = 2
		else:
			wLen = 1
			
		if n + wLen > iLen:
			break
		
		n += wLen
		lst.append(w)
		
	st = u"".join(lst)
	return st.encode("UTF-8")
#===============================================================================
# 打印复杂数据相关
#===============================================================================
global G_Tab
def printd(data):
	global G_Tab
	G_Tab=0
	if type(data) is dict:
		print "{"
		for k,v in data.iteritems():
			if type(v) is dict: 
				writdict(k,v)
			elif type(v) is list:
				writlist(k,v)
			else:
				writnormal(k,v)
		print "}"
	elif type(data) is list:
		writlist("",data)
	else:
		print data
	G_Tab=0

def writdict(k,v):
	global G_Tab
	for i in xrange(G_Tab):
		print "    ",
	writone(k)
	print ":{"
	G_Tab+=1
	for k1,v1 in v.iteritems():
		if type(v1) is dict:
			writdict(k1,v1)
		elif type(v1) is list:
			writlist(k1,v1)
		else:
			writnormal(k1,v1)
	for i in xrange(G_Tab):
		print "    ",
	print "},"
	G_Tab-=1

def writlist(k,v):
	global G_Tab
	for i in xrange(G_Tab):
		print "    ",
	if k:
		writone(k)
		print ":["
	else:
		print "["
	G_Tab+=1
	for v1 in v:
		if type(v1) is dict:
			for i in xrange(G_Tab):
				print "    ",
			print "{"
			for k2,v2 in v1.iteritems():
				if type(v2) is dict:
					writdict(k2,v2)
				elif type(v2) is list:
					writlist(k2,v2)
				else:
					writnormal(k2,v2)
			for i in xrange(G_Tab):
				print "    ",
			print "},"
		elif type(v1) is list:
			for v2 in v1:
				writlist(k,v2)
		else:
			for i in xrange(G_Tab):
				print "    ",
			writone(v1)
			print ","
	for i in xrange(G_Tab):
		print "    ",
	print "],"
	G_Tab-=1

def writnormal(k,v):
	global G_Tab
	for i in xrange(G_Tab):
		print "    ",
	writone(k)
	print ":",
	writone(v)
	print ","

def writone(kv):
	if type(kv) is int or type(kv) is float or type(kv) is bool:# or not kv
		print kv,
	elif type(kv) is long:
		print "%sL"%kv,
	elif type(kv) is tuple:
		print "(",
		for v3 in kv:
			writone(v3)
			print ",",
		print ")",
	else:
		print "\"%s\""%(kv),