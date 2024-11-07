from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ChatJoinRequestHandler,
    CallbackContext,
)

from config import CHECKER_TOKEN, LINK, CH1, CH2, ADMIN


async def handle_join_request(update: Update, context: CallbackContext):
    try:
        request = update.chat_join_request
        user = request.from_user

        # if await check_subscription(context, user.id, CH2):
        #     await context.bot.approve_chat_join_request(chat_id=CH1, user_id=user.id)
        # elif not context.user_data.get("sent", False):
        if not context.user_data.get("sent", False) and not await check_subscription(context, user.id, CH2):
            context.user_data["sent"] = True
            await context.bot.send_message(
                chat_id=user.id,
                text=f"Пока доступ в мой канал для тебя\nзакрыт и откроется в автоматическом\nрежиме лишь при подписки на мой\nвторой канал\nДерзай и не теряй шанс заработать😉 {LINK}",
            )

        # if not await check_subscription(context, user.id, CH2):
        await context.bot.approve_chat_join_request(chat_id=CH2, user_id=user.id)

        return
    except Exception as e:
        print(e)


async def check_subscription(
    context: CallbackContext, user_id: int, channel_id: int
) -> bool:
    try:
        member = await context.bot.get_chat_member(chat_id=channel_id, user_id=user_id)
        return member.status in ["member", "creator", "administrator"]
    except Exception as e:
        print(f"Помилка при перевірці підписки: {e}")
    return False


async def start(update: Update, context: CallbackContext):
    await update.message.reply_text(text=f"Подпишись сначала на наш канал {LINK}.")


async def set_link(update: Update, context: CallbackContext):
    if update.message.chat_id == ADMIN:
        global LINK
        LINK = update.message.text.split("/set_link ")[1]
        await update.message.reply_text(text=f"Ссылка успешно изменена на {LINK}.")


def main() -> None:
    application = Application.builder().token(CHECKER_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("set_link", set_link))
    application.add_handler(ChatJoinRequestHandler(handle_join_request))
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
