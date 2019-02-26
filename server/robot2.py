# -*- coding: utf-8 -*-
import sys
sys.path.insert(0,"lib/")
import netlibproxy # 把script目录加进去之前要先import
sys.path.insert(0,"proto/")
sys.path.insert(0,"pbfile/")
sys.path.insert(0,"script/")
from libnet import *
from public import *
from pbpack2 import *
import connection
import os
from struct import *
import netlibproxy
from only import *
import libprint

import proto.common_pb2
import proto.csprotocol_pb2
import proto.ssprotocol_pb2
import proto.res_pb2

if os.environ.get("DOCKER"):	#docker部署
	SERVER_IP = os.environ.get("SERVER_IP","47.102.151.50")
	SERVER_PORT = int(os.environ.get("SERVER_PORT","3063"))
else:
	SERVER_IP = "47.102.151.50"	#内网IP
	SERVER_PORT = 3063

g_userid = "102"
connect = Random(10000000)
g_Print = False#True######

def randomString(n):
	return (''.join(map(lambda xx:(hex(ord(xx))[2:]),os.urandom(n))))[0:n]

class RobotConnection_C(connection.CPbConnection2):
	m_ConnectID = 0
	m_userid = ""
	m_player = None
	m_ServerId = 0

	def OnConnected(self):
		if g_Print:
			print "OnConnected"
		global connect 
		connect += 1
		self.m_ConnectID = connect
		self.m_userid = g_userid+str(self.m_ConnectID)	
		self.m_RecvBuff2 = ""
		self.ApplyHallServer()
		#self.PlayerLogin(self.m_userid)

	def OnDisconnected(self,sReason):
		if 1:
			print "OnDisconnected"
		if hasattr(self,"m_Timer") and self.m_Timer.active():
			self.m_Timer.cancel()

	def OnPbPacketArrived2(self,iHead,bodyObj):
		#print "OnPbPacketArrived2==>",iHead,bodyObj
		if iHead:
			if iHead==proto.csprotocol_pb2.RSP_APPLY_HALL_SERVER:
				self.m_ServerId = bodyObj.ApplyHallServer.ServerId
				self.PlayerLogin(self.m_userid)
				return
			if not self.m_player:
				if iHead == proto.csprotocol_pb2.RSP_LOGIN:
					player = OnGS2CLoginPlayer(self,self.m_ConnectID,self.m_userid,self.m_ServerId)
					self.m_player = player
					player.GetCMD(iHead,bodyObj)
			else:
				self.m_player.GetCMD(iHead,bodyObj)
	
	def ApplyHallServer(self):#请求密钥
		c2s = proto.csprotocol_pb2.CSReqBody()
		sData = PBPack2(proto.csprotocol_pb2.REQ_APPLY_HALL_SERVER,c2s,0)
		self.SendData(sData)
		
	def PlayerLogin(self,userid):
# 		Login:<DeviceId:"3F20A8C2B7C974D42E65E3537CA8AF8C" 
# 		OsVersion:"Windows 10  (10.0.0) 64bit" 
# 		DeviceType:"All Series (ASUS)" 
# 		NetType:NETTYPE_WIFI 
# 		LySdkDeviceId:"9a86c7469caaf883a71f6fdc1392825bc285aaa0" 
# 		ChannelId:"dangle" 
# 		ApkVersion:"0.1" 
# 		Resolution:"unknown" 
# 		ResourceVersion:"1.0" > 
		c2s = proto.csprotocol_pb2.CSReqBody()
# 		c2s.Login.PlatformType=proto.common_pb2.PLATFORMTYPE_ANDROID
		c2s.Login.DeviceId = str(userid)
		c2s.Login.DeviceType ="All Series (ASUS)"
		c2s.Login.OsVersion ="Windows 10  (10.0.0) 64bit"
		c2s.Login.NetType = proto.common_pb2.NETTYPE_WIFI
		c2s.Login.LySdkDeviceId = "9a86c7469caaf883a71f6fdc1392825bc285aaa0"
		c2s.Login.ChannelId ="dangle"
		c2s.Login.Resolution ="unknown"
		c2s.Login.ApkVersion = "0.1"
		c2s.Login.ResourceVersion = "1.0"
		if g_Print:
			print "PlayerLogin==>",c2s
		else:
			print "PlayerLogin==>",userid
		sData = PBPack2(proto.csprotocol_pb2.REQ_LOGIN,c2s,self.m_ServerId)
		self.SendData(sData)

class OnGS2CLoginPlayer(object):
	def __init__(self,connect,ConnID,userid,serverId):
		self.m_Connect = connect
		self.m_ConnID = ConnID
		self.m_ID = ConnID
		self.userid = userid
		self.data = {}
		self.equipList = []
		self.m_Resprond = 0
		self.m_ItemData={}
		
		self.m_ServerId=serverId
		
		self.m_Server_Id = ""
		self.m_Server_SessionId = ""
		
		self.m_timeoutID =0

	def C2SCreatePlayer(self,bodyObj):
		if g_Print:
			print "C2SCreatePlayer创建成功==>",bodyObj
		else:
			print "C2SCreatePlayer创建成功==>",bodyObj.Login.Id
		#Log("robot2","C2SCreatePlayer创建成功:%s"%bodyObj)
		if bodyObj.ErrMsg:
			print "C2SCreatePlayer创建失败==>",bodyObj
			#Log("robot2","C2SCreatePlayer创建失败:%s"%bodyObj)
			return
		self.m_Server_Id = bodyObj.Login.Id
		self.m_Server_SessionId = bodyObj.Login.SessionId
		for items in bodyObj.Login.Items:
			self.m_ItemData[items.Id]=items.Count
		#print self.m_ItemData
		DelTimer("UpPower%s"%self.m_ID)
		SetTimer(RandInt(1,3),Functor(self.UpPower,5) ,"UpPower%s"%self.m_ID)
		
	def UpPower(self,iTime):#强化自己
		if iTime==5:#发邮件
			c2s = proto.csprotocol_pb2.CSReqBody()
			c2s.WorldChat.Content="/sendmail 测试 我是%s-%s-%s"%(self.m_ID,self.userid,self.m_Server_Id)
			sData = PBPack2(proto.csprotocol_pb2.REQ_WORLD_CHAT,c2s,self.m_ServerId)
			self.SendData2Server(sData)
		elif iTime==4:#设置名字
			c2s = proto.csprotocol_pb2.CSReqBody()
			c2s.UserNameSet.UserName="我是%s"%(randomString(6))
			sData = PBPack2(proto.csprotocol_pb2.REQ_USERNAME_SET,c2s,self.m_ServerId)
			self.SendData2Server(sData)
		elif iTime==3:#加MMR
			c2s = proto.csprotocol_pb2.CSReqBody()
			c2s.WorldChat.Content="/addmmr %s"%Random(4000)
			if g_Print:
				print c2s
			sData = PBPack2(proto.csprotocol_pb2.REQ_WORLD_CHAT,c2s,self.m_ServerId)
			self.SendData2Server(sData)
		elif iTime==2:#加糖果
			c2s = proto.csprotocol_pb2.CSReqBody()
			c2s.WorldChat.Content="/addobject 1 1 %s"%Random(5000)
			sData = PBPack2(proto.csprotocol_pb2.REQ_WORLD_CHAT,c2s,self.m_ServerId)
			self.SendData2Server(sData)
		elif iTime==1:#加其他道具
			c2s = proto.csprotocol_pb2.CSReqBody()
			iType=Random(3)+2
			if iType == proto.common_pb2.CHESS_PLAYER:
				c2s.WorldChat.Content="/addobject 2 %s 1"%(Random(3)+2001)
			elif iType == proto.common_pb2.SCENE:
				c2s.WorldChat.Content="/addobject 3 %s 1"%(Random(2)+3001)
			elif iType == proto.common_pb2.HEAD_PIC:
				c2s.WorldChat.Content="/addobject 4 %s 1"%(Random(5)+4001)
			if g_Print: 
				print c2s
			sData = PBPack2(proto.csprotocol_pb2.REQ_WORLD_CHAT,c2s,self.m_ServerId)
			self.SendData2Server(sData)
		
		iTime-=1
		if iTime>0:
			DelTimer("UpPower%s"%self.m_ID)
			SetTimer(RandInt(1,3),Functor(self.UpPower,iTime) ,"UpPower%s"%self.m_ID)
		else:
			DelTimer("C2GSAnyOperation%s"%self.m_ID)
			SetTimer(RandInt(5,14),self.C2GSAnyOperation ,"C2GSAnyOperation%s"%self.m_ID)
		
	def C2GSAnyOperation(self):
		DelTimer("C2GSAnyOperation%s"%self.m_ID)
		cmdData = {	
				"什么也不做"			:	6000,
				"GM指令"				:	100,
				"玩家基础信息"		:	500,
				"玩家详细信息"		:	100,
				"世界聊天"			:	50,
				"获取排行榜数据"		:	500,
				"领取邮件奖励"		:	300,
				"购买扭蛋"			:	500,
				"随机用户名"			:	100,
				"设置头像"			:	100,
# 				"pvp请求"			:	1,
# 				"取消匹配"			:	1,
				"装备棋手"			:	100,
				"装备场景"			:	100,
				}
		cmd = ChooseKey(cmdData)
		if g_Print:
			print "玩家%s=============================================================%s==>%s"%(self.m_ID,self.m_Server_Id,cmd)
		#Log("robot2","玩家%s====%s==>%s"%(self.m_ID,self.m_Server_Id,cmd))
		if cmd == "什么也不做":
			if g_Print:
				ts("C2SHeart%s"%self.m_timeoutID,0.001)
			c2s = proto.csprotocol_pb2.CSReqBody()
			c2s.Heart.time = 1
			sData = PBPack2(proto.csprotocol_pb2.REQ_HEART,c2s,self.m_ServerId)
			self.SendData2Server(sData)
		elif cmd == "GM指令":
			c2s = proto.csprotocol_pb2.CSReqBody()
			iType=Random(4)+1
			if iType == proto.common_pb2.CANDY:
				c2s.WorldChat.Content="/addobject 1 1 %s"%Random(200)
			elif iType == proto.common_pb2.CHESS_PLAYER:
				c2s.WorldChat.Content="/addobject 2 %s 1"%(Random(3)+2001)
			elif iType == proto.common_pb2.SCENE:
				c2s.WorldChat.Content="/addobject 3 %s 1"%(Random(2)+3001)
			elif iType == proto.common_pb2.HEAD_PIC:
				c2s.WorldChat.Content="/addobject 4 %s 1"%(Random(5)+4001)
			if g_Print: 
				print c2s
			sData = PBPack2(proto.csprotocol_pb2.REQ_WORLD_CHAT,c2s,self.m_ServerId)
			self.SendData2Server(sData)
		elif cmd == "玩家基础信息":
			c2s = proto.csprotocol_pb2.CSReqBody()
			#c2s.Login.DeviceId = str(self.userid)
			for i in ["XWF1","KWFK"]:
				c2s.PlayersBaseInfo.Ids.append(i)
			sData = PBPack2(proto.csprotocol_pb2.REQ_PLAYERS_BASE_INFO,c2s,self.m_ServerId)
			self.SendData2Server(sData)
		elif cmd == "玩家详细信息":
			c2s = proto.csprotocol_pb2.CSReqBody()
			c2s.PlayerDetailInfo.IdUsrName="ZHGZX"
			sData = PBPack2(proto.csprotocol_pb2.REQ_PLAYER_DETAIL_INFO,c2s,self.m_ServerId)
			self.SendData2Server(sData)
		elif cmd == "世界聊天":
			c2s = proto.csprotocol_pb2.CSReqBody()
			c2s.WorldChat.Content="我是%s-%s-%s"%(self.m_ID,self.userid,self.m_Server_Id)
# 			c2s.WorldChat.Content="百度v不好看就会受到和v可接受的和v看,NCVKJDSFKVCSCVHWEDFFB你的歌广泛豆腐干的官方公布 回国后核事故发生后的方式方法就让他有机会然后回来好几天了也就是风格还是让他好好大会高峰论坛后来他皇上的话会不会给皇上的哈尔德Thad刚发的很方便的v根本听不懂吧大锅饭大锅饭的发表v打副本大二的特别提到后来就没倒还不如回家南斯拉夫Bret会不会是地方干部了嘎尔个人"
# 			c2s = proto.csprotocol_pb2.CSRspBody()
# 			for i in xrange(200):
# 				#DTItem = proto.common_pb2.CSDTItemList()
# 				Items2=c2s.Login.Items[i].Items.add()
# 				Items2.Id=1
# 				Items2.Count=1
# 				Items2.InstanceId=1
# 				#c2s.Login.Items[i].foo=Items2
			sData = PBPack2(proto.csprotocol_pb2.REQ_WORLD_CHAT,c2s,self.m_ServerId)
			self.SendData2Server(sData)
		elif cmd == "获取排行榜数据":
			c2s = proto.csprotocol_pb2.CSReqBody()
			c2s.GetNumRank.Type= RandInt(proto.common_pb2.RANKTYPE_MVP,proto.common_pb2.RANKTYPE_MAX-1)
			sData = PBPack2(proto.csprotocol_pb2.REQ_GET_NUM_RANK,c2s,self.m_ServerId)
			self.SendData2Server(sData)
		elif cmd == "领取邮件奖励":
			c2s = proto.csprotocol_pb2.CSReqBody()
			c2s.GetMailAward.Id=0
			sData = PBPack2(proto.csprotocol_pb2.REQ_GET_MAIL_AWARD,c2s,self.m_ServerId)
			self.SendData2Server(sData)
		elif cmd == "购买扭蛋":
			c2s = proto.csprotocol_pb2.CSReqBody()
			c2s.BuyEgg.Count=3
			sData = PBPack2(proto.csprotocol_pb2.REQ_BUY_EGG,c2s,self.m_ServerId)
			self.SendData2Server(sData)
		elif cmd == "随机用户名":
			c2s = proto.csprotocol_pb2.CSReqBody()
			c2s.UserNameRandom.UserName="我是%s"%(randomString(8))
			sData = PBPack2(proto.csprotocol_pb2.REQ_USERNAME_RANDOM,c2s,self.m_ServerId)
			self.SendData2Server(sData)
		elif cmd == "设置头像":
			c2s = proto.csprotocol_pb2.CSReqBody()
			self.m_ItemData
			c2s.HeadPicSet.HeadPic = (Random(5)+4001)
			sData = PBPack2(proto.csprotocol_pb2.REQ_HEADPIC_SET,c2s,self.m_ServerId)
			self.SendData2Server(sData)
		elif cmd == "pvp请求":
			c2s = proto.csprotocol_pb2.CSReqBody()
			c2s.Pvp.Mode = proto.common_pb2.AUTO_CHESS
			sData = PBPack2(proto.csprotocol_pb2.REQ_PVP,c2s,self.m_ServerId)
			self.SendData2Server(sData)
		elif cmd == "取消匹配":
			c2s = proto.csprotocol_pb2.CSReqBody()
			sData = PBPack2(proto.csprotocol_pb2.REQ_PVP_MATCH_CANCEL,c2s,self.m_ServerId)
			self.SendData2Server(sData)
		elif cmd == "装备棋手":
			c2s = proto.csprotocol_pb2.CSReqBody()
			c2s.DressChessPlayer.Id = Random(3)+2001
			sData = PBPack2(proto.csprotocol_pb2.REQ_DRESS_CHESS_PLAYER,c2s,self.m_ServerId)
			self.SendData2Server(sData)
		elif cmd == "装备场景":
			c2s = proto.csprotocol_pb2.CSReqBody()
			c2s.DressScene.Id = Random(2)+3001
			sData = PBPack2(proto.csprotocol_pb2.REQ_DRESS_SCENE,c2s,self.m_ServerId)
			self.SendData2Server(sData)

		SetTimer(RandInt(5,14)+RandInt(1,100)*0.01,self.C2GSAnyOperation ,"C2GSAnyOperation%s"%self.m_ID)
	
	def C2SHeart(self,bodyObj):
		if g_Print: 
			ts("C2SHeart%s"%self.m_timeoutID,0.001)
			self.m_timeoutID+=1
			print "C2SHeart心跳包===>",bodyObj
	
	def RSP_PlayersBaseInfo(self,bodyObj):
		if g_Print: 
			print "RSP_PlayersBaseInfo玩家基础信息===>",bodyObj
	
	def RSP_PlayersDetailInfo(self,bodyObj):
		if g_Print:
			print "RSP_PlayersDetailInfo玩家详细信息===>",bodyObj
	
	def RSP_WorldChat(self,bodyObj):
		if g_Print:
			print "RSP_WorldChat世界聊天===>",bodyObj
	
	def NTF_WorldChat(self,bodyObj):
		if g_Print:
			print "NTF_WorldChat世界聊天===>",bodyObj.WorldChat.WorldChat.BaseInfo.Id,"==说==>",bodyObj.WorldChat.WorldChat.Content
	
	def RSP_GetNumRank(self,bodyObj):
		if g_Print:
			print "RSP_GetNumRank获取排行榜数据===>",bodyObj
	
	def NTF_Mail(self,bodyObj):
		if g_Print:
			print "NTF_Mail邮件===>",bodyObj
	
	def RSP_GetMailAward(self,bodyObj):
		if g_Print:
			print "RSP_GetMailAward领取邮件奖励===>",bodyObj
	
	def RSP_BuyEgg(self,bodyObj):
		if g_Print:
			print "RSP_BuyEgg购买扭蛋===>",bodyObj
	
	def RSP_UserNameSet(self,bodyObj):
		if g_Print:
			print "RSP_UserNameSet设置用户名===>",bodyObj
	
	def RSP_UserNameRandom(self,bodyObj):
		if g_Print:
			print "RSP_UserNameRandom随机用户名===>",bodyObj.UserNameRandom.UserName
	
	def RSP_HeadPicSet(self,bodyObj):
		if g_Print:
			print "RSP_HeadPicSet设置头像===>",bodyObj
	
	def NTF_HeadPicSet(self,bodyObj):
		if g_Print:
			print "NTF_HeadPicSet头像变更通告===>",bodyObj
	
	def RSP_PvpMatch(self,bodyObj):
		if g_Print:
			print "RSP_PvpMatch匹配pvp===>",bodyObj
	def RSP_PvpMatchCancel(self,bodyObj):
		if g_Print:
			print "RSP_PvpMatchCancel匹配取消===>",bodyObj
	def NTF_PvpMatch(self,bodyObj):
		if g_Print:
			print "NTF_PvpMatch===>",bodyObj
	def NTF_PvpMatchCancel(self,bodyObj):
		if g_Print:
			print "NTF_PvpMatchCancel===>",bodyObj
	def NTF_Pvp(self,bodyObj):
		if g_Print:
			print "NTF_Pvp===>",bodyObj
	def NTF_PvpStatus(self,bodyObj):
		if g_Print:
			print "NTF_PvpStatus===>",bodyObj
	
	def RSP_DressChessPlayer(self,bodyObj):
		if g_Print:
			print "RSP_DressChessPlayer===>",bodyObj
	def RSP_DressScene(self,bodyObj):
		if g_Print:
			print "RSP_DressScene===>",bodyObj
	
	
	g_Func = {
		#============================RSP==========================
		proto.csprotocol_pb2.RSP_LOGIN					:	C2SCreatePlayer,
		proto.csprotocol_pb2.RSP_HEART					:	C2SHeart,
		proto.csprotocol_pb2.RSP_PLAYERS_BASE_INFO		:	RSP_PlayersBaseInfo,
		proto.csprotocol_pb2.RSP_PLAYER_DETAIL_INFO		:	RSP_PlayersDetailInfo,
		proto.csprotocol_pb2.RSP_WORLD_CHAT				:	RSP_WorldChat,
		proto.csprotocol_pb2.RSP_GET_NUM_RANK			:	RSP_GetNumRank,
		proto.csprotocol_pb2.RSP_GET_MAIL_AWARD			:	RSP_GetMailAward,
		proto.csprotocol_pb2.RSP_BUY_EGG				:	RSP_BuyEgg,
		proto.csprotocol_pb2.RSP_USERNAME_SET			:	RSP_UserNameSet,
		proto.csprotocol_pb2.RSP_USERNAME_RANDOM		:	RSP_UserNameRandom,
		proto.csprotocol_pb2.RSP_HEADPIC_SET			:	RSP_HeadPicSet,
		proto.csprotocol_pb2.RSP_PVP					:	RSP_PvpMatch,
		proto.csprotocol_pb2.RSP_PVP_MATCH_CANCEL		:	RSP_PvpMatchCancel,
		proto.csprotocol_pb2.RSP_DRESS_CHESS_PLAYER		:	RSP_DressChessPlayer,
		proto.csprotocol_pb2.RSP_DRESS_SCENE			:	RSP_DressScene,
		#============================NTF==========================
		proto.csprotocol_pb2.NTF_WORLD_CHAT				:	NTF_WorldChat,
		proto.csprotocol_pb2.NTF_MAILS					:	NTF_Mail,
		proto.csprotocol_pb2.NTF_HEAD_PIC				:	NTF_HeadPicSet,
		proto.csprotocol_pb2.NTF_PVP_MATCH				:	NTF_PvpMatch,
		proto.csprotocol_pb2.NTF_PVP_MATCH_CANCEL		:	NTF_PvpMatchCancel,
		proto.csprotocol_pb2.NTF_PVP					:	NTF_Pvp,
		proto.csprotocol_pb2.NTF_PVP_STATUS				:	NTF_PvpStatus,
		}

	def GetCMD(self,icmd,bodyObj):
		#print "Func====icmd",icmd
		if self.g_Func.has_key(icmd):
			self.g_Func[icmd](self,bodyObj)
		else:
			if g_Print:
				print "NoFunc====icmd=>",icmd,bodyObj
	
	def SendData2Server(self,sData):
		self.m_Connect.SendData(sData)

if __name__=="__main__":
	import sys
	count = 1
	print sys.argv
	if len(sys.argv)>=2:
		count=int(sys.argv[1])
	for i in xrange(count):
		netlibproxy.ConnectTCP(SERVER_IP,SERVER_PORT,RobotConnection_C)#139.224.10.0#172.16.0.93#2+Random(2)
	netlibproxy.Start()
		
