import logging
import threading
import SessionContextService
import SlackTokenService
import Constants

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(levelname)s %(name)s %(message)s')
logger = logging.getLogger(__name__)

def startClearInactiveUserTimer():
    # Remove inactive user sessions every 5 minutes
    clearInactiveUserTimer = threading.Timer(5 * 60, target=SessionContextService.cleanup_inactive_sessions(Constants.USER_SESSION_DICT))
    clearInactiveUserTimer.start()

def startRefreshTokenTimer():
    # Refresh bot token every 12 hours
    refreshTokenTImer = threading.Timer(12 * 60 * 60, target=SlackTokenService.refresh_bot_token())
    refreshTokenTImer.start()

# if __name__ == "__main__":
    # startClearInactiveUserTimer()
    # startRefreshTokenTimer()