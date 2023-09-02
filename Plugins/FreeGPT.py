import g4f
# from Plugins.GPT3_Sifc import sifcGPTMgr

class FreeGPT:
    def call(self, query: str):
        chat_completion = g4f.ChatCompletion.create(
                         model="gpt-3.5-turbo",
                        messages=[{"role": "user", "content": query}],
                        provider=	g4f.Provider.DeepAi,
                        #  stream=True,
                    )  
        return True,chat_completion
        # return sifcGPTMgr.call(query)
 
freeGPTMgr = FreeGPT()    