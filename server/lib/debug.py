# -*- coding: utf-8 -*-
def ExceptOutput(etype,value,tb):
	import sys,traceback,time

	sExcept="".join([
		time.strftime("[%Y-%m-%d %H:%M:%S]\n",time.localtime()),
		"".join(traceback.format_tb(tb)),
		"\n",
		"  {0}:{1}\n".format(etype,value),
	])
	sys.stderr.write(sExcept)

	global g_ErrorFile
	if g_ErrorFile:
		g_ErrorFile.write(sExcept)
		g_ErrorFile.flush()

	if "notify" in sys.modules and "netcmd" in sys.modules:
		import notify, netcmd
		pid = netcmd.GetLastPID()
		if pid > 0:
			notify.GS2CNotify(pid, "服务端报错,请联系相关服务端程序!")

def OutputError():
	import sys
	etype,value,tb=sys.exc_info()
	ExceptOutput(etype,value,tb)
	
def Traceback(bStdout=True):
	import sys,traceback,os 
	Lines=["==========Traceback=========={0}".format(os.linesep)]
	for sFile,iLine,sFunction,sCode in traceback.extract_stack()[:-2]:
		Lines.append("File:{0},Line:{1}\n".format(sFile,iLine))
	Lines.append("============================={0}".format(os.linesep))
	
	if bStdout:
		sys.stdout.writelines(Lines)
	
	global g_TracebackFile
	if g_TracebackFile:
		g_TracebackFile.writelines(Lines)
	
def Init(sErrorFileName="err.txt",sTbFileName="traceback.txt"):
	import sys,atexit
	
	reload(sys) 
	sys.setdefaultencoding('utf-8') #python 2.7 mimetypes 编码有bug
	
	global g_ErrorFile,g_TracebackFile
	g_ErrorFile=open(sErrorFileName,"a")
	atexit.register(g_ErrorFile.close)
	sys.excepthook=ExceptOutput
	g_TracebackFile=open(sTbFileName,"a")
	atexit.register(g_TracebackFile.close)
	try:
		from twisted.python import log
		log.discardLogs()
		log.err=log.deferr=lambda _stuff=None, _why=None, **kw:OutputError()
	except ImportError:
		pass
	except:
		OutputError()
    
try:
	g_ErrorFile
	g_TracebackFile
except NameError:
	g_ErrorFile=None
	g_TracebackFile=None
	
__all__=["Init","OutputError","Traceback"]