from flask import Flask, render_template, request, redirect
import openai
import uuid
import os
import time
import json

# Key einstellen
openai.api_key = "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"

# Define the name of the bot
name = 'Response'

messages = []

# Define the impersonated role with instructions
impersonated_role = ""

# Initialize variables for chat history
explicit_input = ""
Output = 'Output: /n'
historyLocation = os.getcwd() + "/chat_history"
index = uuid.uuid4()
# Find an available chat history file
while os.path.exists(os.path.join(historyLocation, f'{index}.json')):
    index = uuid.uuid4()

history_file = os.path.join(historyLocation, f'{index}.json')

# Create a new chat history file
with open(history_file, 'w') as f:
    f.write('\n')

# Initialize chat history
chat_history = ''

# Create a Flask web application
app = Flask(__name__)

# Function to complete chat input using OpenAI's GPT-3.5 Turbo
def Getoutput(user_input, impersonated_role, explicit_input, chat_history):
    output = openai.ChatCompletion.create(
        model="gpt-3.5-turbo-0301",
        temperature=1,
        presence_penalty=0,
        frequency_penalty=0,
        max_tokens=2000,
        messages=[
            {"role": "system", "content": f"{impersonated_role}. Conversation history: {chat_history}"},
            {"role": "user", "content": f"{user_input}. {explicit_input}"},
        ]
    )

    for item in output['choices']:
        chatgpt_output = item['message']['content']

    return chatgpt_output

# Function to handle user chat input
def chat(user_input):
    global chat_history, name, chatgpt_output
    Day = time.strftime("%d/%m", time.localtime())
    Time = time.strftime("%H:%M:%S", time.localtime())
    chat_history += f'\nUser: {user_input}\n'
    output = Getoutput(user_input, impersonated_role, explicit_input, chat_history).replace(f'{name}:', '')
    chatgpt_output = f'{name}: {output}'
    chat_history += chatgpt_output + '\n'

    data = {
        "msg":{
            "day": Day,
            "time": Time,
            "user_input": user_input,
            "reponse": chatgpt_output
        }
    }
    messages.append(data)

    json_data = json.dumps(messages, indent=4)

    with open(history_file, 'w') as f:
        f.write(json_data +' \n')
        f.close()
    return output

# Function to get a response from the chatbot
def get_response(userText):
    return chat(userText)

# Home route
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/get")
# Get AI response
def get_bot_response():
    userText = request.args.get('msg')
    return str(get_response(userText))

@app.route("/deletes")
# Delete the history
def guide_delete():
    global chat_history, messages
    chat_history = ''
    messages.clear()
    json_data = json.dumps(messages, indent=4)
    with open(history_file, 'w') as f:
        f.write(json_data + ' \n')
        f.close()
    return ''


# Start the Flask app
if __name__ == "__main__":
    app.run()
