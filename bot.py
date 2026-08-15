# =========================================================
# V2RayX TELEGRAM BOT
# PART 1/4
# =========================================================

import os
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
# DIRECT BOT SETTINGS
# NO .ENV REQUIRED
# =========================================================


# Telegram Bot Token
# අලුත් token එක මෙතන දාන්න

BOT_TOKEN = "8750154251:AAE_t_mXprxpL77LqK9i24-d9gxifsri-8U"



# Telegram /id command එකෙන් ගන්න Admin ID

ADMIN_ID = 7768611586



# =========================================================
# 3X-UI PANEL SETTINGS
# =========================================================


PANEL_URL = (
    "https://hiru.v2raypoddaserver.ggff.net:11568/siaXP8HNhI9njPbC9Q/"
)


PANEL_USERNAME = (
    "hiru"
)


PANEL_PASSWORD = (
    "hiru"
)


PANEL_API_TOKEN = ""



# =========================================================
# PAYMENT SETTINGS
# =========================================================


BANK_NAME = (
    "People's Bank"
)


ACCOUNT_NAME = (
    "Hirusha Denuwan Gimhana"
)


ACCOUNT_NUMBER = (
    "089200190081987"
)


BRANCH = (
    "Katugasthota"
)



# =========================================================
# SUPPORT
# =========================================================


SUPPORT_USERNAME = (
    "V2ray_podda"
)



# =========================================================
# REFERRAL
# =========================================================


REFERRAL_PERCENTAGE = 5



# =========================================================
# 3X-UI CONNECT
# =========================================================


xui = ThreeXUI(

    PANEL_URL.rstrip("/"),

    PANEL_USERNAME,

    PANEL_PASSWORD,

    PANEL_API_TOKEN,

)



# =========================================================
# HELPERS
# =========================================================


def safe_float(value, default=0.0):

    try:
        return float(value)

    except Exception:
        return default



def safe_int(value, default=0):

    try:
        return int(value)

    except Exception:
        return default



def gb_text(value):

    value = safe_float(value)

    if value <= 0:
        return "Unlimited"

    return f"{value:g} GB"



def admin_only(user_id):

    return safe_int(user_id) == ADMIN_ID



def html_text(value):

    return escape(
        str(value or "")
    )



def url_host(url):

    try:

        return (
            urlparse(url)
            .hostname
            or ""
        )

    except Exception:

        return ""



# =========================================================
# VALIDATE SETTINGS
# =========================================================


def validate_settings():


    missing = []


    if not BOT_TOKEN:
        missing.append(
            "BOT_TOKEN"
        )


    if not ADMIN_ID:
        missing.append(
            "ADMIN_ID"
        )


    if not PANEL_URL:
        missing.append(
            "PANEL_URL"
        )


    if not PANEL_USERNAME:
        missing.append(
            "PANEL_USERNAME"
        )


    if not PANEL_PASSWORD:
        missing.append(
            "PANEL_PASSWORD"
        )



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
# =========================================================
# PART 2/4
# MENU + START + ADMIN SYSTEM
# =========================================================



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
# START COMMAND
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

        f"Welcome "
        f"{html_text(user.first_name)} 👋\n\n"

        "Choose an option:",


        parse_mode="HTML",


        reply_markup=main_menu()

    )





# =========================================================
# GET TELEGRAM ID
# =========================================================


async def get_id(

    update: Update,

    context: ContextTypes.DEFAULT_TYPE

):


    user = update.effective_user


    if not user:
        return



    await update.message.reply_text(


        "🆔 <b>Your Telegram ID</b>\n\n"

        f"<code>{user.id}</code>",


        parse_mode="HTML"

    )






# =========================================================
# ADMIN COMMAND
# =========================================================


async def admin(

    update: Update,

    context: ContextTypes.DEFAULT_TYPE

):


    user = update.effective_user


    if not user:
        return



    if not admin_only(user.id):


        await update.message.reply_text(

            "⛔ Admin only."

        )


        return



    await send_admin_dashboard(

        user.id,

        context

    )







# =========================================================
# ADMIN DASHBOARD
# =========================================================


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

        "👨‍💼 <b>V2RayX ADMIN</b>\n"

        "━━━━━━━━━━━━━━\n\n"


        f"👥 Users : <b>{users}</b>\n"

        f"🧾 Orders : <b>{orders}</b>\n"

        f"⏳ Pending : <b>{pending}</b>\n"

        f"💰 Sales : <b>Rs.{sales:.2f}</b>\n\n"


        "🔌 Panel\n"

        f"<code>{html_text(PANEL_URL)}</code>\n\n"


        "Select option:"

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

                "📡 Panel Inbounds",

                callback_data="panel_inbounds"

            )

        ],



        [

            InlineKeyboardButton(

                "🔌 Test Panel",

                callback_data="panel_test"

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
# SHOW PACKAGES
# =========================================================


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


                f"📦 {name} | {duration}D | "

                f"{gb_text(traffic_gb)} | "

                f"Rs.{price}",


                callback_data=

                f"package_{package_id}"

            )


        ])




    keyboard.append([


        InlineKeyboardButton(

            "🔙 Back",

            callback_data="back"

        )

    ])





    await query.edit_message_text(


        "🛒 <b>SELECT PACKAGE</b>",


        parse_mode="HTML",


        reply_markup=InlineKeyboardMarkup(

            keyboard

        )

    )

# =========================================================
# PART 3/4
# ORDER + PAYMENT + 3X-UI CONFIG
# =========================================================


# =========================================================
# CREATE PANEL CONFIG
# =========================================================


async def create_panel_config(
    order_id,
    context
):


    order = get_order(order_id)


    if not order:

        return False, "Order not found"



    if len(order) < 15:

        return False, "Invalid order data"



    (

        db_order_id,
        user_id,
        package_id,
        package_name,
        duration,
        price,
        status,
        inbound_id,
        traffic_gb,
        sni,
        payment_proof,
        old_config,
        old_expiry,
        created_at,
        updated_at

    ) = order[:15]



    user_id = safe_int(user_id)

    duration = safe_int(duration)

    inbound_id = safe_int(inbound_id)

    traffic_gb = safe_float(traffic_gb)




    # LOGIN PANEL

    try:

        ok, msg = xui.login()


    except Exception as e:

        return False, str(e)



    if not ok:

        return False, msg




    # GET INBOUND

    try:

        inbound = xui.get_inbound(
            inbound_id
        )


    except Exception as e:

        return False, str(e)



    if not inbound:

        return False, "Inbound not found"





    # EXPIRY

    expiry = (

        datetime.now()

        +

        timedelta(
            days=duration
        )

    )



    expiry_ms = int(

        expiry.timestamp()

        *

        1000

    )



    expiry_text = expiry.strftime(

        "%Y-%m-%d %H:%M"

    )





    email = (

        f"vp_{user_id}_{order_id}"

        .replace("-","_")

        .lower()

    )





    # CREATE CLIENT


    try:


        success, result = xui.create_client(


            inbound_id=inbound_id,


            email=email,


            expiry_ms=expiry_ms,


            traffic_gb=traffic_gb,


            telegram_id=user_id

        )


    except Exception as e:


        return False, str(e)




    if not success:


        return False, str(result)





    await asyncio.sleep(1)





    links=[]



    try:


        ok,data = xui.get_client_links(
            email
        )


        if ok:

            links = extract_links(data)



    except Exception:

        pass





    # UUID FALLBACK


    client_uuid=None



    if isinstance(result,dict):


        client_uuid = (

            result.get("uuid")

            or

            result.get("id")

        )






    # VLESS FALLBACK


    if not links and client_uuid:


        host=url_host(PANEL_URL)


        port=inbound.get("port")



        if host and port:


            config=(


                f"vless://"

                f"{client_uuid}@"

                f"{host}:{port}"

                f"#{package_name}"

            )


            links.append(config)







    if not links:


        return False,"Config generate failed"





    final_config="\n\n".join(links)





    try:


        final_config = apply_sni(

            final_config,

            sni

        )


    except Exception:

        pass





    save_config(

        order_id,

        final_config,

        expiry_text

    )


    update_order_status(

        order_id,

        "COMPLETED"

    )





    # SEND USER CONFIG


    await context.bot.send_message(


        chat_id=user_id,


        text=(


            "🎉 <b>CONFIG READY</b>\n\n"

            f"📦 {package_name}\n"

            f"📅 Expire: {expiry_text}\n\n"

            "<pre>"

            f"{escape(final_config)}"

            "</pre>"

        ),


        parse_mode="HTML"

    )




    return True, final_config







# =========================================================
# CALLBACK BUY SYSTEM
# =========================================================


async def create_order_callback(

    query,

    user

):


    package_id = int(

        query.data.split("_")[1]

    )



    package=get_package(
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

        duration,

        price,

        active,

        inbound_id,

        traffic_gb,

        sni

    )=package[:8]






    order=create_order(

        user.id,

        package_id

    )





    order_id = str(order)




    await query.edit_message_text(


        "🧾 <b>ORDER CREATED</b>\n\n"

        f"🆔 <code>{order_id}</code>\n"

        f"📦 {name}\n"

        f"💰 Rs.{price}\n\n"

        "Continue payment:",


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









# =========================================================
# PAYMENT PAGE
# =========================================================


async def payment_page(

    query,

    order_id,

    user

):


    order=get_order(order_id)



    if not order:


        await query.edit_message_text(

            "❌ Order missing"

        )

        return





    await query.edit_message_text(



        "💳 <b>PAYMENT DETAILS</b>\n\n"

        f"🧾 Order : <code>{order_id}</code>\n\n"

        f"🏦 Bank : {BANK_NAME}\n"

        f"👤 Name : {ACCOUNT_NAME}\n"

        f"🔢 Account : {ACCOUNT_NUMBER}\n"

        f"📍 Branch : {BRANCH}\n\n"

        "Payment කරලා receipt photo එක upload කරන්න.",



        parse_mode="HTML"

    )





    query.message.chat_data[

        "payment_order"

    ] = order_id
# =========================================================
# PART 4/4
# HANDLERS + MAIN
# =========================================================



# =========================================================
# PHOTO PAYMENT RECEIVER
# =========================================================


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



        await message.reply_text(

            "✅ Payment slip received.\n"
            "⏳ Waiting admin approval."

        )



        await context.bot.send_photo(


            chat_id=ADMIN_ID,


            photo=photo.file_id,


            caption=(

                "💳 NEW PAYMENT\n\n"

                f"Order : {order_id}\n"

                f"User : {user.id}"

            )

        )


    except Exception as e:


        await message.reply_text(

            f"❌ Error: {e}"

        )







# =========================================================
# BUTTON HANDLER
# =========================================================


async def button_handler(

    update: Update,

    context: ContextTypes.DEFAULT_TYPE

):


    query = update.callback_query


    if not query:

        return



    await query.answer()



    user=query.from_user

    data=query.data





    # BUY


    if data=="buy":


        await show_packages(query)

        return






    # PACKAGE SELECT


    if data.startswith("package_"):


        await create_order_callback(

            query,

            user

        )

        return






    # PAYMENT


    if data.startswith("pay_"):


        order_id=data.replace(

            "pay_",

            ""

        )


        context.user_data[

            "payment_order"

        ]=order_id



        await payment_page(

            query,

            order_id,

            user

        )


        return






    # CONFIGS


    if data=="configs":


        configs=get_user_configs(

            user.id

        )



        if not configs:


            await query.edit_message_text(

                "📦 No configs."

            )

            return




        text="📦 MY CONFIGS\n\n"



        for c in configs:


            text += (

                f"<pre>{escape(str(c))}</pre>\n"

            )



        await query.edit_message_text(

            text,

            parse_mode="HTML"

        )


        return






    # ADMIN HOME


    if data=="admin_home":


        await send_admin_dashboard(

            user.id,

            context

        )


        return







    # ADMIN PENDING


    if data=="admin_pending":


        orders=get_pending_orders()



        if not orders:


            await query.edit_message_text(

                "No pending orders."

            )

            return





        keyboard=[]



        for row in orders:


            keyboard.append([


                InlineKeyboardButton(

                    f"{row[0]} | {row[3]}",


                    callback_data=

                    f"admin_order_{row[0]}"

                )


            ])





        await query.edit_message_text(


            "🧾 Pending Orders",


            reply_markup=InlineKeyboardMarkup(

                keyboard

            )

        )


        return







    # ADMIN ORDER VIEW


    if data.startswith("admin_order_"):


        order_id=data.replace(

            "admin_order_",

            ""

        )



        await query.edit_message_text(


            f"🧾 Order\n\n"

            f"ID: {order_id}",



            reply_markup=InlineKeyboardMarkup([


                [


                    InlineKeyboardButton(

                        "✅ Approve",

                        callback_data=

                        f"approve_{order_id}"

                    )


                ],


                [


                    InlineKeyboardButton(

                        "❌ Reject",

                        callback_data=

                        f"reject_{order_id}"

                    )


                ]


            ])

        )



        return






    # APPROVE


    if data.startswith("approve_"):


        order_id=data.replace(

            "approve_",

            ""

        )


        await query.edit_message_text(

            "⏳ Creating config..."

        )



        ok,result = await create_panel_config(

            order_id,

            context

        )



        if ok:


            await query.edit_message_text(

                "✅ Config created."

            )


        else:


            await query.edit_message_text(

                f"❌ Error\n{result}"

            )



        return





    # REJECT


    if data.startswith("reject_"):


        order_id=data.replace(

            "reject_",

            ""

        )


        update_order_status(

            order_id,

            "REJECTED"

        )


        await query.edit_message_text(

            "❌ Order rejected."

        )


        return





    # BACK


    if data=="back":


        await query.edit_message_text(


            "🟢 V2RayX",

            reply_markup=main_menu()

        )









# =========================================================
# ERROR HANDLER
# =========================================================


async def error_handler(

    update,

    context

):


    print(

        "ERROR:",

        context.error

    )







# =========================================================
# MAIN
# =========================================================


def main():


    print(

        "Starting V2RayX Bot..."

    )



    if not validate_settings():

        return





    init_database()





    app=(

        Application

        .builder()

        .token(BOT_TOKEN)

        .build()

    )





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

        CallbackQueryHandler(

            button_handler

        )

    )



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





    app.run_polling()







# =========================================================
# START
# =========================================================


if __name__=="__main__":

    main()
