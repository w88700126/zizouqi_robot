# -*- coding: utf-8 -*-
import sys,os
if "twisted.internet.reactor" not in sys.modules:
	try:
		from twisted.internet import epollreactor
		epollreactor.install()
	except:
		print "init epoll failed"
from twisted.internet.protocol import Protocol,ServerFactory,ReconnectingClientFactory
from twisted.internet import reactor
from twisted.python import log
from public import *
g_TimeFlagTable={}

class CMyProtocol(Protocol):
	
	def SetFactory(self,factoryObj):
		self.m_Factory=factoryObj
	
	def SetConnection(self,connObj):
		self.m_ConnObj=connObj
	
	def Disconnect(self):
		return self.transport.loseConnection()
		
	def SendData(self,sData):
		return self.transport.write(sData)
	
	def SendDataAll(self,sData):
		return self.transport.getHandle().sendall(sData)
	
	def connectionMade(self):
		try:
# 			self.transport.setTcpNoDelay(True)
			self.m_ConnObj.OnConnected()
		except:
			debug.OutputError()
		
	def connectionLost(self,reason):
		try:
			self.m_ConnObj.OnDisconnected(reason.getErrorMessage())
		except:
			debug.OutputError()
		del self.m_ConnObj
		del self.m_Factory
		
	def dataReceived(self,sData):
		try:
			self.m_ConnObj.OnDataArrived(sData)
		except:
			debug.OutputError()
		
class CMyClientProtocol(CMyProtocol):
	
	def connectionLost(self,reason):
		self.m_Factory.stopTrying()
		CMyProtocol.connectionLost(self,reason)
		
class CMyServerFactory(ServerFactory):
	
	def buildProtocol(self,address):
		p=CMyProtocol()
		p.SetFactory(self)
		p.SetConnection(self.connClass(address.host,address.port,p))
		return p
		
class CMyClientFactory(ReconnectingClientFactory):
	factor=1#重连时间系数
	jitter=0
	noisy=False
	def buildProtocol(self,address):
		p=CMyClientProtocol()
		p.SetFactory(self)
		p.SetConnection(self.connClass(address.host,address.port,p))
		return p
		
def Start():
	if reactor.running:
		return
	import servercnf
# 	if os.name != "nt":
# 		log.startLogging(file("../twisted_%s.txt"%servercnf.ServerCnf["servertype"],"a+"))
	reactor.run()
	
def Stop():
	if not reactor.running:
		return
	reactor.stop()
	
	
def HttpGetPage(url,*args,**kwargs):
	from twisted.web import client
#	@type deferred: Deferred
#    @ivar deferred: A Deferred that will fire when the content has
#          been retrieved. Once this is fired, the ivars `status', `version',
#          and `message' will be set.
#
#    @type status: bytes
#    @ivar status: The status of the response.
#
#    @type version: bytes
#    @ivar version: The version of the response.
#
#    @type message: bytes
#    @ivar message: The text message returned with the status.
#
#    @type response_headers: dict
#    @ivar response_headers: The headers that were specified in the
#          response from the server.
#
#    @type method: bytes
#    @ivar method: The HTTP method to use in the request.  This should be one of
#        OPTIONS, GET, HEAD, POST, PUT, DELETE, TRACE, or CONNECT (case
#        matters).  Other values may be specified if the server being contacted
#        supports them.
#
#    @type redirectLimit: int
#    @ivar redirectLimit: The maximum number of HTTP redirects that can occur
#          before it is assumed that the redirection is endless.
#
#    @type afterFoundGet: C{bool}
#    @ivar afterFoundGet: Deviate from the HTTP 1.1 RFC by handling redirects
#        the same way as most web browsers; if the request method is POST and a
#        302 status is encountered, the redirect is followed with a GET method
#
#    @type _redirectCount: int
#    @ivar _redirectCount: The current number of HTTP redirects encountered.
#
#    @ivar _disconnectedDeferred: A L{Deferred} which only fires after the last
#        connection associated with the request (redirects may cause multiple
#        connections to be required) has closed.  The result Deferred will only
#        fire after this Deferred, so that callers can be assured that there are
#        no more event sources in the reactor once they get the result.

	return client.getPage(url,*args,**kwargs)


def CallLater(fDelay,callObj,sFlag=""):
	import time,public,random
# 	if sFlag=="warturn":
# 		maxcount=250
# 		delayrange=3
# 		iTime=int(time.time()+fDelay)
# 		if not g_TimeFlagTable.get(iTime):
# 			g_TimeFlagTable[iTime]=0
# 		if g_TimeFlagTable[iTime]>maxcount:
# 			#public.Log("calllater","full %s %s"%(iTime,g_TimeFlagTable[iTime]))
# 			add=0
# 			for i in range(delayrange):
# 				if g_TimeFlagTable.get(iTime+i)<maxcount:
# 					add=i
# 			if not add:
# 				add=public.Random(delayrange)
# 			iTime+=add
# 			fDelay+=add+random.random()
# 			#return CallLater(fDelay+1,callObj,sFlag)
# 		
# 		List=g_TimeFlagTable.keys()
# 		List.sort()
# 		for i in List:
# 			if i<int(time.time()):
# 				del g_TimeFlagTable[i]
# 		g_TimeFlagTable[iTime]+=1
			
	return reactor.callLater(fDelay,callObj)
	
def ListenTCP(iPort,iBacklog,connClass):
	f=CMyServerFactory()
	f.connClass=connClass
	reactor.listenTCP(iPort,f,iBacklog)
	
def ConnectTCP(sHost,iPort,connClass):
	f=CMyClientFactory()
	f.connClass=connClass
	reactor.connectTCP(sHost,iPort,f)
	
__all__=["Start","Stop","CallLater","ListenTCP","ConnectTCP"]