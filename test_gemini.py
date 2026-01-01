import google.generativeai as genai

genai.configure(api_key="AIzaSyDXiGnYrdyb6yNEzJW_eQ4f1i1RjGF_tpg")

model = genai.GenerativeModel("gemini-1.5-flash")
print(model.generate_content("Say OK").text)
