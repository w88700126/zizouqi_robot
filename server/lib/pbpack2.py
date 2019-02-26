# -*- coding: utf-8 -*-
from struct import *
import zlib
from Crypto.Cipher import AES
import proto.csprotocol_pb2

HEAH_LENGTH =1

class CPBPackObject2:
	
	def __init__(self,iBuffSize=1024*8):
		self.m_Buff=bytearray(iBuffSize)
		self.m_Key="DanJuanGame@2016"[:AES.block_size]
		self.m_EncryptObj=AES.new(self.m_Key,AES.MODE_CBC,self.m_Key)
	
	def Pad(self,s):
		padding = AES.block_size - len(s) % AES.block_size
		return s + padding * chr(padding)
	
	def Unpad(self,s):
		return s[0:-ord(s[-1])]
	
	def PBPack2(self,iHead,pbObj,iServerId):
		#进行编码
		body = pbObj.SerializeToString()
# 		import binascii
# 		print "body=1===>",len(body),"==>",binascii.hexlify(body)
# 		#压缩
# 		body = zlib.compress(body)#, zlib.Z_BEST_COMPRESSION
# 		print "body=2===>",len(body),"==>",binascii.hexlify(body)
# 		#加密
# 		cryptor=AES.new(self.m_Key,AES.MODE_CBC,self.m_Key)#每次都要用新的
# 		body = cryptor.encrypt(self.Pad(body))
# 		print "body=3===>",len(body),"==>",binascii.hexlify(body)
# 		#解密测试
# 		body2 = self.Unpad(self.m_EncryptObj.decrypt(body))
# 		print "body=4===>",len(body2),"==>",binascii.hexlify(body2)
		iBodyLen = len(body)
		
		headObj = proto.csprotocol_pb2.CSHead()
		headObj.MsgId = iHead
		headObj.BodyLen = iBodyLen
		headObj.ServerId = iServerId
# 		headObj.Compress = True		#压缩
		head = headObj.SerializeToString()
		iHeadLen = len(head)
		#print "head=====>",iHeadLen,"==>",binascii.hexlify(head)
		
		pack_into("!B",self.m_Buff,0,iHeadLen)
		pack_into("!{0}s".format(iHeadLen),self.m_Buff,HEAH_LENGTH,head)
		pack_into("!{0}s".format(iBodyLen),self.m_Buff,HEAH_LENGTH+iHeadLen,body)
		#print "self.m_Buff==>",iHeadLen,iBodyLen
		#print binascii.hexlify(self.m_Buff[:(1+iHeadLen+iBodyLen)])
		return str(self.m_Buff[:(1+iHeadLen+iBodyLen)])
	
	def PBUnPack2(self,sData):
		iHeadLen = unpack_from("!B", sData[:HEAH_LENGTH], 0)[0]  #head
# 		print "PBUnPack2==>iHeadLen==>",iHeadLen
		head=sData[HEAH_LENGTH:iHeadLen+HEAH_LENGTH]
		if len(head)!=iHeadLen:
			return -1,None,0
		headObj = proto.csprotocol_pb2.CSHead()
		headObj.ParseFromString(head)
# 		print "PBUnPack2*******>headObj****************************>",iHeadLen
# 		print headObj
		iHead = headObj.MsgId
		iBodyLen = headObj.BodyLen
		body=sData[iHeadLen+HEAH_LENGTH:iHeadLen+HEAH_LENGTH+iBodyLen]
# 		import binascii
# 		print "PBUnPack2=body==1=>",len(body),"==>",binascii.hexlify(body)
# 		if len(body):
# 			#解密
# 			cryptor=AES.new(self.m_Key,AES.MODE_CBC,self.m_Key)#每次都要用新的
# 			body = cryptor.decrypt(body)#self.m_EncryptObj.decrypt(body)
# # 			print "PBUnPack2=body==2=>",len(body),"==>",binascii.hexlify(body)
# 			body = self.Unpad(body)
# 			print "PBUnPack2=body==3=>",len(body),"==>",binascii.hexlify(body)

		if len(head)!=iHeadLen:
			return -1,None,0
		if iHead<1000:
			bodyObj = proto.csprotocol_pb2.CSReqBody()
		elif iHead<2000:
			bodyObj = proto.csprotocol_pb2.CSRspBody()
		elif iHead<3000:
			bodyObj = proto.csprotocol_pb2.CSNtfBody()
		bodyObj.ParseFromString(body)
# 		print "PBUnPack2*******>bodyObj*******>",iBodyLen
# 		print bodyObj
		return iHead,bodyObj,(iHeadLen+HEAH_LENGTH+iBodyLen)
	
def PBPack2(iHead,pbObj,iServerId):
	global g_PBPackObj2
	return g_PBPackObj2.PBPack2(iHead,pbObj,iServerId)

def CheckPBUnpack2(sData,iMaxSize=256):
	global g_PBUnpackObj2
	return g_PBUnpackObj2.CheckPBUnpack2(sData,iMaxSize)

def PBUnPack2(sData):
	global g_PBUnpackObj2
	return g_PBUnpackObj2.PBUnPack2(sData)

try:
	g_PBPackObj2
	g_PBUnpackObj2
except NameError:
	g_PBPackObj2=CPBPackObject2()
	g_PBUnpackObj2=CPBPackObject2()
if __name__=="__main__":
	print len("8299d5c8cacc3c86c6a2e9d410c96c89c809d802052114684f9f5c5108b35377")
	
