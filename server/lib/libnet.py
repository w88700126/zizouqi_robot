# -*- coding: utf-8 -*-
from public import *
# from datapack import *
# from pbpack import *
# from kcppbpack import *
import netlibproxy
import marshal
from netlibproxy import HttpGetPage
import json
class CTimerObj:
	def __init__(self,pid):
		self.m_ID=pid
		self.m_TimerList={}
		self.m_AoiPackList={}
		GetNetObjMgr().Add(self)
		
	def SetAoiPack(self,idx,data):
		self.m_AoiPackList[idx]=data
		
	def GetAoiPack(self,idx):
		return self.m_AoiPackList.get(idx)
		
	def SetTimer(self,iTime,Func,sFlag):
		tobj=self.m_TimerList.get(sFlag)
		if tobj and tobj.active():
			tobj.cancel()
		if isinstance(Func,Functor):
			if self in Func.m_Args:
				raise Exception("循环引用")
		self.m_TimerList[sFlag]=netlibproxy.CallLater(iTime,Functor(OnTimerCall,self.m_ID,sFlag,Func),sFlag)
		
	def DelTimer(self,sFlag):
		tobj=self.m_TimerList.get(sFlag)
		if tobj and tobj.active():
			tobj.cancel()
		self.m_TimerList.pop(sFlag,None)
		
	def GetTimer(self,sFlag):
		return self.m_TimerList.get(sFlag)
	
	def HasActiveTimer(self, sFlag):
		tobj=self.m_TimerList.get(sFlag)
		return tobj and tobj.active()
	
	def ClearTimer(self):
		self.m_TimerList={}

def OnTimerCall(pid,sFlag,Func):
	if pid!=0:
		obj=GetObject(pid)
	else:
		obj=g_Timer
	if not obj:
		return
	obj.DelTimer(sFlag)
	Func()

class CNetObj(CTimerObj):
	def __init__(self,pid):
		CTimerObj.__init__(self,pid)
		self.m_Commend=None
		
	def SetCommend(self,func):
		self.m_Commend=func
		
	def OnDisconnect(self):
		DelObject(self.m_ID)

class CNetObjMgr:
	def __init__(self):
		self.m_List={}       #所有连接都加进来，最开始客户端来的时候，都是负数的
		self.m_Players={}      #######每个玩家对应CTimerObj()对象
		
	def Get(self,pid):
		return self.m_List.get(pid)
	
	def Add(self,obj):
		if self.IsPlayerID(obj.m_ID):
			self.m_Players[obj.m_ID]=1
		self.m_List[obj.m_ID]=obj
		
	def Del(self,pid):
		#print "del",len(self.m_List),pid
		if self.m_Players.get(pid):
			del self.m_Players[pid]	
		if self.m_List.get(pid):
			self.m_List[pid].ClearTimer()
			del self.m_List[pid]

	def IsPlayerID(self,ID):
		return ID>0 and ID<MAX_PLAYER_ID

class CGSMgr:	#proxy.py用于管理链接的GS服务器
	def __init__(self):
		self.m_Conn={}
		
	def Add(self,conobj):
		if self.m_Conn.has_key(conobj.m_GSID):
			self.m_Conn[conobj.m_GSID].Disconnect()
		self.m_Conn[conobj.m_GSID]=conobj
		
	def Del(self,sKey):
		#print "del"#,self,self.m_Conn,iCon
		if  self.m_Conn.get(sKey):
			del self.m_Conn[sKey]
		#print self,self.m_Conn,iCon
			
	def Get(self,sKey):
		return self.m_Conn.get(sKey)
			
	def Size(self):
		return len(self.m_Conn)
	
	def GetConnList(self):
		return self.m_Conn

class CProxyMgr:	#gs.py用于管理链接的代理proxy服务器
	def __init__(self):
		self.m_Conn={}
		self.m_CurID=0
		
	def Add(self,conobj):
		self.m_CurID+=1
		conobj.m_ID=self.m_CurID
		self.m_Conn[self.m_CurID]=conobj
		
	def Del(self,sKey):
		#print "del"#,self,self.m_Conn,iCon
		if  self.m_Conn.get(sKey):
			del self.m_Conn[sKey]
		#print self,self.m_Conn,iCon
	
	def HasIP(self,sip):
		for i in self.m_Conn.values():
			if i.GetHost()==sip:
				return i
		return 0
			
	def Get(self,sKey):
		return self.m_Conn.get(sKey)
			
	def Size(self):
		return len(self.m_Conn)
	
	def GetConnList(self):
		return self.m_Conn
	
	def SendPack2Server(self,iServer,data,pid=0):
		con=None
		for i in self.m_Conn:
			if iServer in self.m_Conn[i].m_ProxyConnList:
				con= self.m_Conn[i]
				break
		if not con:
			return 0
		if not pid:
			con.GS2ProxySendPack(iServer,data)
		else:
			con.GS2ProxyTransPlayerPack(iServer,pid,data)
		return 1

	def IsConnect(self,iServer):
		for i in self.m_Conn:
			if iServer in self.m_Conn[i].m_ProxyConnList:
				return 1
			#else:
			#	Log("Proxy_debug","%s %s %s"%(iServer,i,self.m_Conn[i].m_ProxyConnList))
		return 0


	def GetConnectedGSList(self):
		gsList = []
		for i in self.m_Conn:
			for iServer in self.m_Conn[i].m_ProxyConnList:
				if iServer not in gsList:
					gsList.append(iServer)
		return gsList

def IsConnectGS(iServer):
	return GetProxyMgr().IsConnect(iServer)

def GetConnectedGSList():
	return GetProxyMgr().GetConnectedGSList()

def GetGSMgr():
	global g_GSMgr
	return g_GSMgr

def GetProxyMgr():
	global g_ProxyMgr
	return g_ProxyMgr

def GetGateConn():
	global g_GateConn
	return g_GateConn

def SetGateConn(conn):
	global g_GateConn
	g_GateConn=conn

def GetGate2Conn():
	global g_Gate2Conn
	return g_Gate2Conn

def SetGate2Conn(conn):
	global g_Gate2Conn
	g_Gate2Conn=conn

def PackPrepare(iCmd):
	Prepare()
	PackInt(iCmd)

def PacketJson(data):
	sText=str(json.dumps(data,ensure_ascii=False))
	PackInt(len(sText))
	PackString(sText, len(sText))

def UnpacketJson():
	ilen=UnpackInt()
	sText=UnpackString(ilen)
	return json.loads(sText)
	
def Send2MatchServer(iGuanQiaID):
	import ctrlcenter
	iServer=ctrlcenter.GetMatchServerNum(iGuanQiaID)
	return Send2Server(iServer)

def Send2ServerList(serverList,isAll=False):
	data = GetPackData()
	for iServer in serverList:
		GetProxyMgr().SendPack2Server(iServer,data)

def Send2Server(iServer,isAll=False):
	return GetProxyMgr().SendPack2Server(iServer,GetPackData())

def PacketSendEx(pid,iServer=0,isAll=False):
	if iServer:
		GetProxyMgr().SendPack2Server(iServer,GetPackData(),pid)
	else:
		PacketSend(pid)

def PacketSend(pid):
	data=GetPackData()
	Prepare()
	PackInt(GS2GATE_TRANS_DATA)
	PackLong(pid)
	PackString(data,len(data))
	#GetGate2Conn().SendData(GetPackData())
def PacketPBSend(pid,data):
	PacketSendToGate2(pid,data)
def PacketSendToGate2(pid,data):
	Prepare()
	PackInt(GS2GATE_TRANS_DATA_PB)
	PackLong(pid)
	PackString(data,len(data))
	GetGate2Conn().SendData(GetPackData())

def Send2Players(List):
	sList=marshal.dumps(List)
	data=GetPackData()
	Prepare()
	PackInt(GS2GATE_SEND_PLAYERS)
	PackInt(len(sList))
	PackString(sList,len(sList))
	PackString(data,len(data))
	#GetGate2Conn().SendData(GetPackData())
def Send2PlayersPB(List, data):
	sList = marshal.dumps(List)
	# data=GetPackData()
	Prepare()
	PackInt(GS2GATE_SEND_PLAYERS_PB)
	PackInt(len(sList))
	PackString(sList, len(sList))
	PackInt(len(data))
	PackString(data, len(data))
	GetGate2Conn().SendData(GetPackData())


def SendAllPlayers():
	data=GetPackData()
	Prepare()
	PackInt(GS2GATE_SEND_ALLPLAYERS)
	PackString(data,len(data))
	#GetGate2Conn().SendData(GetPackData())
def SendAllPlayersPB(data):
	Prepare()
	PackInt(GS2GATE_SEND_ALLPLAYERS_PB)
	PackString(data,len(data))
	GetGate2Conn().SendData(GetPackData())

def ReplaceID(pid1,pid2):
	if not pid1:
		return
	if not pid2:
		return
	if GetGate2Conn():
		GetGate2Conn().ReplaceID(pid1,pid2)
	
def Disconnect(pid):
	if not pid:
		return
	Log("gs", "GS Disconnect %d"%pid)
	if GetGate2Conn():
		GetGate2Conn().DisconnectPlayer(pid)
	'''if GetGateConn():
		GetGateConn().DisconnectPlayer(pid)
	'''
	obj=GetNetObjMgr().Get(pid)
	if not obj:
		return
	import time
	obj.m_DisconnectTime=time.time()
	obj.OnDisconnect()
	
def DelObject(pid):
	if not pid:
		return
	Log("gs", "GS DelObject %d"%pid)
	if GetGate2Conn():
		GetGate2Conn().DisconnectPlayer(pid)
	if GetGateConn():
		GetGateConn().DisconnectPlayer(pid)
	obj=GetNetObjMgr().Get(pid)
	if not obj:
		return
	obj.m_Delete=1
	GetNetObjMgr().Del(pid)
	if hasattr(obj,"AutoSave") and obj.IsAutoSave():
		if hasattr(obj,"SaveToDB"):
			obj.SaveToDB()
			import libsave
			libsave.Commit()
	
def GetObject(pid):
	if not pid:
		return
	return GetNetObjMgr().Get(pid)

def GetOnlinePlayer(pid):
	obj=GetObject(pid)
	if not obj:
		return
	if getattr(obj,"m_Loading",1):
		return
	return obj

def GetPlayers():
	List=GetNetObjMgr().m_Players.keys()
	return List

def GetTolPlayer():
	return len(GetNetObjMgr().m_Players)
	
def GetNetObjMgr():
	global g_NetObjMgr
	#print "GetNetObjMgr",g_NetObjMgr.m_List.keys()
	return g_NetObjMgr

def SetTimer(iTime,Func,sFlag):
	g_Timer.SetTimer(iTime,Func,sFlag)
	
def DelTimer(sFlag):
	g_Timer.DelTimer(sFlag)
	
def GetTimer(sFlag):
	return g_Timer.GetTimer(sFlag)

def Start():
	netlibproxy.Start()

def Stop():
	netlibproxy.Stop()

if not globals().has_key("g_GateConn"):
	g_GateConn=None
	g_Gate2Conn=None
	g_NetObjMgr=CNetObjMgr()
	g_Timer=CTimerObj(0)
	g_GSMgr=CGSMgr()
	g_ProxyMgr=CProxyMgr()



__all__=[
		"GetGateConn", "SetGateConn","GetGate2Conn", "SetGate2Conn","PackPrepare", "PacketJson", "UnpacketJson", "PacketSend","PacketSendToGate2","PacketPBSend","Send2Players","Send2PlayersPB",
		"CTimerObj", "OnTimerCall", "CNetObj", "CNetObjMgr",
		"SendAllPlayers", "SendAllPlayersPB", "PacketSendEx","ReplaceID", "Disconnect", "DelObject", "GetObject", "GetPlayers", "GetNetObjMgr",
		"SetTimer", "DelTimer", "GetTimer", "Start", "Stop", "GetTolPlayer",
		"Send2Server","Send2MatchServer","Send2ServerList",#,"Send2ServerPidList"
		"IsConnectGS","GetOnlinePlayer","GetConnectedGSList",
		"GetGSMgr","GetProxyMgr",

	"HttpGetPage",
	
	]
