#!/usr/bin/env python3
# coding: utf-8
# Copyright 2016 Abram Hindle, https://github.com/tywtyw2002, and https://github.com/treedust
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Do not use urllib's HTTP GET and POST mechanisms.
# Write your own HTTP GET and POST
# The point is to understand what you have to send and get experience with it

import sys
import socket
import re
# you may use urllib to encode data appropriately
from urllib.parse import urlparse
from urllib.parse import urlencode

def help():
    print("httpclient.py [GET/POST] [URL]\n")

class HTTPResponse(object):
    def __init__(self, code=200, body=""):
        self.code = code
        self.body = body

class HTTPClient(object):
    #def get_host_port(self,url):

    def connect(self, host, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))
        return self.socket

    def get_code(self, data):
        #print("\r\nbegin")
        data_list = data.splitlines()
        status = data_list[0]
        code = status.split()[1]
        #print(code)
        #print("end\r\n")
        return int(code)

    def get_headers(self,data):
        #print("\r\nbegin")
        header = data.split("\r\n\r\n")[0]
        #print(header)
        #print("end\r\n")
        return header

    def get_body(self, data):
        #print("\r\nbegin")
        body = data.split("\r\n\r\n")[1]
        #print(data)
        #print(body)
        #print("end\r\n")
        
        return body
    
    def sendall(self, data):
        self.socket.sendall(data.encode('utf-8'))
        
    def close(self):
        self.socket.close()

    # read everything from the socket
    def recvall(self, sock):
        buffer = bytearray()
        done = False
        while not done:
            part = sock.recv(4096)
            if (part):
                buffer.extend(part)
            else:
                done = not part
        return buffer.decode('utf-8')
    
    def parse_url(self,url):
        o = urlparse(url)
        url_scheme = o.scheme
        url_path = o.path
        url_port = o.port
        url_hostname = o.hostname
        
        if not url_port: 
            if url_scheme !="https":
                url_port = 80
            else:
                url_port = 443

        if url_path == "":
            url_path = "/"

        return url_path,url_port,url_hostname


    def GET(self, url, args=None):
        code = 500
        body = ""
        path,port,hostname = self.parse_url(url)
        method_handle = "GET "+path+ " HTTP/1.1\r\n"
        host_handle = "Host: " + hostname+"\r\n"
        content_handle = "Content-Type: application/x-www-form-urlencoded\r\n"
        connect = "Connection: close\r\n\r\n"
        total_request = method_handle+ host_handle +content_handle+connect
        s = self.connect(hostname,port)
        self.sendall(total_request)
        response = self.recvall(s)
        self.close()
        code = self.get_code(response)
        #body_1 = self.get_headers(response)
        body_2 = "\r\n"+self.get_body(response)
        #body = body_1+body_2
        body = body_2



        return HTTPResponse(code, body)

    def POST(self, url, args=None):
        code = 500
        body = ""
        #print("\r\nbegin")
        path,port,hostname = self.parse_url(url)
        method_handle = "POST "+path+ " HTTP/1.1\r\n"
        host_handle = "Host: " + hostname+"\r\n"
        content_handle = "Content-Type: application/x-www-form-urlencoded\r\n"
        if args:
            args_str = urlencode(args)
            content_length = len(args_str)
        else:
            content_length = 0
            args_str = ""
        content_length_handle = "Content-Length: "+str(content_length)+"\r\n"
        connect = "Connection: close\r\n\r\n"
        total_request = method_handle+ host_handle +content_handle+content_length_handle+connect+args_str
        s = self.connect(hostname,port)
        self.sendall(total_request)
        response = self.recvall(s)
        self.close()
        code = self.get_code(response)
        body_1 = self.get_headers(response)
        body_2 = "\r\n"+self.get_body(response)
        body = body_2

        #print("end\r\n")

        return HTTPResponse(code, body)

    def command(self, url, command="GET", args=None):
        if (command == "POST"):
            return self.POST( url, args )
        else:
            return self.GET( url, args )
    
if __name__ == "__main__":
    client = HTTPClient()
    command = "GET"
    if (len(sys.argv) <= 1):
        help()
        sys.exit(1)
    elif (len(sys.argv) == 3):
        print(client.command( sys.argv[2], sys.argv[1] ))
    else:
        print(client.command( sys.argv[1] ))