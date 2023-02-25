import logging
import requests
import Constants

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(levelname)s %(name)s %(message)s')
logger = logging.getLogger(__name__)

def exchange_bot_token():
    logger.info("======================================================================================")
    
    # slack rotate bot token api
    response = requests.post(
        url = Constants.SLACK_BOT_TOKEN_EXCHANGE_API_URL,
        headers = {
            "Content-Type": "application/x-www-form-urlencoded"
        },  
        data = {
            "client_id": Constants.SLACK_CLIENT_ID,
            "client_secret": Constants.SLACK_CLIENT_SECRET,
            "token": Constants.SLACK_BOT_OAUTH_TOKEN
        }
    )

    response_json = response.json()
    logger.info("response %s", response_json)

    logger.info("======================================================================================")
    
    # 提取新的 bot token
    if response_json.get('ok') == True:
        return response_json.g["access_token"]
    else:
        logger.error("Failed to get new bot token: %s", response_json)    


def refresh_bot_token():
    logger.info("======================================================================================")
    
    response = requests.post(
        url = Constants.SLACK_BOT_TOKEN_REFRESH_API_URL,
        headers = {
            "Content-Type": "application/x-www-form-urlencoded"
        },  
        data = {
            "client_id": Constants.SLACK_CLIENT_ID,
            "client_secret": Constants.SLACK_CLIENT_SECRET,
            "refresh_token": Constants.SLACK_REFRESH_TOKEN,
            "grant_type": "refresh_token"
        }
    )

    response_json = response.json()
    logger.info("response %s", response_json)
    logger.info("======================================================================================")

    if response_json.get('ok') == True:
        return response_json.get("access_token")
    else:
        logger.error("Failed to update token: %s", response_json)    
    
if __name__ == "__main__":
    exchange_bot_token()
    refresh_bot_token()    
