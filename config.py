from environs import Env


env = Env()
env.read_env()

with env.prefixed("APP_"):
    BOT_TOKEN = env.str("BOT_TOKEN")
    ADMIN_CHAT_ID = env.int("ADMIN_CHAT_ID")


with env.prefixed("CHECKER_"):
    CHECKER_TOKEN = env.str("BOT_TOKEN")
    CH1 = env.str("CH1")
    CH2 = env.str("CH2")
    LINK = env.str("LINK")
    ADMIN = env.str('ADMIN')
