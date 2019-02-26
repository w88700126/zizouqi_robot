#!/usr/bin/python
# -*- coding:utf-8 -*-
import os
root = os.path.split(os.path.realpath(__file__))[0]
root = os.path.dirname(root)
if not os.path.exists('%s/proto' %root):
  os.makedirs('%s/proto' %root)
os.system('protoc --cpp_out=%s/proto -I=%s/pbfile %s/pbfile/*.proto' %(root, root, root))
os.system('protoc --python_out=%s/python/comm/proto -I=%s/pbfile %s/pbfile/*.proto' %(root, root, root))
protocmakefile = root + '/proto/CMakeLists.txt'
root = root + '/proto'
f = open(protocmakefile, "w")
f.write("""
project(proto)

ADD_LIBRARY(proto STATIC 
""")



for i in os.listdir(root):
  if os.path.isfile(os.path.join(root, i)):
    n = os.path.splitext(i)  
    if n[1] == ".cc":  
      f.write(i + "\n");
f.write("""
)""")
f.close()

parser_h = os.path.join(root, "..", "net", "CParser.h")
proto_path = os.path.join( root, "..", "proto" )

f = open(parser_h, "w")

f.write("""
#pragma once
#include "NetDefine.h"
#include <AntNet/All.h>
#include <google/protobuf/message.h>
""")

headers = []
for i in os.listdir(proto_path):
    if os.path.isfile(os.path.join(root, i)) and i.find(".pb.h") >= 0:
        headers.append( '#include "%s"\n' % i )

f.write( "".join(headers) )
f.write("""
using namespace google::protobuf;

struct CParser
{
    public:
        CParser(){}
        virtual ~CParser(){}
                
    public:
};
""")


