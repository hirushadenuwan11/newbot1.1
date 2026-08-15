# =========================================================
# V2RayX Telegram Bot
# Part 1/3
# ENV + CONFIG.JSON SYSTEM
# =========================================================

import os
import json
import asyncio
import traceback

from datetime import datetime, timedelta
from html import escape
from urllib.parse import urlparse


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


from dotenv import load_dotenv


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



# =========================================================
# CONFIG SYSTEM
# =========================================================


load_dotenv()


CONFIG_FILE = "config.json"


def load_config():

    if os.path.exists(CONFIG_FILE):

        try:

            with open(
                CONFIG_FILE,
                "r",
                encoding="utf-8"
            ) as f:

                return json.load(f)

        except Exception:

            return {}

    return {}



def save_config(data):

    with open(
        CONFIG_FILE,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            data,
            f,
            indent=4,
            ensure_ascii=False
        )



CONFIG = load_config()



def env(name, default=""):

    # Priority:
    # 1. Telegram setup config
    # 2. .env file
    # 3. default value


    if name in CONFIG:

        return str(
            CONFIG[name]
        ).strip()



    value = os.getenv(
        name,
        default
    )


    return str(
        value or ""
    ).strip()



# =========================================================
# SETTINGS
# =========================================================


BOT_TOKEN = env(
    "BOT_TOKEN"
)


ADMIN_ID = int(
    env(
        "ADMIN_ID",
        "0"
    )
    or 0
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
    "YOUR BRANCH"
)



SUPPORT_USERNAME = env(
    "SUPPORT_USERNAME",
    "v2ray_podda"
)



REFERRAL_PERCENTAGE = int(
    env(
        "REFERRAL_PERCENTAGE",
        "5"
    )
    or 5
)




# =========================================================
# 3X-UI CONNECT
# =========================================================


xui = ThreeXUI(

    PANEL_URL,

    PANEL_USERNAME,

    PANEL_PASSWORD,

    PANEL_API_TOKEN

)



# =========================================================
# HELPERS
# =========================================================


def safe_int(
    value,
    default=0
):

    try:

        return int(value)

    except:

        return default



def safe_float(
    value,
    default=0.0
):

    try:

        return float(value)

    except:

        return default



def html_text(value):

    return escape(
        str(
            value or ""
        )
    )



def gb_text(value):

    value = safe_float(value)


    if value <= 0:

        return "Unlimited"


    return f"{value:g} GB"




def admin_only(
    user_id
):

    return (
        safe_int(user_id)
        ==
        ADMIN_ID
    )



def url_host(url):

    try:

        return urlparse(
            url
        ).hostname or ""

    except:

        return ""



# =========================================================
# MAIN MENU
# =========================================================


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
                "🧾 My Orders",
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




# =========================================================
# /SETUP COMMAND
# =========================================================


async def setup(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):


    user = update.effective_user


    if not admin_only(
        user.id
    ):


        await update.message.reply_text(
            "⛔ Admin only"
        )

        return



    if len(
        context.args
    ) < 2:


        await update.message.reply_text(

"""
⚙️ CONFIG SETUP


Use:

/setup KEY VALUE


Example:


/setup BOT_TOKEN token_here


/setup ADMIN_ID 123456


/setup PANEL_URL https://panel.com


/setup PANEL_USERNAME admin


/setup PANEL_PASSWORD password


/setup BANK_NAME PeoplesBank

"""

        )

        return




    key = context.args[0]


    value = " ".join(
        context.args[1:]
    )



    CONFIG[key] = value


    save_config(
        CONFIG
    )



    await update.message.reply_text(

f"""
✅ Saved

KEY:
{key}

VALUE:
{value}


Restart bot.
"""

    )




# =========================================================
# /START
# =========================================================


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
            "save user error:",
            e
        )




    await update.message.reply_text(


f"""
🟢 <b>V2RayX</b>


Welcome,
{html_text(user.first_name)} 👋


Choose option:

""",


        parse_mode="HTML",

        reply_markup=main_menu()

    )



# =========================================================
# /ID
# =========================================================


async def get_id(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):


    user = update.effective_user


    await update.message.reply_text(

f"""
🆔 Telegram ID

<code>{user.id}</code>
""",

        parse_mode="HTML"

    )
# =========================================================
# ADMIN DASHBOARD
# =========================================================


async def admin(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    user = update.effective_user


    if not admin_only(
        user.id
    ):

        await update.message.reply_text(
            "⛔ Admin only"
        )

        return


    await send_admin_dashboard(
        user.id,
        context
    )




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



    text = f"""

👨‍💼 <b>V2RayX ADMIN</b>

━━━━━━━━━━━━━━

👥 Users:
<b>{users}</b>

🧾 Orders:
<b>{orders}</b>

⏳ Pending:
<b>{pending}</b>

💰 Sales:
<b>Rs.{sales}</b>


🔌 PANEL

<code>{html_text(PANEL_URL)}</code>


Select option:

"""


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
                "📡 Inbounds",
                callback_data="panel_inbounds"
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





# =========================================================
# PACKAGE VIEW
# =========================================================


async def show_packages(query):


    try:

        packages = get_packages(True)


    except Exception as e:


        await query.edit_message_text(

            f"❌ Error\n\n{e}"

        )

        return



    if not packages:


        await query.edit_message_text(

            "❌ No packages available."

        )

        return



    keyboard=[]



    for row in packages:


        if len(row)<8:
            continue



        (

            package_id,

            name,

            duration,

            price,

            active,

            inbound_id,

            traffic_gb,

            sni

        ) = row[:8]



        keyboard.append([


            InlineKeyboardButton(

                f"📦 {name} | "
                f"{duration}D | "
                f"Rs.{price}",

                callback_data=
                f"package_{package_id}"

            )


        ])




    await query.edit_message_text(

        "🛒 Select Package",

        reply_markup=InlineKeyboardMarkup(
            keyboard
        )

    )





# =========================================================
# EXTRACT CONFIG LINKS
# =========================================================


def extract_links(data):


    result=[]



    if not data:

        return result



    if isinstance(
        data,
        str
    ):


        if data.startswith(
            (
                "vless://",
                "vmess://",
                "trojan://"
            )
        ):

            result.append(data)


        return result



    if isinstance(
        data,
        list
    ):


        for x in data:

            result.extend(
                extract_links(x)
            )


    if isinstance(
        data,
        dict
    ):


        for x in data.values():

            result.extend(
                extract_links(x)
            )


    return result





# =========================================================
# CREATE 3X-UI CLIENT
# =========================================================


async def create_panel_config(

    order_id,

    context

):


    order = get_order(
        order_id
    )


    if not order:

        return False,"Order missing"



    user_id = safe_int(
        order[1]
    )


    package_name = order[3]


    duration = safe_int(
        order[4]
    )


    inbound_id = safe_int(
        order[7]
    )


    traffic = safe_float(
        order[8]
    )


    sni = order[9]



    # LOGIN PANEL

    try:

        ok,msg=xui.login()


    except Exception as e:

        return False,str(e)



    if not ok:

        return False,msg




    expiry = (

        datetime.now()

        +

        timedelta(
            days=duration
        )

    )



    expiry_ms=int(

        expiry.timestamp()

        *

        1000

    )



    email = (

        f"vp_{user_id}_{order_id}"

    )




    try:


        success,result=xui.create_client(

            inbound_id=inbound_id,

            email=email,

            expiry_ms=expiry_ms,

            traffic_gb=traffic,

            telegram_id=user_id

        )


    except Exception as e:

        return False,str(e)




    if not success:

        return False,str(result)




    links=[]



    try:

        ok,data=xui.get_client_links(
            email
        )


        if ok:

            links=extract_links(
                data
            )


    except:

        pass




    if not links:

        return False,"Config link not found"




    final=[]



    for link in links:


        try:

            link=apply_sni(
                link,
                sni
            )

        except:

            pass



        final.append(link)




    config="\n\n".join(
        final
    )



    expiry_text=expiry.strftime(
        "%Y-%m-%d %H:%M"
    )



    save_config(

        order_id,

        config,

        expiry_text

    )


    update_order_status(

        order_id,

        "COMPLETED"

    )




    try:


        await context.bot.send_message(

            chat_id=user_id,


            text=f"""

🎉 <b>CONFIG READY</b>


📦 {package_name}

📅 Expire:
<code>{expiry_text}</code>


<pre>{escape(config)}</pre>

""",

            parse_mode="HTML"

        )


    except Exception:

        pass




    return True,config
# =========================================================
# CALLBACK HANDLER
# =========================================================


async def button_handler(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    query = update.callback_query

    if not query:
        return


    await query.answer()


    user = query.from_user

    data = query.data



    # BUY

    if data == "buy":

        await show_packages(
            query
        )

        return



    # PACKAGE SELECT

    if data.startswith(
        "package_"
    ):


        package_id = int(
            data.split("_")[1]
        )


        package = get_package(
            package_id
        )


        if not package:

            await query.edit_message_text(
                "❌ Package not found"
            )

            return



        order = create_order(

            user.id,

            package_id

        )


        order_id = order



        await query.edit_message_text(

f"""
🧾 <b>ORDER CREATED</b>


🆔 <code>{order_id}</code>

📦 {package[1]}

💰 Rs.{package[3]}


Payment කරන්න.

""",

parse_mode="HTML",

reply_markup=InlineKeyboardMarkup([

[

InlineKeyboardButton(

"💳 Payment",

callback_data=f"pay_{order_id}"

)

]

])

)

        return





    # PAYMENT

    if data.startswith(
        "pay_"
    ):


        order_id=data.replace(
            "pay_",
            ""
        )


        context.user_data[
            "payment_order"
        ] = order_id



        await query.edit_message_text(

f"""

💳 <b>PAYMENT</b>


Order:

<code>{order_id}</code>


🏦 Bank:
{BANK_NAME}


👤 Name:
{ACCOUNT_NAME}


🔢 Account:
<code>{ACCOUNT_NUMBER}</code>


📍 Branch:
{BRANCH}


Payment slip photo එක send කරන්න.

""",

parse_mode="HTML"

)

        return




    # MY CONFIGS


    if data=="configs":


        configs=get_user_configs(
            user.id
        )


        if not configs:

            await query.edit_message_text(
                "📦 No configs"
            )

            return



        text="📦 MY CONFIGS\n\n"


        for c in configs:


            text += (

                f"<pre>{escape(str(c))}</pre>\n\n"

            )



        await query.edit_message_text(

            text,

            parse_mode="HTML"

        )


        return




    # ADMIN PANEL


    if data=="admin_pending":


        if not admin_only(
            user.id
        ):

            return



        orders=get_pending_orders()



        if not orders:


            await query.edit_message_text(
                "No pending orders"
            )

            return



        keyboard=[]



        for o in orders:


            keyboard.append([

                InlineKeyboardButton(

                    f"{o[0]} | Rs.{o[4]}",

                    callback_data=
                    f"admin_order_{o[0]}"

                )

            ])




        await query.edit_message_text(

            "🧾 Pending Orders",

            reply_markup=InlineKeyboardMarkup(
                keyboard
            )

        )

        return






    # APPROVE


    if data.startswith(
        "approve_"
    ):


        if not admin_only(
            user.id
        ):

            return



        order_id=data.replace(
            "approve_",
            ""
        )



        await query.edit_message_text(

            "⏳ Creating config..."

        )



        ok,result=await create_panel_config(

            order_id,

            context

        )



        if ok:


            await query.edit_message_text(

                "✅ Config Created"

            )

        else:


            await query.edit_message_text(

                f"❌ Error\n{result}"

            )



        return







    # REJECT


    if data.startswith(
        "reject_"
    ):


        order_id=data.replace(
            "reject_",
            ""
        )


        update_order_status(

            order_id,

            "REJECTED"

        )


        await query.edit_message_text(

            "❌ Order rejected"

        )


        return





# =========================================================
# PAYMENT PHOTO
# =========================================================


async def receive_payment_photo(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):


    user=update.effective_user


    order_id=context.user_data.get(
        "payment_order"
    )



    if not order_id:


        await update.message.reply_text(

            "❌ First select payment"

        )

        return




    photo=update.message.photo[-1]



    save_payment_proof(

        order_id,

        photo.file_id

    )


    update_order_status(

        order_id,

        "PAYMENT_SUBMITTED"

    )



    await update.message.reply_text(

        "✅ Payment slip received\nWaiting admin approval"

    )



    try:


        await context.bot.send_photo(

            chat_id=ADMIN_ID,

            photo=photo.file_id,

            caption=f"""

💳 New Payment


Order:
{order_id}


User:
{user.id}

"""

        )


    except:

        pass





# =========================================================
# VALIDATE
# =========================================================


def validate_settings():


    required=[

        BOT_TOKEN,

        ADMIN_ID,

        PANEL_URL,

        PANEL_USERNAME,

        PANEL_PASSWORD

    ]


    return all(required)





# =========================================================
# MAIN
# =========================================================


def main():



    print(
        "Starting V2RayX Bot..."
    )



    if not validate_settings():

        print(
            "Missing settings"
        )

        return




    init_database()




    app = (

        Application

        .builder()

        .token(
            BOT_TOKEN
        )

        .build()

    )




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


    app.add_handler(

        CommandHandler(
            "setup",
            setup
        )

    )



    # BUTTONS


    app.add_handler(

        CallbackQueryHandler(
            button_handler
        )

    )



    # PHOTO


    app.add_handler(

        MessageHandler(

            filters.PHOTO,

            receive_payment_photo

        )

    )



    print(
        "BOT RUNNING..."
    )



    app.run_polling(
        drop_pending_updates=True
    )





# =========================================================
# RUN
# =========================================================


if __name__=="__main__":

    main()