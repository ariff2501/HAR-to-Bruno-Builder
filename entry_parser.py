from urllib.parse import unquote
import xml.etree.ElementTree as ET
import re

class Log : 
     def __init__(self,json_data):
        data = json_data.get('log', {}) 
        self.version = data.get('version', 'Unknown')
        self.creator = data.get('creator',{})
        self.pages = data.get('pages',[])
        self.entries = [Entry(entry_data) for entry_data in data.get('entries',[])]
     
     def getEntriesLength(self):
          return len(self.entries)
     
     def logAnalyzer(self):
          analysis = {}
          # how much entries:
          analysis['Entries'] =  self.getEntriesLength()
          # how much xml
          analysis['XML'] = 0
          
          for entry in self.entries:
               if entry.request.isXML():
                    analysis['XML'] += 1
          analysis['nonXML'] = analysis['Entries'] - analysis['XML']
          # how much request with no postData
          # analysis['nbRequestWpostData'] = 0
          analysis['Technical Request'] = 0
          analysis['TOM Request'] = 0
          for entry in self.entries : 
               if entry.request.isXML():
                    if entry.request.hasPostData():
                         if entry.request.hasPostBody():
                              analysis['TOM Request'] += 1
                         # analysis['nbRequestWpostData'] += 1
                         else :
                              analysis['Technical Request'] += 1 
                    else : 
                         analysis['Technical Request'] += 1 
          # how much request with params
          # analysis['nbRequestWparams'] = 0
          # for entry in self.entries : 
          #      if entry.request.hasParams():
          #           analysis['nbRequestWparams'] += 1

          # how much request with no body
          
          # for entry in self.entries : 
          #      if entry.request.hasPostData() :
          #           if entry.request.postData.hasPostBody() :
          #                analysis['nbRequestWpostDataWparamsWpostBody'] += 1

          return analysis
     
     def displayAnalysis(self):
          analysis = self.logAnalyzer()
          for key, value in analysis.items():
               print(f"{key}: {value}")


class Entry : 
     def __init__(self,data):
        self._connectionId = data.get('_connectionId','')
     #    self._initiator = data.get('_initiator',[])
        self.request = Request(data.get('request',{}))
        self.response =Response(data.get('response',{}))
     
     def to_dict(self):
        return {
            '_connectionId': self._connectionId,
          #   '_initiator': self._initiator,
            'request': self.request.to_dict() if hasattr(self.request, 'to_dict') else self.request,
          #   'response': self.response
        }
    
     def get_bruno_data(self):
          if self.request.isXML() :
               return{
                    "type": "http",
                    "name": "",
                    "filename": "",
                    "seq":0,
                    "request": self.request.setTests(self.request.get_bruno_data(),self.prepareTests()) if hasattr(self.request, 'get_bruno_data') else self.request,
                    "metadata" : {
                         "postData" : self.request.hasPostData(),
                         "postBody" : self.request.hasPostBody(),
                         "params" : self.request.hasParams()
                    }
               }
          else :
               return None
     
     def getTests(self): # return a string containing test code
          tests = self.response.get_bruno_response()
          testText = ""
          for key in tests :
               testText += f"//{key} : {tests[key]}\n"
          return testText
     
     def prepareTests(self):
          status = self.response.status
          txt = (f"test(\"Response Status should be {status}\", function () {{\n" 
                 f" expect(res.getStatus()).to.equal({status});\n}});\n")
          headertest = ""
          resbody =""
          for key in self.response.get_bruno_response() :
               if self.is_valid_xml(self.response.get_bruno_response()[key]) :

                    # get xml declaration / response header
                    xml_decl_pattern = r'^<\?xml[^>]+\?>'
                    match = re.search(xml_decl_pattern, self.response.get_bruno_response()[key].strip())
                    header = f"{match[0]}" if match else ""
                    header = header.replace('"', r'\"')
                    header = f"\"{header}\""
                    headertest = (f"test(\"Header response should be correct\", function() {{\n"  
                    f"expect(res.body).contains({header});\n}});\n\n")   
                    #get response body
                    rest_xml_code = re.sub(xml_decl_pattern, '', self.response.get_bruno_response()[key], count=1).strip()
                    rest_xml_code =rest_xml_code.replace('"', r'\"')
                    rest_xml_code = f"\"{rest_xml_code}\""
                    resbody= (f"test(\"Response body should be correct\", function() {{\n " 
                              f"expect(res.body).contains({rest_xml_code});\n}});")
                    resbody = f"/* {resbody} */"

          txt =  txt + "\n\n" + headertest + "\n\n" + resbody

          return txt
     
     def is_valid_xml(self,input_string):
          if(type(input_string) is str) :
               try:
                    root = ET.fromstring(input_string)
                    return True
               except ET.ParseError:
                    return False
          else :
               return False
     
class Request : 
     def __init__(self,data):
          self.method = data.get("method","")
          self.url = data.get("url","")
          self.httpVersion = data.get('httpVersion',"")
          self.headers = data.get('headers',[])
          self.postData = PostData(data.get('postData',{})) if 'postData' in data else None
          # self.queryString = data.get("queryString", [])
          # self.cookies = data.get("cookies",[])
          # self.headersSize = data.get("headersSize","")
          # self.bodySize = data.get("bodySize", "")
     
     def to_dict(self):
          return {
               "method": self.method,
               "url": self.url,
               "httpVersion": self.httpVersion,
               "headers": self.headers,
               "postData": self.postData.to_dict() if self.postData else None,
          #   "queryString": self.queryString,
          #   "cookies": self.cookies,
          #   "headersSize": self.headersSize,
          #   "bodySize": self.bodySize
          }
     
     def get_bruno_data(self):
          return{
               "method": self.method,
               "url": self.url + "?" + self.getUrlArgument() if self.hasParams() else self.url,
               # "httpVersion": self.httpVersion,
               "headers": [], # to see later if headers needed
               "params" : self.postData.get_bruno_params() if self.hasParams() else [], # get on parameters
               # "postData": self.postData.get_bruno_data() if self.postData else None,
               "body": {
                    "mode": "xml",
                    "xml": self.postData.get_bruno_postbody() if self.hasPostData() else "",
                    "json":"",
                    "formUrlEncoded": [],
                    "multipartForm": [],
                    "file": []
               },
               "script": {},
               "vars": {},
               "assertions": [],
               "tests":"", 
               "docs": "",
               "auth": {
               "mode": "inherit"
               }
          }
     def setTests(self,bruno_data,response):
          bruno_data["tests"] = response
          return bruno_data

     def getUrlArgument(self):
          if self.hasPostData():
               args = self.postData.text
               if not self.postData.hasPostBody() :
                    return args
               else :
                    return args
          else:
               return ''

     def isXML(self):
          return self.url.endswith('.xml')
     
     def hasPostData(self) : 
          return self.postData is not None
     
     def hasParams(self):
          return self.postData.hasParams() if self.hasPostData() else False

     def hasPostBody(self):
          return self.postData.hasPostBody() if self.hasPostData() else False

class PostData : 
     def __init__(self,data):
          self.mimeType = data.get("mimeType","")
          self.text = data.get("text","")
          self.params = [Param(param) for param in data.get("params",[])]
     
     def to_dict(self):
          return {
               "mimeType": self.mimeType,
               "text": self.text,
               "params": [param.to_dict() for param in self.params]
          }
     
     def get_bruno_data(self):
          return{
               "mimeType": self.mimeType,
               "text": self.text,
               "params": [param.get_bruno_data() for param in self.params]
          }
     
     def get_bruno_params(self):
          return [param.get_bruno_params() for param in self.params] if self.hasParams() else []
     
     def get_bruno_postbody(self):
          for param in self.params:
               if param.get_bruno_postbody() is not None:
                    return param.get_bruno_postbody()
          return ''
     
     def getParamsLength(self):
          return len(self.params)
     
     def hasPostBody(self): 
          return any(param.name == 'postbody' for param in self.params)
     
     def hasParams(self): # only return if there is params other than postbody
          return any(param.name != 'postbody' for param in self.params)

class Param : 
     def __init__(self, data):
          self.name = data.get("name","")
          self.value = data.get("value","")
     
     def to_dict(self) :
          return {"name" : self.name, "value" : self.value}
     
     def get_bruno_data(self):
          return {"name" : self.name, "value" : self.value, "type" : "query", "enabled" : True}
     
     def get_bruno_params(self):
          return {"name" : self.name, "value" : self.value, "type" : "query", "enabled" : True} if self.name != 'postbody' else None
     
     def get_bruno_postbody(self):
          return self.clean_to_xml(self.value) if self.name == 'postbody' else None
     
     def clean_to_xml(self,url_to_convert):
          xml_form = unquote(url_to_convert)
          xml_form = xml_form.replace('+', ' ').replace('\t', '  ')
          return xml_form

class Response:
     def __init__(self,data):
          self.status = data.get("status",None)
          self.content = Content(data.get("content",{}))

     def get_bruno_response(self):
          return {"status" : self.status, "text" : self.content.get_bruno_text()}

class Content : 
     def __init__(self, data):
          self.mimeType = data.get("mimeType",None)
          self.text = data.get("text",None)

     def get_bruno_text(self):
          return self.text
