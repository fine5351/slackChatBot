import os
import openai
import time
from slack_bolt.adapter.socket_mode import SocketModeHandler
from slack_sdk import WebClient
from slack_bolt import App
import threading
import logging


SLACK_BOT_TOKEN = "xoxb-12553261381-4867863505825-XJyVTKHVmQHrIuVYpPQet6QY"
SLACK_APP_TOKEN = "xapp-1-A04RUS4PXG8-4855215966722-47b09ce84f5af6579fcaf2e20834883c764ef43206170773a20852172d6345cc"
OPENAI_API_KEY = "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"
MODEL_ENGINE = "text-davinci-003"
MAX_TOKEN = 2048
SESSION_CONTEXT = {}

# Create Slack API client
client = WebClient(token=SLACK_BOT_TOKEN)

# Create Slack Bolt app
app = App(token=SLACK_BOT_TOKEN)

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(levelname)s %(name)s %(message)s')
logger = logging.getLogger(__name__)

# Remove inactive user sessions every 5 minutes
def cleanup_inactive_sessions():
    while True:
        time.sleep(10)
        logger.info("Cleaning up inactive sessions")
        now = time.time()
        for user_id, last_active_time in SESSION_CONTEXT.items():
            if now - last_active_time > 300:
                del SESSION_CONTEXT[user_id]
        logger.info("Inactive sessions cleaned up")

# Thread to remove inactive user sessions
cleanup_thread = threading.Thread(target=cleanup_inactive_sessions, daemon=True)
cleanup_thread.start()

# Handler for app mention events
@app.event("app_mention")
def handle_message_events(body, logger):
    # Get user ID
    user_id = body["event"]["user"]
    # Get user input message
    input_message = str(body["event"]["text"]).split(">")[1]
    # Log message
    logging.info("user_id: %s, input_message : %s",user_id, input_message)

    # Get session context
    session_context = SESSION_CONTEXT.get(user_id, "")
    
    if "rcs" in input_message.strip():
        SESSION_CONTEXT[user_id] = ""
        client.chat_postMessage(channel=body["event"]["channel"], 
                                thread_ts=body["event"]["event_ts"],
                                text=f"對話已重置")
        return

    # Let the user know that we are busy with the request 
    response = client.chat_postMessage(channel=body["event"]["channel"], 
                                        thread_ts=body["event"]["event_ts"],
                                        text=f"正在處理結果中, 請耐心等待回覆...")
    
    # Check ChatGPT
    openai.api_key = OPENAI_API_KEY
    input_message = session_context + "\n" + input_message
    response = openai.Completion.create(
        engine=MODEL_ENGINE,
        prompt=input_message,
        max_tokens=MAX_TOKEN,
        n=1,
        stop=None,
        temperature=0.5).choices[0].text
    
    SESSION_CONTEXT[user_id] = time.time()
    SESSION_CONTEXT[user_id] = session_context + "\n" + response

    # Reply to thread 
    response = client.chat_postMessage(channel=body["event"]["channel"], 
                                        thread_ts=body["event"]["event_ts"],
                                        text=f"回答如下:{response}")
    
    logging.info("user_id: %s, response : %s", user_id, response['message']['text'])

if __name__ == "__main__":
    # Start SocketModeHandler
    SocketModeHandler(app, SLACK_APP_TOKEN).start()
