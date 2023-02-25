import logging
import time

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(levelname)s %(name)s %(message)s')
logger = logging.getLogger(__name__)

def cleanup_inactive_sessions(session_dict):
    logger.info("======================================================================================")
    logger.info("context users : %s", session_dict)
    logger.info("Cleaning up inactive sessions")
    now = time.time()
    for user_id, last_active_time in session_dict.items():
        if now - last_active_time > 300:
            del session_dict[user_id]
            logger.info("User %s session cleaned up", user_id)
    logger.info("Inactive sessions cleaned up")
    logger.info("======================================================================================")

# if __name__ == "__main__":
#     dictionary = {}
#     cleanup_inactive_sessions(dictionary)        
        