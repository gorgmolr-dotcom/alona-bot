"""
بوت حماية تيليجرام - Arabic Telegram Protection Bot
المطور: أحمد الجمال @Ahmedjammal1988
المكتبة: python-telegram-bot v20.3
"""

import logging
import asyncio
import os
import re
from telegram import Update, ChatPermissions
from telegram.ext import (
    Application, MessageHandler,
    filters, ContextTypes
)
from telegram.error import BadRequest

# ===================== الإعدادات =====================
BOT_TOKEN = os.environ.get("BOT_TOKEN", "")

# معرف المطور - صاحب البوت (صلاحيات كاملة في كل الجروبات)
# ⚠️ غيّر هذا الرقم لمعرفك الحقيقي على تيليجرام
# احصل على معرفك من @userinfobot
DEVELOPER_ID = 0  # ضع معرفك هنا
DEVELOPER_USERNAME = "Ahmedjammal1988"

# قاعدة بيانات في الذاكرة
group_settings = {}
admins = {}
vip_users = {}

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# ===================== دوال مساعدة =====================

def get_group_settings(chat_id):
    if chat_id not in group_settings:
        group_settings[chat_id] = {
            "active": False,
            "lock_links": False,
            "lock_forward": False,
            "lock_usernames": False,
            "lock_photos": False,
            "lock_videos": False,
            "lock_stickers": False,
        }
    return group_settings[chat_id]

async def is_developer(user_id):
    return DEVELOPER_ID != 0 and user_id == DEVELOPER_ID

async def is_group_admin(update, context, user_id=None):
    chat_id = update.effective_chat.id
    uid = user_id or update.effective_user.id
    if DEVELOPER_ID != 0 and uid == DEVELOPER_ID:
        return True
    try:
        member = await context.bot.get_chat_member(chat_id, uid)
        return member.status in ["administrator", "creator"]
    except:
        return False

async def check_permission(update, context):
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id
    if await is_developer(user_id):
        return True
    if await is_group_admin(update, context, user_id):
        return True
    if user_id in admins.get(chat_id, set()):
        return True
    await update.message.reply_text("❌ ليس لديك صلاحية لاستخدام هذا الأمر.")
    return False

# ===================== أوامر التشغيل =====================

async def cmd_activate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    if chat.type == "private":
        await update.message.reply_text("⚠️ هذا الأمر يعمل في المجموعات فقط.")
        return
    if not await check_permission(update, context):
        return
    get_group_settings(chat.id)["active"] = True
    await update.message.reply_text(
        "✅ *تم تفعيل البوت بنجاح!*\n"
        "اكتب `الاوامر` لعرض قائمة الأوامر الكاملة.\n\n"
        "🛡️ _بوت الحماية — تطوير @Ahmedjammal1988_",
        parse_mode="Markdown"
    )

async def cmd_deactivate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_permission(update, context):
        return
    get_group_settings(update.effective_chat.id)["active"] = False
    await update.message.reply_text("🔴 تم تعطيل البوت. اكتب `تفعيل` لإعادة تشغيله.", parse_mode="Markdown")

async def cmd_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = """
🛡️ *بوت الحماية — قائمة الأوامر*
_تطوير: @Ahmedjammal1988_

━━━━━━━━━━━━━━━━━
⚙️ *أوامر التشغيل*
━━━━━━━━━━━━━━━━━
`تفعيل` — تشغيل البوت
`تعطيل` — إيقاف البوت
`الاوامر` — عرض هذه القائمة

━━━━━━━━━━━━━━━━━
🔒 *أوامر الحماية والقفل*
━━━━━━━━━━━━━━━━━
`قفل الروابط` / `فتح الروابط`
`قفل التوجيه` / `فتح التوجيه`
`قفل المعرفات` / `فتح المعرفات`
`قفل الصور` / `فتح الصور`
`قفل الفيديو` / `فتح الفيديو`
`قفل الملصقات` / `فتح الملصقات`

━━━━━━━━━━━━━━━━━
👥 *إدارة الأعضاء* _(رد على رسالة العضو)_
━━━━━━━━━━━━━━━━━
`كتم` — منع من الكتابة
`الغاء كتم` — السماح بالكتابة
`حظر` — حظر العضو نهائياً
`الغاء حظر` — فك الحظر
`طرد` — إخراج العضو فقط

━━━━━━━━━━━━━━━━━
🏅 *الرتب والصلاحيات*
━━━━━━━━━━━━━━━━━
`رفع ادمن` — ترقية لمشرف بوت
`تنزيل ادمن` — سحب الإشراف
`رفع مميز` — استثناء من القيود
`تنزيل مميز` — إلغاء الاستثناء

━━━━━━━━━━━━━━━━━
🧹 *مسح الشات*
━━━━━━━━━━━━━━━━━
`مسح` — مسح من نقطة الرد حتى الآن
`مسح كل` — مسح آخر 100 رسالة
`مسح 50` — مسح عدد محدد
`مسح عضو` — مسح رسائل عضو معين

━━━━━━━━━━━━━━━━━
👑 *أوامر المطور فقط*
━━━━━━━━━━━━━━━━━
`معلومات البوت` — إحصائيات البوت
`جروباتي` — عدد الجروبات النشطة

━━━━━━━━━━━━━━━━━
💡 تأكد من رفع البوت كـ *مشرف* بصلاحيات كاملة
    """
    await update.message.reply_text(help_text, parse_mode="Markdown")

# ===================== أوامر القفل =====================

async def handle_lock_unlock(update, context, key, lock, label):
    if not await check_permission(update, context):
        return
    get_group_settings(update.effective_chat.id)[key] = lock
    icon = "🔒" if lock else "🔓"
    status = "تم قفل" if lock else "تم فتح"
    await update.message.reply_text(f"{icon} {status} *{label}* في هذه المجموعة.", parse_mode="Markdown")

# ===================== إدارة الأعضاء =====================

async def cmd_mute(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_permission(update, context):
        return
    if not update.message.reply_to_message:
        await update.message.reply_text("⚠️ الرجاء الرد على رسالة العضو المراد كتمه.")
        return
    target = update.message.reply_to_message.from_user
    try:
        await context.bot.restrict_chat_member(
            update.effective_chat.id, target.id,
            permissions=ChatPermissions(can_send_messages=False)
        )
        await update.message.reply_text(
            f"🔇 تم كتم [{target.first_name}](tg://user?id={target.id})\n_بواسطة {update.effective_user.first_name}_",
            parse_mode="Markdown"
        )
    except Exception as e:
        await update.message.reply_text(f"❌ فشل الكتم: {e}")

async def cmd_unmute(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_permission(update, context):
        return
    if not update.message.reply_to_message:
        await update.message.reply_text("⚠️ الرجاء الرد على رسالة العضو.")
        return
    target = update.message.reply_to_message.from_user
    try:
        await context.bot.restrict_chat_member(
            update.effective_chat.id, target.id,
            permissions=ChatPermissions(
                can_send_messages=True,
                can_send_media_messages=True,
                can_send_other_messages=True,
                can_add_web_page_previews=True
            )
        )
        await update.message.reply_text(
            f"🔊 تم فك كتم [{target.first_name}](tg://user?id={target.id})",
            parse_mode="Markdown"
        )
    except Exception as e:
        await update.message.reply_text(f"❌ فشل فك الكتم: {e}")

async def cmd_ban(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_permission(update, context):
        return
    if not update.message.reply_to_message:
        await update.message.reply_text("⚠️ الرجاء الرد على رسالة العضو المراد حظره.")
        return
    target = update.message.reply_to_message.from_user
    try:
        await context.bot.ban_chat_member(update.effective_chat.id, target.id)
        await update.message.reply_text(
            f"🚫 تم حظر [{target.first_name}](tg://user?id={target.id})\n_بواسطة {update.effective_user.first_name}_",
            parse_mode="Markdown"
        )
    except Exception as e:
        await update.message.reply_text(f"❌ فشل الحظر: {e}")

async def cmd_unban(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_permission(update, context):
        return
    target_user = None
    if update.message.reply_to_message:
        target_user = update.message.reply_to_message.from_user
    elif context.args:
        try:
            target_user = await context.bot.get_chat(context.args[0].replace("@", ""))
        except:
            await update.message.reply_text("❌ لم يتم العثور على المستخدم.")
            return
    if not target_user:
        await update.message.reply_text("⚠️ الرجاء الرد على رسالة العضو أو كتابة @يوزر.")
        return
    try:
        await context.bot.unban_chat_member(update.effective_chat.id, target_user.id)
        await update.message.reply_text(
            f"✅ تم فك حظر [{target_user.first_name}](tg://user?id={target_user.id})",
            parse_mode="Markdown"
        )
    except Exception as e:
        await update.message.reply_text(f"❌ فشل فك الحظر: {e}")

async def cmd_kick(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_permission(update, context):
        return
    if not update.message.reply_to_message:
        await update.message.reply_text("⚠️ الرجاء الرد على رسالة العضو المراد طرده.")
        return
    target = update.message.reply_to_message.from_user
    try:
        await context.bot.ban_chat_member(update.effective_chat.id, target.id)
        await context.bot.unban_chat_member(update.effective_chat.id, target.id)
        await update.message.reply_text(
            f"👢 تم طرد [{target.first_name}](tg://user?id={target.id})\n_بواسطة {update.effective_user.first_name}_",
            parse_mode="Markdown"
        )
    except Exception as e:
        await update.message.reply_text(f"❌ فشل الطرد: {e}")

# ===================== الرتب =====================

async def cmd_promote_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_group_admin(update, context):
        await update.message.reply_text("❌ هذا الأمر لمشرفي الجروب فقط.")
        return
    if not update.message.reply_to_message:
        await update.message.reply_text("⚠️ الرجاء الرد على رسالة العضو.")
        return
    chat_id = update.effective_chat.id
    target = update.message.reply_to_message.from_user
    if chat_id not in admins:
        admins[chat_id] = set()
    admins[chat_id].add(target.id)
    await update.message.reply_text(
        f"⭐ تمت ترقية [{target.first_name}](tg://user?id={target.id}) كمشرف بوت.",
        parse_mode="Markdown"
    )

async def cmd_demote_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_group_admin(update, context):
        await update.message.reply_text("❌ هذا الأمر لمشرفي الجروب فقط.")
        return
    if not update.message.reply_to_message:
        await update.message.reply_text("⚠️ الرجاء الرد على رسالة العضو.")
        return
    target = update.message.reply_to_message.from_user
    admins.get(update.effective_chat.id, set()).discard(target.id)
    await update.message.reply_text(
        f"🔽 تم سحب صلاحيات [{target.first_name}](tg://user?id={target.id})",
        parse_mode="Markdown"
    )

async def cmd_promote_vip(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_permission(update, context):
        return
    if not update.message.reply_to_message:
        await update.message.reply_text("⚠️ الرجاء الرد على رسالة العضو.")
        return
    chat_id = update.effective_chat.id
    target = update.message.reply_to_message.from_user
    if chat_id not in vip_users:
        vip_users[chat_id] = set()
    vip_users[chat_id].add(target.id)
    await update.message.reply_text(
        f"💎 [{target.first_name}](tg://user?id={target.id}) أصبح عضواً مميزاً ومستثنى من القيود.",
        parse_mode="Markdown"
    )

async def cmd_demote_vip(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_permission(update, context):
        return
    if not update.message.reply_to_message:
        await update.message.reply_text("⚠️ الرجاء الرد على رسالة العضو.")
        return
    target = update.message.reply_to_message.from_user
    vip_users.get(update.effective_chat.id, set()).discard(target.id)
    await update.message.reply_text(
        f"🔽 تم إلغاء تميز [{target.first_name}](tg://user?id={target.id})",
        parse_mode="Markdown"
    )

# ===================== مسح الشات (مصلّح) =====================

async def cmd_purge(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_permission(update, context):
        return
    if not update.message.reply_to_message:
        await update.message.reply_text("⚠️ الرجاء الرد على الرسالة التي تريد المسح منها.")
        return
    chat_id = update.effective_chat.id
    from_id = update.message.reply_to_message.message_id
    to_id = update.message.message_id
    status_msg = await update.message.reply_text("🧹 جاري المسح...")
    deleted = 0
    for msg_id in range(from_id, to_id + 1):
        try:
            await context.bot.delete_message(chat_id, msg_id)
            deleted += 1
        except:
            pass
        await asyncio.sleep(0.05)
    try:
        await status_msg.delete()
    except:
        pass
    confirm = await context.bot.send_message(chat_id, f"✅ تم مسح *{deleted}* رسالة.", parse_mode="Markdown")
    await asyncio.sleep(4)
    try:
        await confirm.delete()
    except:
        pass

async def cmd_purge_count(update: Update, context: ContextTypes.DEFAULT_TYPE, count: int = 100):
    if not await check_permission(update, context):
        return
    count = min(count, 500)
    chat_id = update.effective_chat.id
    to_id = update.message.message_id
    from_id = max(1, to_id - count)
    status_msg = await update.message.reply_text(f"🧹 جاري مسح آخر {count} رسالة...")
    deleted = 0
    for msg_id in range(from_id, to_id + 1):
        try:
            await context.bot.delete_message(chat_id, msg_id)
            deleted += 1
        except:
            pass
        await asyncio.sleep(0.05)
    try:
        await status_msg.delete()
    except:
        pass
    confirm = await context.bot.send_message(chat_id, f"✅ تم مسح *{deleted}* رسالة.", parse_mode="Markdown")
    await asyncio.sleep(4)
    try:
        await confirm.delete()
    except:
        pass

async def cmd_purge_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_permission(update, context):
        return
    if not update.message.reply_to_message:
        await update.message.reply_text("⚠️ الرجاء الرد على رسالة العضو المراد مسح رسائله.")
        return
    target = update.message.reply_to_message.from_user
    chat_id = update.effective_chat.id
    from_id = update.message.reply_to_message.message_id
    to_id = update.message.message_id
    status_msg = await update.message.reply_text(
        f"🧹 جاري مسح رسائل [{target.first_name}](tg://user?id={target.id})...",
        parse_mode="Markdown"
    )
    deleted = 0
    for msg_id in range(from_id, to_id + 1):
        try:
            await context.bot.delete_message(chat_id, msg_id)
            deleted += 1
        except:
            pass
        await asyncio.sleep(0.05)
    try:
        await status_msg.delete()
    except:
        pass
    confirm = await context.bot.send_message(
        chat_id,
        f"✅ تم مسح *{deleted}* رسالة من [{target.first_name}](tg://user?id={target.id}).",
        parse_mode="Markdown"
    )
    await asyncio.sleep(4)
    try:
        await confirm.delete()
    except:
        pass

# ===================== أوامر المطور =====================

async def cmd_bot_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_developer(update.effective_user.id):
        await update.message.reply_text("❌ هذا الأمر للمطور فقط.")
        return
    active_groups = sum(1 for s in group_settings.values() if s.get("active"))
    await update.message.reply_text(
        f"📊 *إحصائيات البوت*\n\n"
        f"👑 المطور: @{DEVELOPER_USERNAME}\n"
        f"🟢 الجروبات النشطة: {active_groups}\n"
        f"📁 إجمالي الجروبات: {len(group_settings)}\n"
        f"⭐ مشرفو البوت: {sum(len(a) for a in admins.values())}\n"
        f"💎 الأعضاء المميزون: {sum(len(v) for v in vip_users.values())}",
        parse_mode="Markdown"
    )

async def cmd_my_groups(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_developer(update.effective_user.id):
        await update.message.reply_text("❌ هذا الأمر للمطور فقط.")
        return
    active = sum(1 for s in group_settings.values() if s.get("active"))
    await update.message.reply_text(
        f"📋 *الجروبات النشطة:* {active}\n"
        f"📋 *إجمالي الجروبات:* {len(group_settings)}",
        parse_mode="Markdown"
    )

# ===================== رسالة ترحيبية =====================

async def welcome_new_member(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    if not get_group_settings(chat.id)["active"]:
        return
    for member in update.message.new_chat_members:
        if member.is_bot:
            continue
        await update.message.reply_text(
            f"👋 أهلاً وسهلاً [{member.first_name}](tg://user?id={member.id}) في *{chat.title}*!\n"
            f"يرجى الالتزام بقوانين المجموعة. 🌹\n\n"
            f"_🛡️ بوت الحماية — @{DEVELOPER_USERNAME}_",
            parse_mode="Markdown"
        )

# ===================== فلتر الرسائل =====================

async def filter_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message
    if not msg:
        return
    chat = update.effective_chat
    user = update.effective_user
    settings = get_group_settings(chat.id)
    if not settings["active"]:
        return
    if await is_developer(user.id):
        return
    if await is_group_admin(update, context, user.id):
        return
    if user.id in vip_users.get(chat.id, set()):
        return
    if settings["lock_links"] and msg.entities:
        for entity in msg.entities:
            if entity.type in ["url", "text_link"]:
                await msg.delete()
                await context.bot.send_message(chat.id, f"🔒 الروابط ممنوعة يا [{user.first_name}](tg://user?id={user.id})", parse_mode="Markdown")
                return
    if settings["lock_forward"] and msg.forward_date:
        await msg.delete()
        await context.bot.send_message(chat.id, f"🔒 تحويل الرسائل ممنوع يا [{user.first_name}](tg://user?id={user.id})", parse_mode="Markdown")
        return
    if settings["lock_usernames"] and msg.text:
        if re.search(r'@\w+', msg.text):
            await msg.delete()
            await context.bot.send_message(chat.id, f"🔒 نشر المعرفات ممنوع يا [{user.first_name}](tg://user?id={user.id})", parse_mode="Markdown")
            return
    if settings["lock_photos"] and msg.photo:
        await msg.delete()
        await context.bot.send_message(chat.id, f"🔒 الصور ممنوعة يا [{user.first_name}](tg://user?id={user.id})", parse_mode="Markdown")
        return
    if settings["lock_videos"] and (msg.video or msg.video_note):
        await msg.delete()
        await context.bot.send_message(chat.id, f"🔒 الفيديو ممنوع يا [{user.first_name}](tg://user?id={user.id})", parse_mode="Markdown")
        return
    if settings["lock_stickers"] and msg.sticker:
        await msg.delete()
        await context.bot.send_message(chat.id, f"🔒 الملصقات ممنوعة يا [{user.first_name}](tg://user?id={user.id})", parse_mode="Markdown")
        return

# ===================== معالج الأوامر =====================

async def text_command_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message
    if not msg or not msg.text:
        return
    text = msg.text.strip()
    chat = update.effective_chat
    if chat.type == "private":
        if text in ["الاوامر", "مساعدة"]:
            await cmd_help(update, context)
        elif text == "معلومات البوت":
            await cmd_bot_info(update, context)
        return
    await filter_messages(update, context)
    commands = {
        "تفعيل":         cmd_activate,
        "تعطيل":         cmd_deactivate,
        "الاوامر":        cmd_help,
        "مساعدة":        cmd_help,
        "كتم":           cmd_mute,
        "الغاء كتم":     cmd_unmute,
        "فك كتم":        cmd_unmute,
        "حظر":           cmd_ban,
        "الغاء حظر":     cmd_unban,
        "طرد":           cmd_kick,
        "رفع ادمن":      cmd_promote_admin,
        "تنزيل ادمن":    cmd_demote_admin,
        "رفع مميز":      cmd_promote_vip,
        "تنزيل مميز":    cmd_demote_vip,
        "مسح":           cmd_purge,
        "مسح كل":        lambda u, c: cmd_purge_count(u, c, 100),
        "مسح عضو":       cmd_purge_user,
        "معلومات البوت": cmd_bot_info,
        "جروباتي":       cmd_my_groups,
    }
    lock_commands = {
        "قفل الروابط":   ("lock_links",     True,  "الروابط"),
        "فتح الروابط":   ("lock_links",     False, "الروابط"),
        "قفل التوجيه":  ("lock_forward",   True,  "التوجيه"),
        "فتح التوجيه":  ("lock_forward",   False, "التوجيه"),
        "قفل المعرفات": ("lock_usernames", True,  "المعرفات"),
        "فتح المعرفات": ("lock_usernames", False, "المعرفات"),
        "قفل الصور":    ("lock_photos",    True,  "الصور"),
        "فتح الصور":    ("lock_photos",    False, "الصور"),
        "قفل الفيديو":  ("lock_videos",    True,  "الفيديو"),
        "فتح الفيديو":  ("lock_videos",    False, "الفيديو"),
        "قفل الملصقات": ("lock_stickers",  True,  "الملصقات"),
        "فتح الملصقات": ("lock_stickers",  False, "الملصقات"),
    }
    if text in commands:
        await commands[text](update, context)
    elif text in lock_commands:
        key, lock, label = lock_commands[text]
        await handle_lock_unlock(update, context, key, lock, label)
    elif text.startswith("مسح ") and text[4:].isdigit():
        await cmd_purge_count(update, context, int(text[4:]))

# ===================== تشغيل البوت =====================

def main():
    if not BOT_TOKEN:
        print("❌ خطأ: BOT_TOKEN غير موجود في المتغيرات!")
        return
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_command_handler))
    app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, welcome_new_member))
    app.add_handler(MessageHandler(
        filters.PHOTO | filters.VIDEO | filters.Sticker.ALL | filters.FORWARDED,
        filter_messages
    ))
    print("🤖 البوت يعمل الآن...")
    print(f"👑 المطور: @{DEVELOPER_USERNAME}")
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
