# -*- coding: utf-8 -*-
import debug
import netlibproxy
from pbpack2 import *
from public import *
import os
from autobahn.twisted.websocket import WebSocketServerFactory, WebSocketServerProtocol, listenWS
class CConnection:
	def __init__(self,sHost,iPort,proxyObj):
		self.m_Host=sHost
		self.m_Port=iPort
		self.m_ProxyObj=proxyObj
		self.m_RecvBuff=""
		
	def Disconnect(self):
		return self.m_ProxyObj.Disconnect()
		
	def SendData(self,sData):
		# import debug
		# debug.Traceback()
		return self.m_ProxyObj.SendData(sData)
	
	def SendDataAll(self,sData):
		return self.m_ProxyObj.SendDataAll(sData)
	
	def GetHost(self):
		return self.m_Host
		
	def GetPort(self):
		return self.m_Port
		
	def GetMaxPacketSize(self):
		return 1024*1024*50
		
	def OnDataArrived(self,sData):
		#Log("connection","OnDataArrived%s %s %s %s %s"%(os.getpid(),self,self.GetHost(),self.GetPort(),len(sData)))
		#print "OnDataArrived", len(sData)
		self.m_RecvBuff+=sData
		while self.m_RecvBuff:
			iSize=CheckUnpack(self.m_RecvBuff,self.GetMaxPacketSize())
			if iSize==0:
				#Log("connection","err OnDataArrived%s 0"%os.getpid())
				break
			if iSize==-1:
				self.Disconnect()
				Log("connection","err OnDataArrived%s -1"%os.getpid())
				return
			sUnpackData,self.m_RecvBuff=self.m_RecvBuff[:iSize],self.m_RecvBuff[iSize:]
			try:
				SetForUnpack(sUnpackData)
				self.OnPacketArrived()
			except:
				debug.OutputError()

	def OnConnected(self):
		pass
		
	def OnDisconnected(self,sReason):
		pass
			
	def OnPacketArrived(self):
		pass

class CPbConnection(CConnection):
	def __init__(self,sHost,iPort,proxyObj):
		CConnection.__init__(self,sHost,iPort,proxyObj)

	def GetMaxPacketSize(self):
		return 1024*1024*50
	
	def OnDataArrived(self,sData):
		#Log("connection","OnDataArrived%s %s %s %s %s"%(os.getpid(),self,self.GetHost(),self.GetPort(),len(sData)))
		#print "OnDataArrived", len(sData)
		self.m_RecvBuff+=sData
		while self.m_RecvBuff:
			iBodyLen=CheckPBUnpack(self.m_RecvBuff,self.GetMaxPacketSize())
			if iBodyLen==0:
				Log("connection","err OnDataArrived%s PB-0"%os.getpid())
				break
			if iBodyLen==-1:
				#self.Disconnect()
				Log("connection","err OnDataArrived%s PB-1"%os.getpid())
				return
			sPBUnpackData,self.m_RecvBuff=self.m_RecvBuff[:iBodyLen],self.m_RecvBuff[iBodyLen:]
			try:
				iHead,iCMD,body,bodyEX = PBUnPack(sPBUnpackData)
				if iHead==-1:
					DebugLog("connection","err OnDataArrived%s PB-2"%os.getpid(),1)
					return
				if iCMD==-1:
					DebugLog("connection","err OnDataArrived%s PB-3"%os.getpid(),1)
					return
				self.OnPbPacketArrived(iHead,iCMD,body,bodyEX)
			except:
				debug.OutputError()
	
	def OnPbPacketArrived(self,iHead,iCMD,body,bodyEX):
		pass

class CPbConnection2(CConnection):
	def __init__(self,sHost,iPort,proxyObj):
		CConnection.__init__(self,sHost,iPort,proxyObj)

	def GetMaxPacketSize(self):
		return 1024*1024*50
	
	def OnDataArrived(self,sData):
# 		print "sData===1>",sData
# 		import binascii
# 		print "sData===2>",binascii.hexlify(sData)
		self.m_RecvBuff+=sData
		#while self.m_RecvBuff:
		try:
			iHead,bodyObj,iDataLen = PBUnPack2(self.m_RecvBuff)
			if iHead==-1:
				DebugLog("connection","err OnDataArrived2%s PB-2"%os.getpid(),1)
				return
			self.OnPbPacketArrived2(iHead,bodyObj)
			self.m_RecvBuff=self.m_RecvBuff[iDataLen:]
		except:
			debug.OutputError()
	
	def OnPbPacketArrived2(self,iHead,bodyObj):
		pass

class CDBClientConnection(CConnection):
	def __init__(self,sHost,iPort,proxyObj):
		CConnection.__init__(self,sHost,iPort,proxyObj)
		self.m_QueryFunc={}
		self.m_QueryID=0
		
	def NewQueryID(self):
		self.m_QueryID+=1
		return self.m_QueryID
	
	def GetQueryID(self):
		return self.m_QueryID
	
	def OnConnected(self):
		pass
		#print "connected",self.GetHost(),self.GetPort()
		#sText="1"*1000
		#
		#self.Update("table1",100,sText)
		#	
		#self.Insert("table1",0,"aa")
		#self.Delete("table1",101)
		#self.Disconnect()
	
	def Update(self,sTable,id,data):
		if type(id)!=str:
			self.UpdateI(sTable,id,data)
		else:
			self.UpdateS(sTable,id,data)
	
	def Insert(self,sTable,id,data):
		if type(id)!=str:
			self.InsertI(sTable,id,data)
		else:
			self.InsertS(sTable,id,data)
		
	def Query(self,sTable,id,func):
		if type(id)!=str:
			self.QueryI(sTable,id,func)
		else:
			self.QueryS(sTable,id,func)
		
	def Delete(self,sTable,id):
		if type(id)!=str:
			self.DeleteI(sTable,id)
		else:
			self.DeleteS(sTable,id)
		
	def UpdateI(self,sTable,id,data):
		Prepare()
		PackUShort(1)
		PackUInt(len(sTable))
		PackString(sTable,len(sTable))
		PackULong(id)
		PackString(data,len(data))
		self.SendData(GetPackData())
	
	def InsertI(self,sTable,id,data):
		Prepare()
		PackUShort(2)
		PackUInt(len(sTable))
		PackString(sTable,len(sTable))
		PackULong(id)
		PackString(data,len(data))
		self.SendData(GetPackData())
		
	def QueryI(self,sTable,id,func):
		Prepare()
		PackUShort(3)
		PackUInt(self.NewQueryID())
		PackUInt(len(sTable))
		PackString(sTable,len(sTable))
		PackULong(id)
		self.SendData(GetPackData())
		self.m_QueryFunc[self.GetQueryID()]=func
		
	def DeleteI(self,sTable,id):
		Prepare()
		PackUShort(4)
		PackUInt(len(sTable))
		PackString(sTable,len(sTable))
		PackULong(id)
		self.SendData(GetPackData())
	
	def UpdateS(self,sTable,sid,data):
		Prepare()
		PackUShort(11)
		PackUInt(len(sTable))
		PackString(sTable,len(sTable))
		PackInt(len(sid))
		PackString(sid,len(sid))
		PackString(data,len(data))
		self.SendData(GetPackData())
	
	def InsertS(self,sTable,sid,data):
		Prepare()
		PackUShort(12)
		PackUInt(len(sTable))
		PackString(sTable,len(sTable))
		PackInt(len(sid))
		PackString(sid,len(sid))
		PackString(data,len(data))
		self.SendData(GetPackData())
		
	def QueryS(self,sTable,sid,func):
		Prepare()
		PackUShort(13)
		PackUInt(self.NewQueryID())
		PackUInt(len(sTable))
		PackString(sTable,len(sTable))
		PackInt(len(sid))
		PackString(sid,len(sid))
		self.SendData(GetPackData())
		self.m_QueryFunc[self.GetQueryID()]=func
		
	def DeleteS(self,sTable,sid):
		Prepare()
		PackUShort(14)
		PackUInt(len(sTable))
		PackString(sTable,len(sTable))
		PackInt(len(sid))
		PackString(sid,len(sid))
		self.SendData(GetPackData())
		
	def Commit(self,func):
		Prepare()
		PackUShort(5)
		PackUInt(self.NewQueryID())
		self.SendData(GetPackData())
		self.m_QueryFunc[self.GetQueryID()]=func
		
	def Excute(self,sql,sKey,sData,func):
		Prepare()
		PackUShort(6)
		PackUInt(self.NewQueryID())
		PackUInt(len(sql))
		PackString(sql,len(sql))
		PackUInt(len(sKey))
		PackString(sKey,len(sKey))
		PackUInt(len(sData))
		PackString(sData,len(sData))
		self.SendData(GetPackData())
		self.m_QueryFunc[self.GetQueryID()]=func
		
	def OnDisconnected(self,sReason):
		#print "disconnected",self.GetHost(),self.GetPort(),sReason
		netlibproxy.Stop()
			
	def OnPacketArrived(self):
		iSub=UnpackUInt()
		iQuery=UnpackUInt()
		if iSub==1:
			if self.m_QueryFunc.get(iQuery):
				List=[]
				iCount=UnpackUInt()
				for i in xrange(iCount):
					iLen=UnpackUInt()
					data=UnpackString(iLen)
					List.append(data)

				func=self.m_QueryFunc[iQuery]
				del self.m_QueryFunc[iQuery],
				func(List)         ###########此处的fun则是发送数据时传进来的函数，一般是OnDataArrive（）
			else:
				print "query err",iQuery
		elif iSub==2:
			if self.m_QueryFunc.get(iQuery):
				func=self.m_QueryFunc[iQuery]
				del self.m_QueryFunc[iQuery]
				func()
			
	

class WebConnection(WebSocketServerProtocol):
	def Disconnect(self):
		return self.transport.loseConnection()	#主动断线,最终调用onClose
	
	def SendData(self,sData,isBinary=True):
		self.sendMessage(sData,isBinary)	#==self.transport.write(sData)
	#==========================================
	def onConnect(self, request):#==connectionMade
		print "Client connecting: {}".format(request.peer)
		try:
			self.OnConnected()
		except:
			debug.OutputError()

# 	# 建立websocket时调用的函数
# 	def onOpen(self):#先调用onConnect,后调用onOpen
# 		print "open"

	# websocket关闭时调用的函数，其中wasClean指示是否正常关闭，code指示关闭状态，reason指示原因
	def onClose(self, wasClean, code, reason):#==connectionLost
		DebugLog("websocket", "WebConnection:onClose wasClean=%s,code=%s,reason=%s"%(wasClean,code,reason),1)
		try:
			self.OnDisconnected(reason)
		except:
			debug.OutputError()

	# 收到消息后的处理函数，其中binary指示是字符串形式还是二进制
	def onMessage(self, msg, isBinary):#==dataReceived
		# iHead,iCMD,iBodyLen = unpack_from(">III", msg[:12], 0)
		# body = msg[12:]
		# print "msg length:",len(msg),iBodyLen
		# print "Icmd:",iCMD
		#print "msg",len(msg),msg
		try:
			self.OnDataArrived(msg)
		except:
			debug.OutputError()
	#==========================================
	def OnConnected(self):
		pass

	def OnDisconnected(self,sReason):
		pass
	
	def OnDataArrived(self,icmd,body):
		pass


__all__=["CConnection","CPbConnection"]