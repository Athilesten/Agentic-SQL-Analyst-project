import google.generativeai as genai

print("Program Started")

API_KEY = 

genai.configure(api_key=API_KEY)

print("API Configured")

for model in genai.list_models():
    print(model.name)

print("Program Finished")