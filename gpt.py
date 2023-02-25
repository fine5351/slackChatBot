SLACK_BOT_TOKEN = "xoxb-12553261381-4867863505825-XJyVTKHVmQHrIuVYpPQet6QY"
SLACK_APP_TOKEN = "xapp-1-A04RUS4PXG8-4855215966722-47b09ce84f5af6579fcaf2e20834883c764ef43206170773a20852172d6345cc"
OPENAI_API_KEY  = "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"
MODEL_ENGINE = "text-davinci-003"
MAX_TOKEN = 2048
SESSION_CONTEXT = ""

import os
import openai
from slack_bolt.adapter.socket_mode import SocketModeHandler
from slack_sdk import WebClient
from slack_bolt import App

# Event API & Web API
app = App(token=SLACK_BOT_TOKEN) 
client = WebClient(SLACK_BOT_TOKEN)

# This gets activated when the bot is tagged in a channel    
@app.event("app_mention")
def handle_message_events(body, logger):
    
    global SESSION_CONTEXT
    # Log message
    print(str(body["event"]["text"]).split(">")[1])
    
    # Create prompt for ChatGPT
    prompt = str(body["event"]["text"]).split(">")[1]

    if "rcs" in prompt.strip():
        SESSION_CONTEXT = ""
        client.chat_postMessage(channel=body["event"]["channel"], 
                                       thread_ts=body["event"]["event_ts"],
                                       text=f"對話已重置")
        return
    
    # Let thre user know that we are busy with the request 
    response = client.chat_postMessage(channel=body["event"]["channel"], 
                                       thread_ts=body["event"]["event_ts"],
                                       text=f"正在處理結果中, 請耐心等待回覆...")
    
    # Check ChatGPT
    openai.api_key = OPENAI_API_KEY
    prompt = SESSION_CONTEXT + "\n" + prompt
    response = openai.Completion.create(
        engine=MODEL_ENGINE,
        prompt=prompt,
        max_tokens=MAX_TOKEN,
        n=1,
        stop=None,
        temperature=0.5).choices[0].text
    
    SESSION_CONTEXT = SESSION_CONTEXT + "\n" + response
    
    # Reply to thread 
    response = client.chat_postMessage(channel=body["event"]["channel"], 
                                       thread_ts=body["event"]["event_ts"],
                                       text=f"回答如下:\n{response}")

if __name__ == "__main__":
    SocketModeHandler(app, SLACK_APP_TOKEN).start()