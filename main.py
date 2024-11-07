from io import BytesIO
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
    CallbackContext,
    Application,
    PicklePersistence,
)
from config import BOT_TOKEN, ADMIN_CHAT_ID


# Приветственное сообщение и выбор языка
async def start(update: Update, context: CallbackContext) -> None:
    keyboard = [
        [InlineKeyboardButton("Russian", callback_data="lang_ru")],
        [InlineKeyboardButton("English", callback_data="lang_en")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "EOS Network Account — это обозреватель блокчейна. Мы не проводим и не отменяем транзакции. Вернуть криптовалюту может только получатель.\n\n"
        "EOS Network Account is a blockchain explorer. We neither cancel transactions nor sign them. Only the recipient can return the cryptocurrencies.\n\n"
        "Choose your language:",
        reply_markup=reply_markup,
    )


# Обработка выбора языка


def _check_lang(callback_data):
    return callback_data in ("lang_ru", "lang_en", "default")


async def language_selection(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    await query.answer()
    is_default = query.data == "default"

    if query.data == "lang_ru" or (
        is_default and context.user_data.get("lang") == "ru"
    ):
        context.user_data["lang"] = "ru"
        if query.data is not None and query.data != "default":
            await query.edit_message_text(
                text="Приветствуем! Если у вас есть вопросы о работе EOS Network, мы с радостью поможем вам\n\n"
                "❗️Важно: команда EOS Network не ответит на смежные вопросы (например, о курсе монеты EOS, возможностях blockchain и др.);\n"
                "Мы стараемся отвечать в течение нескольких часов, но иногда время ответа может увеличиться из-за потока входящих обращений."
            )
        await show_main_menu(update, context, reload=is_default)

    else:
        context.user_data["lang"] = "en"
        if query.data is not None and query.data != "default":
            await query.edit_message_text(
                text="Welcome! If you have questions about how the EOS Network works, we will be happy to help you\n\n"
                "❗️Important: the EOS Network team will not answer related questions (for example, about the EOS coin rate, blockchain capabilities, etc.);\n"
                "We try to respond within a few hours, but sometimes the response time may increase due to the flow of incoming requests."
            )
        await show_main_menu(update, context, reload=is_default)


# Показ главного меню
async def show_main_menu(update, context, user_id=None, reload=False):
    user_id = user_id or (
        update.message.chat_id if update.message else update.effective_chat.id
    )
    query = update.callback_query
    if context.user_data.get("lang", "en") == "ru":
        keyboard = [
            [InlineKeyboardButton("О токене EOS", callback_data="about_eos")],
            [InlineKeyboardButton("Сообщить о баге", callback_data="bug_report")],
            [InlineKeyboardButton("Не пришел перевод", callback_data="no_transfer")],
            [InlineKeyboardButton("Не указал Tag/Memо", callback_data="no_tag")],
        ]
        opt_text = "Пожалуйста, выберите опцию:"
    else:
        keyboard = [
            [InlineKeyboardButton("About EOS token", callback_data="about_eos")],
            [InlineKeyboardButton("Bug Report", callback_data="bug_report")],
            [
                InlineKeyboardButton(
                    "The transfer didn’t arrive", callback_data="no_transfer"
                )
            ],
            [InlineKeyboardButton("Didn’t include Tag/Memo", callback_data="no_tag")],
        ]
        opt_text = "Please choose an option:"

    reply_markup = InlineKeyboardMarkup(keyboard)
    if reload:
        await query.edit_message_text(text=opt_text, reply_markup=reply_markup)
    else:
        await context.bot.send_message(
            chat_id=user_id,
            text=opt_text,
            reply_markup=reply_markup,
        )


def _check_about_eos(callback_data):
    return callback_data == "about_eos"


def _check_bug_report(callback_data):
    return callback_data == "bug_report"


def _check_no_transfer(callback_data):
    return callback_data == "no_transfer"


def _check_no_tag(callback_data):
    return callback_data == "no_tag"


# Обработка выбора из меню
async def menu_selection(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    await query.answer()

    if context.user_data.get("lang") == "ru":
        if query.data == "about_eos":
            await query.edit_message_text(
                text="Что такое EOS?\n\n"
                "EOS использует механизм консенсуса Delegated Proof of Stake. Нативный токен сети EOS — это utility-токен, который используется для покупки системных ресурсов, участия в управлении блокчейном, перемещения средств в нативных приложениях и учета активов инвесторов и спекулянтов.\n"
                "Владельцы токенов также могут вносить EOS в стейкинг и получать часть комиссий, которые пользователи оплачивают за использование системных ресурсов в рамках модели EOS PowerUp Model.",
                reply_markup=InlineKeyboardMarkup(
                    [[InlineKeyboardButton("Назад", callback_data="default")]]
                ),
            )
        elif query.data == "bug_report":
            context.user_data["current_action"] = "bug_report"
            await query.edit_message_text(
                text="Грустно, что вы столкнулись с багом, но кто не ошибается, тот ничего не делает. Для того, чтобы сообщить о баге, пожалуйста:\n\n"
                "1) Подробно опишите проблему;\n"
                "2) Опишите шаги, которые нужно сделать, чтобы воспроизвести проблему;\n"
                "3) Приложите скриншоты или любые другие материалы, которые будут полезны для решения проблемы;\n"
                "4) Если необходимо, приложите адрес кошелька или ссылку на проблемную транзакцию.\n\n"
                "Мы ответим вам как можно быстрее.",
                reply_markup=InlineKeyboardMarkup(
                    [[InlineKeyboardButton("Назад", callback_data="default")]]
                ),
            )

        elif query.data == "no_transfer":
            context.user_data["current_action"] = "no_transfer"
            await query.edit_message_text(
                text="1) Подробно опишите проблему;\n"
                "2) Укажите дату и время транзакции;\n"
                "3) Сообщите ваш tag/memo идентификатор;\n"
                "4) Приложите скриншоты или любые другие материалы, которые будут полезны для решения проблемы.\n\n"
                "Мы ответим вам как можно быстрее.",
                reply_markup=InlineKeyboardMarkup(
                    [[InlineKeyboardButton("Назад", callback_data="default")]]
                ),
            )
        elif query.data == "no_tag":
            context.user_data["current_action"] = "no_tag"
            await query.edit_message_text(
                text="Здравствуйте! Команда EOS Network не может изменять или отменять транзакции.\n\n"
                "При отсутствии или некорректном Tag/Memo — обратитесь, пожалуйста, в поддержку биржи-получателя.",
                reply_markup=InlineKeyboardMarkup(
                    [[InlineKeyboardButton("Назад", callback_data="default")]]
                ),
            )

    elif context.user_data.get("lang") == "en":
        if query.data == "about_eos":
            await query.edit_message_text(
                text="What Is EOS?\n\n"
                "EOS uses Delegated proof-of-stake as its consensus mechanism. Its native token, EOS, is a utility token used on the network to purchase system resources, participate in EOS governance, transfer value on native applications, and account for value by investors and speculators.\n"
                "Token holders can also stake their idle EOS tokens to receive a percentage of the fees collected from users who wish to use EOS system resources through the EOS PowerUp Model.",
                reply_markup=InlineKeyboardMarkup(
                    [[InlineKeyboardButton("Back", callback_data="default")]]
                ),
            )

        elif query.data == "bug_report":
            context.user_data["current_action"] = "bug_report"
            await query.edit_message_text(
                text="It's sad that you encountered a bug, but those who don't make mistakes don't do anything. To report a bug, please:\n\n"
                "1) Describe the problem in detail;\n"
                "2) Describe the steps that need to be taken to reproduce the problem;\n"
                "3) Attach screenshots or any other materials that will be useful in solving the problem;\n"
                "4) If necessary, attach the wallet address or link to the problematic transaction.\n\n"
                "We will reply to you as quickly as possible.",
                reply_markup=InlineKeyboardMarkup(
                    [[InlineKeyboardButton("Back", callback_data="default")]]
                ),
            )
        elif query.data == "no_transfer":
            context.user_data["current_action"] = "no_transfer"
            await query.edit_message_text(
                text="1) Describe the problem in detail;\n"
                "2) Indicate the date and time of the transaction;\n"
                "3) Provide your tag/memo identifier;\n"
                "4) Attach screenshots or any other materials that will be useful in solving the problem.\n\n"
                "We will reply to you as quickly as possible.",
                reply_markup=InlineKeyboardMarkup(
                    [[InlineKeyboardButton("Back", callback_data="default")]]
                ),
            )
        elif query.data == "no_tag":
            context.user_data["current_action"] = "no_tag"
            await query.edit_message_text(
                text="Hello! The EOS Network team cannot modify or cancel transactions.\n\n"
                "If the Tag/Memo is missing or incorrect, please contact the support of the recipient exchange.",
                reply_markup=InlineKeyboardMarkup(
                    [[InlineKeyboardButton("Back", callback_data="default")]]
                ),
            )


# Обработка текстовых сообщений от пользователей
async def handle_message(update: Update, context: CallbackContext) -> None:
    user_message = update.message.text or update.message.caption
    user_id = update.message.chat_id
    current_action = context.user_data.get("current_action", None)
    photo = None
    if update.message.photo:
        photo = await context.bot.get_file(update.message.photo[-1].file_id)
        photo = BytesIO(await photo.download_as_bytearray())

    if user_id == ADMIN_CHAT_ID:
        await handle_admin_response(update, context)
        return

        # Переслать сообщение администратору
    if current_action:
        if photo:
            await context.bot.send_photo(
                chat_id=ADMIN_CHAT_ID,
                photo=photo,
                caption=f"Сообщение от пользователя {user_id}:\n\n"
                f"Действие: {current_action}\n\n"
                f"Сообщение:\n{user_message}",
            )
        else:
            await context.bot.send_message(
                chat_id=ADMIN_CHAT_ID,
                text=f"Сообщение от пользователя {user_id}:\n\n"
                f"Действие: {current_action}\n\n"
                f"Сообщение:\n{user_message}",
            )
        await update.message.reply_text(
            "Ваше сообщение было отправлено. Мы свяжемся с вами в ближайшее время."
        )
    else:
        await update.message.reply_text("Пожалуйста, выберите действие из меню.")


# Обработка ответов от администратора
async def handle_admin_response(update: Update, context: CallbackContext) -> None:
    if update.message.reply_to_message:
        original_message = None
        if (
            update.message.reply_to_message.text
            and "Сообщение от пользователя" in update.message.reply_to_message.text
        ):
            original_message = update.message.reply_to_message.text

        if (
            update.message.reply_to_message.caption
            and "Сообщение от пользователя" in update.message.reply_to_message.caption
        ):
            original_message = update.message.reply_to_message.caption

        if not original_message:
            return

        user_id = int(original_message.split()[3].replace(":", "").strip())
        admin_response = update.message.text
        if context.user_data.get("lang") == "ru":
            text = f"Ответ от администрации:\n\n {admin_response}"
        else:
            text = f"Admin response: {admin_response}"
        # Отправить ответ пользователю
        await context.bot.send_message(chat_id=user_id, text=text)
        await show_main_menu(update, context, user_id=user_id)


def main():
    persistence = PicklePersistence(filepath="EOSNetworkAccountBot.pickle")

    app = Application.builder().token(BOT_TOKEN).persistence(persistence).build()
    add_handlers(app)
    app.run_polling(allowed_updates=Update.ALL_TYPES)


def add_handlers(app):
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(language_selection, pattern=_check_lang))
    app.add_handler(CallbackQueryHandler(menu_selection, pattern=_check_bug_report))
    app.add_handler(CallbackQueryHandler(menu_selection, pattern=_check_no_tag))
    app.add_handler(CallbackQueryHandler(menu_selection, pattern=_check_about_eos))
    app.add_handler(CallbackQueryHandler(menu_selection, pattern=_check_no_transfer))
    app.add_handler(
        MessageHandler(
            (filters.PHOTO | filters.TEXT) & ~filters.COMMAND, handle_message
        )
    )


if __name__ == "__main__":
    main()
