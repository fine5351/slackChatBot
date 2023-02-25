import openai
from slack_bolt.adapter.socket_mode import SocketModeHandler
from slack_sdk import WebClient
from slack_bolt import App
import logging
import time
import Constants
import SlackTokenService

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(levelname)s %(name)s %(message)s')
logger = logging.getLogger(__name__)

# Create Slack API client
client = WebClient(token=Constants.SLACK_BOT_OAUTH_TOKEN)

# Create Slack Bolt app
app = App(token=Constants.SLACK_BOT_OAUTH_TOKEN)

USER_SESSION_DICT = Constants.USER_SESSION_DICT

# Handler for app mention events
@app.event("app_mention")
def handle_message_events(body, logger):
    
    global USER_SESSION_DICT
    # Get user ID
    user_id = body["event"]["user"]
    # Get user input message
    input_message = str(body["event"]["text"]).split(">")[1].strip()
    # Log message
    logging.info("user_id: %s, input_message : %s",user_id, input_message)

    # Get session context
    session_dict = USER_SESSION_DICT.get(user_id, {})
    
    if "rcs" in input_message.strip():
        session_dict['user_id'] = ""
        client.chat_postMessage(channel=body["event"]["channel"], 
                                thread_ts=body["event"]["event_ts"],
                                text=f"對話已重置")
        return

    # Let the user know that we are busy with the request 
    response = client.chat_postMessage(channel=body["event"]["channel"], 
                                        thread_ts=body["event"]["event_ts"],
                                        text=f"正在處理結果中, 請耐心等待回覆...")
    
    # Check ChatGPT
    openai.api_key = Constants.OPENAI_API_KEY
    input_message = session_dict.get('input_message', '') + "\n" + input_message
    response = openai.Completion.create(
        engine=Constants.MODEL_ENGINE,
        prompt=input_message,
        max_tokens=Constants.MAX_TOKEN,
        n=1,
        stop=None,
        temperature=0.5).choices[0].text
    
    session_dict['user_id'] = time.time()
    session_dict['input_message'] = session_dict.get('input_message', '') + "\n" + response

    # Reply to thread 
    response = client.chat_postMessage(channel=body["event"]["channel"], 
                                        thread_ts=body["event"]["event_ts"],
                                        text=f"回答如下:{response}")
    
    logging.info("user_id: %s, response : %s", user_id, response['message']['text'])
    SlackTokenService.refresh_bot_token()

if __name__ == "__main__":
    # Start SocketModeHandler    
    SocketModeHandler(app, Constants.SLACK_SOCKET_MODE_TOKEN).start()
