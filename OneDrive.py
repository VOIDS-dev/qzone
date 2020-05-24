import onedrivesdk
from config import *
import requests
import json
import os
import sys
from string import Template
from anaconda_navigator.utils.py3compat import request
from astroid.__pkginfo__ import description

kilobytes = 1024
standardbytes = kilobytes*320
chunk_size = standardbytes*60


class OneDriveUtil():
    
    def __init__(self):
        self.http_provider = onedrivesdk.HttpProvider()
        self.auth_provider = onedrivesdk.AuthProvider(
            http_provider=self.http_provider,
            client_id=client_id,
            scopes=scopes)
        self.client = onedrivesdk.OneDriveClient(graph_base_url, self.auth_provider, self.http_provider)
    
    def authenticate(self):
        self.auth_url = self.client.auth_provider.get_auth_url(redirect_uri)
        # Ask for the code
        print('Paste this URL into your browser, approve the app\'s access.')
        print('Copy everything in the address bar after "code=", and paste it below.')
        print(self.auth_url)
        code = input('Paste code here: ')
        payload={
            "redirect_uri": redirect_uri,
            "scope" : " ".join(scopes),
            "code" : code,
            "grant_type" : grant_type,
            "client_id" : client_id
#                        "client_secret" : client_secret
            }        
        self.custom_response = json.loads(
            requests.post(token_base_url+token_path, data=payload).text
            )
        print(self.custom_response)
    
    def refresh_token(self):
        
        payload = {
            "redirect_uri": redirect_uri,
            "scope" : " ".join(scopes),
            "refresh_token" : self.custom_response['refresh_token'],
            "grant_type" : 'refresh_token',
            "client_id" : client_id
#           "client_secret" : client_secret
        }  
        self.custom_response = json.loads(
            requests.post(token_base_url+token_path, data=payload).text
            )
        print(self.custom_response)
        pass
    
    def upload_file(self,filename):
        url = graph_base_url
        
    def retrive_filelist(self):
        url = graph_base_url
        path = "/me/drive/root/children"
        headers={"Authorization": "bearer " + self.custom_response['access_token']}
        r = json.loads(requests.get(graph_base_url+path,headers=headers).text)
        print(r)
        return r
    
    def create_folder(self, parent_path, foldername):
        url = graph_base_url
        if not parent_path:
            path = "/me/drive/root/children"
        else:
            path = "/me/drive/root:"+parent_path+":/children"
        headers={
            "Authorization": "bearer " + self.custom_response['access_token'],
            "Content-Type" : "application/json"
            }
        payload=json.dumps({
            "name": foldername,
            "folder": { },
            "@microsoft.graph.conflictBehavior": "fail",
            })
        r = json.loads(requests.post(graph_base_url+path,data=payload,headers=headers).text)
        print(r)
        return r
        
    def upload_largefile(self, parent_path, filename, description = ""):
        url = graph_base_url
        if not parent_path:
            path = "/me/drive/root:/"+filename+":/createUploadSession"
            parent_path = "."
        else:
            path = "/me/drive/root:"+parent_path+":/"+filename+":/createUploadSession"
            
        headers={
            "Authorization": "bearer " + self.custom_response['access_token'],
            "Content-Type" : "application/json"
            }
        
        payload = json.dumps({
            "item": {
                "@odata.type": "microsoft.graph.driveItemUploadableProperties",
                "@microsoft.graph.conflictBehavior": "replace",
                "name": filename,
                "description": description
                }
            })
        
        session_response = json.loads(requests.post(graph_base_url+path,data = payload, headers = headers).text)
        upload_url = session_response['uploadUrl']
        print(session_response)
        self.upload_file_by_session(parent_path, filename, upload_url, session_response)
        
        
    
    def resume_upload_largefile(self, uploadurl, parent_path, filename, description = ""):
        url = graph_base_url
        if not parent_path:
            path = "/me/drive/root:/"+filename+":/createUploadSession"
            parent_path = "."
        else:
            path = "/me/drive/root:"+parent_path+":/"+filename+":/createUploadSession"
            
        headers={
            "Authorization": "bearer " + self.custom_response['access_token'],
            "Content-Type" : "application/json"
            }
        
        payload = json.dumps({
            "item": {
                "@odata.type": "microsoft.graph.driveItemUploadableProperties",
                "@microsoft.graph.conflictBehavior": "fail",
                "name": filename,
                "description": description
                }
            })
        session_response = json.loads(requests.get(uploadurl,data = payload, headers = headers).text)
        self.upload_file_by_session(parent_path, filename, uploadurl, session_response)
        
    
    def upload_file_by_session(self,parent_path, filename, uploadurl, session_response):
        with open(parent_path+"/"+filename,"rb") as f:
            file_size = os.path.getsize(parent_path+"/"+filename)
            
            content_range_template = Template("bytes $start-$end/" + str(file_size))
            data_chunk = f.read(chunk_size)
            uploaded_size = 0
            
            next_expected_ranges = self.transform_expected_range(session_response)            
            chunk_break = 0
            
            while(data_chunk):
                print(next_expected_ranges)
#                 chunk_break+=1
                
                if chunk_break >= 3:
                    break
                
                start = uploaded_size
                end = uploaded_size+len(data_chunk)-1
                size = len(data_chunk)

                is_expected = False
                for expected_range in next_expected_ranges:      
                    if not (start > expected_range['end'] or end < expected_range['start']):
                        is_expected = True
                        break
                if not is_expected:
                    data_chunk = f.read(chunk_size)
                    uploaded_size += size 
                    continue  
                
                upload_headers = {
                    "Authorization": "bearer " + self.custom_response['access_token'],
                    "Content-Length": str(size),
                    "Content-Range": content_range_template.substitute(start=str(start),end=str(end))
                    }
                
                upload_response = requests.put(uploadurl, data=data_chunk, headers=upload_headers)
                print(upload_response.text)
                if upload_response.status_code == 200 or upload_response.status_code == 201:
                    print("Done")
                    break
                upload_info = json.loads(upload_response.text)
                uploaded_size += size                   
                next_expected_ranges = self.transform_expected_range(upload_info)
                print(next_expected_ranges)
                data_chunk = f.read(chunk_size) 
        
    
    def transform_expected_range(self, upload_info):
        next_expected_ranges = []
        for expected_range in upload_info['nextExpectedRanges']:
            start,end = expected_range.split('-')
            if not end:
                end = sys.maxsize
            next_expected_ranges.append({
                'start': int(start),
                'end' : int(end)
                })            
        return next_expected_ranges
    
    def save_uploadurl(self,  uploadurl, parent_path, filename):
        
        
        
        
#     client = onedrivesdk.OneDriveClient(api_base_url, auth_provider, http_provider)
#     auth_url = client.auth_provider.get_auth_url(redirect_uri)
#     # Ask for the code
#     print('Paste this URL into your browser, approve the app\'s access.')
#     print('Copy everything in the address bar after "code=", and paste it below.')
#     print(auth_url)
#     code = raw_input('Paste code here: ')
#     
#     client.auth_provider.authenticate(code, redirect_uri, client_secret)

if __name__ == '__main__':
    onedrive = OneDriveUtil()
    onedrive.authenticate()
    onedrive.refresh_token()
    onedrive.retrive_filelist()
    onedrive.create_folder(parent_path= "/a new folder", foldername="a new child")
    #onedrive.upload_largefile(parent_path = None ,filename = "[高清 720P] 震 撼 老 师 夏 色 祭.flv")
    uploadurl = 'https://api.onedrive.com/rup/e2dc01d552a3277/eyJSZXNvdXJjZUlEIjoiRTJEQzAxRDU1MkEzMjc3ITEwOCIsIlJlbGF0aW9uc2hpcE5hbWUiOiJb6auY5riFIDcyMFBdIOmchyDmkrwg6ICBIOW4iCDlpI8g6ImyIOelrS5mbHYifQ/4m-SzK-duUSQpmVT6VQQ7VaVOlpUSqa8tQ__kHPdIx7rTPPt2mZA2BxBOndd6qkPo9HN9alN_j2DVA_kiWKdliDyiiVZXOCvypd9_vyblKZGc/eyJuYW1lIjoiW-mrmOa4hSA3MjBQXSDpnIcg5pK8IOiAgSDluIgg5aSPIOiJsiDnpa0uZmx2IiwiZGVzY3JpcHRpb24iOiIiLCJAbmFtZS5jb25mbGljdEJlaGF2aW9yIjoicmVwbGFjZSJ9/4wH_fsk8HYJDeQwoPJG3wyWdeBDOC4L_CN1waF7bv5YdRoIushtt7oorHknhzLxl3gvtgKCIE4qfhqt0aniB0EC8Hw3nbvUw_kGKVQ2O9Bu6kNnjDEM4j57PqLUqVqDbcmjGs6Z71BeWHkZHTeuW_aLVWBwptCORGmWJndhfNQgUHAOkLYCSk3zi7fMS7K_ZPR5HSPUBcYsnV0V6GvqjUpWUcY-ZGSJ-EiWJvAN2eVoOKmICGWxX-FUv5XAwEQmRMKfuZOJgvJV3gwamxKOhEZoJTsdTcKjuiRfXf8uZv3BU44i_T4UXDP3bqL7YeG9EnOQcZwzNz2mCCmj64XxeYEgOF4PT6sf-fLgwSOekekCGHl_VSxEO_QdF0KAKba8vle3UrORbO0nKk7OXHB7mMNEbPxPBxDGmZLuuH5qWnGGuOuLJe-8MSWR37qszttiReIIEKQh8doT8kxReV9HBw2VmOP8Is8k5KMBltCPgGse54-ZmlWU2K7Yn_9IxT0ma6jELeJ5B8_-zX7iUGn2f3-ItDbhlKuVvgNlgduzY2g3Ws5F-wPiZejJF8OsP-b0DHe'
    onedrive.resume_upload_largefile(uploadurl = uploadurl, parent_path = None ,filename = "[高清 720P] 震 撼 老 师 夏 色 祭.flv")
#     root_folder = client.item(drive='me', id='root').children.get()
#     id_of_file = root_folder[0].id
# 
#     client.item(drive='me', id=id_of_file).download('./path_to_download_to')
    