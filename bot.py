import os
import asyncio
import traceback

from datetime import datetime, timedelta
from html import escape
from urllib.parse import urlparse

from dotenv import load_dotenv

from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)

from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
    MessageHandler,
    filters,
)


from database import (
    init_database,
    save_user,
    get_user,
    get_user_count,

    get_packages,
    get_package,

    add_package,
    update_package,
    set_package_status,

    create_order,
    get_order,

    get_pending_orders,
    get_user_orders,

    update_order_status,

    get_order_count,
    get_pending_count,
    get_total_sales,

    save_payment_proof,
    save_config,
    get_user_configs,

    get_referral_stats,
    create_referral_earning,
)


from panel import (
    ThreeXUI,
    apply_sni,
)



# ==============================
# LOAD SETTINGS
# ==============================

load_dotenv()


def env(name, default=""):

    return str(
        os.getenv(
            name,
            default
        )
        or ""
    ).strip()



BOT_TOKEN = env(
    "BOT_TOKEN"
)


ADMIN_ID = int(
    env(
        "ADMIN_ID",
        "0"
    )
)



PANEL_URL = env(
    "PANEL_URL"
).rstrip("/")


PANEL_USERNAME = env(
    "PANEL_USERNAME"
)


PANEL_PASSWORD = env(
    "PANEL_PASSWORD"
)


PANEL_API_TOKEN = env(
    "PANEL_API_TOKEN"
)



BANK_NAME = env(
    "BANK_NAME",
    "YOUR BANK"
)


ACCOUNT_NAME = env(
    "ACCOUNT_NAME",
    "V2RayX"
)


ACCOUNT_NUMBER = env(
    "ACCOUNT_NUMBER",
    "0000000000"
)


BRANCH = env(
    "BRANCH",
    "MAIN"
)


SUPPORT_USERNAME = env(
    "SUPPORT_USERNAME",
    "@support"
)



REFERRAL_PERCENTAGE = int(
    env(
        "REFERRAL_PERCENTAGE",
        "5"
    )
)



# ==============================
# 3X-UI CONNECT
# ==============================


xui = ThreeXUI(

    PANEL_URL,

    PANEL_USERNAME,

    PANEL_PASSWORD,

    PANEL_API_TOKEN

)



# ==============================
# HELPERS
# ==============================


def safe_int(v, default=0):

    try:

        return int(v)

    except:

        return default



def safe_float(v, default=0):

    try:

        return float(v)

    except:

        return default



def html_text(v):

    return escape(
        str(v or "")
    )



def gb_text(v):

    v = safe_float(v)

    if v <= 0:

        return "Unlimited"

    return f"{v:g} GB"



def admin_only(uid):

    return safe_int(uid) == ADMIN_ID



def url_host(url):

    try:

        return urlparse(url).hostname or ""

    except:

        return ""



# ==============================
# MAIN MENU
# ==============================


def main_menu():

    return InlineKeyboardMarkup([

        [

            InlineKeyboardButton(
                "🛒 Buy Config",
                callback_data="buy"
            ),

            InlineKeyboardButton(
                "📦 My Configs",
                callback_data="configs"
            )

        ],


        [

            InlineKeyboardButton(
                "🧾 Orders",
                callback_data="orders"
            ),


            InlineKeyboardButton(
                "💳 Payment",
                callback_data="payment"
            )

        ],


        [

            InlineKeyboardButton(
                "🎁 Referrals",
                callback_data="referrals"
            ),


            InlineKeyboardButton(
                "👤 Account",
                callback_data="account"
            )

        ],


        [

            InlineKeyboardButton(
                "🆘 Support",
                callback_data="support"
            )

        ]

    ])
    # ==============================
# START COMMAND
# ==============================


async def start(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    user = update.effective_user

    if not user:
        return


    referral = None


    if context.args:

        referral = (
            context.args[0]
            .strip()
            .upper()
        )


    try:

        save_user(

            user.id,

            user.username,

            user.first_name,

            referral

        )


    except Exception as e:

        print(
            "Save user error:",
            e
        )



    await update.message.reply_text(

        f"🟢 <b>V2RayX</b>\n\n"
        f"Welcome {html_text(user.first_name)} 👋\n\n"
        "Choose option:",

        parse_mode="HTML",

        reply_markup=main_menu()

    )




# ==============================
# GET TELEGRAM ID
# ==============================


async def get_id(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    user = update.effective_user


    await update.message.reply_text(

        f"🆔 Your ID:\n\n"
        f"<code>{user.id}</code>",

        parse_mode="HTML"

    )




# ==============================
# ADMIN COMMAND
# ==============================


async def admin(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    user = update.effective_user


    if not admin_only(user.id):

        await update.message.reply_text(

            "⛔ Admin only."

        )

        return



    await send_admin_dashboard(

        user.id,

        context

    )




# ==============================
# ADMIN DASHBOARD
# ==============================


async def send_admin_dashboard(
    admin_id,
    context
):


    try:

        users = get_user_count()

    except:

        users = 0



    try:

        orders = get_order_count()

    except:

        orders = 0



    try:

        pending = get_pending_count()

    except:

        pending = 0



    try:

        sales = get_total_sales()

    except:

        sales = 0




    text = (

        "👨‍💼 <b>ADMIN PANEL</b>\n"
        "━━━━━━━━━━━━━━\n\n"

        f"👥 Users : {users}\n"
        f"🧾 Orders : {orders}\n"
        f"⏳ Pending : {pending}\n"
        f"💰 Sales : Rs.{sales}\n\n"

        "🔌 Panel\n"
        f"<code>{html_text(PANEL_URL)}</code>"

    )



    keyboard = [


        [

            InlineKeyboardButton(

                "🧾 Pending Orders",

                callback_data="admin_pending"

            )

        ],


        [

            InlineKeyboardButton(

                "📦 Packages",

                callback_data="admin_packages"

            )

        ],



        [

            InlineKeyboardButton(

                "🔌 Test Panel",

                callback_data="panel_test"

            )

        ],



        [

            InlineKeyboardButton(

                "🔄 Refresh",

                callback_data="admin_home"

            )

        ]

    ]




    await context.bot.send_message(

        chat_id=admin_id,

        text=text,

        parse_mode="HTML",

        reply_markup=InlineKeyboardMarkup(
            keyboard
        )

    )




# ==============================
# SHOW PACKAGES
# ==============================


async def show_packages(query):


    try:

        packages = get_packages(True)


    except Exception as e:


        await query.edit_message_text(

            "❌ Package error\n\n"
            f"<code>{html_text(e)}</code>",

            parse_mode="HTML"

        )

        return



    if not packages:


        await query.edit_message_text(

            "❌ No packages available."

        )

        return



    keyboard = []



    for row in packages:


        if len(row) < 8:

            continue



        (

            pid,

            name,

            days,

            price,

            active,

            inbound,

            gb,

            sni

        ) = row[:8]




        keyboard.append(

            [

                InlineKeyboardButton(

                    f"📦 {name} | Rs.{price}",

                    callback_data=f"package_{pid}"

                )

            ]

        )




    keyboard.append(

        [

            InlineKeyboardButton(

                "🏠 Home",

                callback_data="back"

            )

        ]

    )



    await query.edit_message_text(

        "🛒 <b>Select Package</b>",

        parse_mode="HTML",

        reply_markup=InlineKeyboardMarkup(
            keyboard
        )

    )
# ==============================
# CALLBACK HANDLER
# ==============================


async def button_handler(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    query = update.callback_query


    if not query:
        return


    try:

        await query.answer()

    except:

        pass



    user = query.from_user

    data = query.data or ""



    # DEBUG BUTTON DATA

    print(
        "BUTTON DATA:",
        data
    )



    # ==============================
    # ADMIN SECURITY
    # ==============================


    admin_actions = (

        "admin_",
        "panel_",
        "approve_",
        "reject_",
        "pkg_",
        "editpkg_",
        "togglepkg_"

    )


    if data.startswith(admin_actions):


        if not admin_only(user.id):

            await query.answer(

                "⛔ Admin Only",

                show_alert=True

            )

            return




    # ==============================
    # BUY
    # ==============================


    if data == "buy":


        await show_packages(
            query
        )

        return




    # ==============================
    # PACKAGE SELECT
    # ==============================


    if data.startswith(
        "package_"
    ):


        try:

            package_id = int(

                data.split("_")[1]

            )


        except:


            await query.answer(

                "Invalid package",

                show_alert=True

            )

            return




        package = get_package(
            package_id
        )



        if not package:


            await query.edit_message_text(

                "❌ Package not found"

            )

            return



        (

            pid,

            name,

            days,

            price,

            active,

            inbound,

            gb,

            sni

        ) = package[:8]



        try:


            order_id = create_order(

                user.id,

                package_id

            )


        except Exception as e:


            await query.edit_message_text(

                f"❌ Order Error\n\n{e}"

            )

            return




        await query.edit_message_text(


            "🧾 <b>ORDER CREATED</b>\n\n"

            f"🆔 <code>{order_id}</code>\n"

            f"📦 {html_text(name)}\n"

            f"⏱ {days} Days\n"

            f"📊 {gb_text(gb)}\n"

            f"💰 Rs.{price}\n\n"

            "Continue payment:",


            parse_mode="HTML",


            reply_markup=InlineKeyboardMarkup([


                [

                    InlineKeyboardButton(

                        "💳 Payment",

                        callback_data=f"pay_{order_id}"

                    )

                ],


                [

                    InlineKeyboardButton(

                        "🏠 Home",

                        callback_data="back"

                    )

                ]

            ])

        )


        return





    # ==============================
    # PAYMENT
    # ==============================



    if data.startswith(
        "pay_"
    ):


        order_id = data.replace(
            "pay_",
            ""
        )



        order = get_order(
            order_id
        )


        if not order:


            await query.edit_message_text(

                "❌ Order not found"

            )

            return



        context.user_data[

            "payment_order"

        ] = order_id




        await query.edit_message_text(


            "💳 <b>PAYMENT</b>\n\n"

            f"🧾 Order: <code>{order_id}</code>\n"

            f"💰 Amount: Rs.{order[5]}\n\n"


            f"🏦 Bank: {BANK_NAME}\n"

            f"👤 Name: {ACCOUNT_NAME}\n"

            f"🔢 Account: {ACCOUNT_NUMBER}\n"

            f"📍 Branch: {BRANCH}\n\n"


            "Payment slip photo send කරන්න.",



            parse_mode="HTML"

        )


        return





    # ==============================
    # MY CONFIGS
    # ==============================


    if data == "configs":


        configs = get_user_configs(
            user.id
        )


        if not configs:


            await query.edit_message_text(

                "📦 No configs found",

                reply_markup=InlineKeyboardMarkup([

                    [

                    InlineKeyboardButton(

                        "🏠 Home",

                        callback_data="back"

                    )

                    ]

                ])

            )


            return



        text = "📦 <b>MY CONFIGS</b>\n\n"



        for c in configs:


            text += (

                f"<pre>{escape(str(c[1]))}</pre>\n\n"

            )



        await query.edit_message_text(

            text[:4000],

            parse_mode="HTML"

        )


        return





    # ==============================
    # ORDERS
    # ==============================


    if data == "orders":


        orders = get_user_orders(
            user.id
        )


        if not orders:


            await query.edit_message_text(

                "🧾 No orders"

            )

            return



        text = "🧾 <b>ORDERS</b>\n\n"



        for o in orders:


            text += (

                f"🆔 {o[0]}\n"

                f"📦 {o[1]}\n"

                f"📌 {o[4]}\n\n"

            )



        await query.edit_message_text(

            text,

            parse_mode="HTML"

        )


        return





    # ==============================
    # BACK
    # ==============================


    if data == "back":


        await query.edit_message_text(

            "🟢 <b>V2RayX</b>\n\nChoose:",

            parse_mode="HTML",

            reply_markup=main_menu()

        )

        return





    # ==============================
    # UNKNOWN BUTTON FIX
    # ==============================


    await query.answer(

        "⚠️ Button expired. Send /start again.",

        show_alert=True

    )
# ==============================
# PAYMENT PHOTO RECEIVE
# ==============================


async def receive_payment_photo(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    user = update.effective_user

    message = update.message


    if not user or not message:

        return



    order_id = context.user_data.get(
        "payment_order"
    )



    if not order_id:


        await message.reply_text(

            "❌ First select payment order."

        )

        return




    try:


        photo = message.photo[-1]


        save_payment_proof(

            order_id,

            photo.file_id

        )


        update_order_status(

            order_id,

            "PAYMENT_SUBMITTED"

        )


    except Exception as e:


        await message.reply_text(

            f"❌ Upload Error\n{e}"

        )

        return




    await message.reply_text(

        "✅ Payment slip received.\n\n"
        "⏳ Waiting for admin approval."

    )




    # SEND ADMIN ALERT


    try:


        await context.bot.send_photo(


            chat_id=ADMIN_ID,


            photo=photo.file_id,


            caption=(

                "💳 NEW PAYMENT\n\n"

                f"🧾 Order: {order_id}\n"

                f"👤 User: {user.id}"

            ),


            reply_markup=InlineKeyboardMarkup([

                [

                    InlineKeyboardButton(

                        "Approve",

                        callback_data=f"approve_{order_id}"

                    )

                ]

            ])

        )


    except Exception as e:


        print(
            "Admin notify:",
            e
        )




# ==============================
# ADMIN APPROVE
# ==============================


async def approve_order(
    query,
    order_id,
    context
):


    order = get_order(
        order_id
    )


    if not order:


        await query.edit_message_text(

            "❌ Order not found"

        )

        return




    try:


        # CREATE PANEL CLIENT


        success, config = await create_panel_config(

            order_id,

            context

        )



        if success:



            update_order_status(

                order_id,

                "COMPLETED"

            )


            await query.edit_message_text(

                "✅ Order completed\n\n"
                f"🧾 {order_id}"

            )



        else:


            await query.edit_message_text(

                "❌ Config create failed\n\n"

                f"{config}"

            )



    except Exception as e:


        await query.edit_message_text(

            f"❌ Error\n{e}"

        )




# ==============================
# ERROR HANDLER
# ==============================


async def error_handler(
    update,
    context
):

    print(
        "ERROR:",
        context.error
    )

    traceback.print_exc()




# ==============================
# VALIDATE
# ==============================


def validate_settings():


    settings = {


        "BOT_TOKEN": BOT_TOKEN,

        "ADMIN_ID": ADMIN_ID,

        "PANEL_URL": PANEL_URL,

        "PANEL_USERNAME": PANEL_USERNAME,

        "PANEL_PASSWORD": PANEL_PASSWORD


    }



    missing = []


    for k,v in settings.items():

        if not v:

            missing.append(k)



    if missing:


        print(
            "Missing settings:"
        )


        for x in missing:

            print(
                "-",
                x
            )


        return False



    return True





# ==============================
# MAIN TERMUX RUN
# ==============================


def main():


    print(
        "======================"
    )

    print(
        " V2RayX BOT STARTING"
    )

    print(
        "======================"
    )



    if not validate_settings():

        return



    try:


        init_database()


        print(
            "Database OK"
        )


    except Exception as e:


        print(
            "Database Error:",
            e
        )

        return





    app = Application.builder().token(

        BOT_TOKEN

    ).connect_timeout(

        30

    ).read_timeout(

        30

    ).write_timeout(

        30

    ).build()




    # COMMANDS


    app.add_handler(

        CommandHandler(

            "start",

            start

        )

    )


    app.add_handler(

        CommandHandler(

            "id",

            get_id

        )

    )


    app.add_handler(

        CommandHandler(

            "admin",

            admin

        )

    )




    # BUTTONS


    app.add_handler(

        CallbackQueryHandler(

            button_handler

        )

    )



    # PAYMENT PHOTO


    app.add_handler(

        MessageHandler(

            filters.PHOTO,

            receive_payment_photo

        )

    )



    app.add_error_handler(

        error_handler

    )




    print(
        "BOT RUNNING..."
    )



    app.run_polling(

        drop_pending_updates=True

    )





# ==============================
# START
# ==============================


if __name__ == "__main__":

    main()
    
