import requests
import os

    
class Client:
    def __init__(self):
        self.base_url = os.environ.get('LOCAL_LLM_BASE_URL', "http://127.0.0.1:5000/")
        # self.headers = {
        #     "api_key": self.api_key 
        # }

    def create_chat_completion(self,messages, temperature, max_tokens):
        # print(temperature,max_tokens,type(temperature),type(max_tokens))
        if max_tokens is None:
            max_tokens=200
        if float(temperature)==0.0:
            temperature=0.01
        request = {'prompt': str(messages),'temperature': float(temperature), 'max_tokens': int(max_tokens)}

        response = requests.post(self.base_url+'/api/v1/generate', json=request)
        
        if response.status_code == 200:

            resp=response.json()
            print(resp)
            return resp['results'][0]['text']
        else:
            return "Error " 


    def get_embedding(self,text):
        request = {'text':str(text)}

        response = requests.post(self.base_url+'/api/v1/get-embeddings', json=request)
        
        if response.status_code == 200:
            return response.json()['results'][0]['embeddings']
        else:
            return ["Error"]

