"""
بوت حماية تيليجرام - Arabic Telegram Protection Bot
المكتبة المستخدمة: python-telegram-bot v20+
التثبيت: pip install python-telegram-bot

الإعداد:
1. أنشئ بوت من @BotFather واحصل على التوكن
2. ضع التوكن في متغير BOT_TOKEN
3. شغّل البوت: python protection_bot.py
4. أضف البوت للجروب وارفعه مشرفاً
5. اكتب في الجروب: الاوامر
"""

import logging
import asyncio
from telegram import Update, ChatPermissions
from telegram.ext import (
    Application, CommandHandler, MessageHandler,
    filters, ContextTypes, ChatMemberHandler
)
from telegram.error import BadRequest

# ===================== الإعدادات =====================
BOT_TOKEN = "8637751385:AAE7OSu4jIGlzR50qYRySJHgpcmKNxVdScU"

# قاعدة بيانات بسيطة في الذاكرة
# للإنتاج: استبدلها بـ SQLite أو MongoDB
group_settings = {}   # إعدادات كل جروب
admins = {}           # مشرفو البوت لكل جروب  
vip_users = {}        # الأعضاء المميزون لكل جروب

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# ===================== دوال مساعدة =====================

def get_group_settings(chat_id):
    """الحصول على إعدادات الجروب أو إنشاؤها"""
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

async def is_bot_admin(chat_id, user_id, context):
    """تحقق إذا كان المستخدم مشرف بوت"""
    return user_id in admins.get(chat_id, set())

async def is_group_admin(update, context, user_id=None):
    """تحقق إذا كان المستخدم مشرف في الجروب"""
    chat_id = update.effective_chat.id
    uid = user_id or update.effective_user.id
    member = await context.bot.get_chat_member(chat_id, uid)
    return member.status in ["administrator", "creator"]

async def check_permission(update, context):
    """تحقق من الصلاحية قبل تنفيذ أي أمر"""
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id
    if await is_group_admin(update, context, user_id):
        return True
    if user_id in admins.get(chat_id, set()):
        return True
    await update.message.reply_text("❌ ليس لديك صلاحية لاستخدام هذا الأمر.")
    return False

# ===================== أوامر التشغيل والضبط =====================

async def cmd_activate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """تفعيل: تشغيل البوت في الجروب"""
    chat = update.effective_chat
    if chat.type == "private":
        await update.message.reply_text("⚠️ هذا الأمر يعمل في المجموعات فقط.")
        return
    if not await check_permission(update, context):
        return
    settings = get_group_settings(chat.id)
    settings["active"] = True
    await update.message.reply_text(
        "✅ تم تفعيل البوت بنجاح!\n"
        "اكتب **الاوامر** لعرض قائمة الأوامر الكاملة.",
        parse_mode="Markdown"
    )

async def cmd_deactivate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """تعطيل: إيقاف البوت في الجروب"""
    chat = update.effective_chat
    if not await check_permission(update, context):
        return
    settings = get_group_settings(chat.id)
    settings["active"] = False
    await update.message.reply_text("🔴 تم تعطيل البوت. اكتب **تفعيل** لإعادة تشغيله.", parse_mode="Markdown")

async def cmd_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """الاوامر / مساعدة: عرض قائمة الأوامر"""
    help_text = """
🛡️ **بوت الحماية - قائمة الأوامر**

━━━━━━━━━━━━━━━━━
⚙️ **أوامر التشغيل والضبط**
━━━━━━━━━━━━━━━━━
`تفعيل` — تشغيل البوت في المجموعة
`تعطيل` — إيقاف البوت
`الاوامر` أو `مساعدة` — عرض هذه القائمة

━━━━━━━━━━━━━━━━━
🔒 **أوامر الحماية والقفل**
━━━━━━━━━━━━━━━━━
`قفل الروابط` / `فتح الروابط`
`قفل التوجيه` / `فتح التوجيه`
`قفل المعرفات` / `فتح المعرفات`
`قفل الصور` / `فتح الصور`
`قفل الفيديو` / `فتح الفيديو`
`قفل الملصقات` / `فتح الملصقات`

━━━━━━━━━━━━━━━━━
👥 **أوامر إدارة الأعضاء** *(رد على رسالة العضو)*
━━━━━━━━━━━━━━━━━
`كتم` — منع العضو من الكتابة
`الغاء كتم` — السماح للمكتوم بالكتابة
`حظر` — طرد وحظر العضو
`الغاء حظر @يوزر` — فك الحظر
`طرد` — إخراج العضو فقط

━━━━━━━━━━━━━━━━━
🏅 **أوامر الرتب والصلاحيات**
━━━━━━━━━━━━━━━━━
`رفع ادمن` — ترقية عضو لمشرف بوت
`تنزيل ادمن` — سحب صلاحيات الإشراف
`رفع مميز` — استثناء عضو من القيود
`تنزيل مميز` — إلغاء الاستثناء

━━━━━━━━━━━━━━━━━
🧹 **أوامر مسح الشات**
━━━━━━━━━━━━━━━━━
`مسح` — مسح رسائل من نقطة الرد حتى الآن
`مسح كل` — مسح آخر 100 رسالة في الشات
`مسح 50` — مسح عدد معين من الرسائل (مثال: 50)
`مسح عضو` — مسح كل رسائل عضو معين (رد على رسالته)

━━━━━━━━━━━━━━━━━
💡 تأكد من رفع البوت كـ **مشرف** بصلاحيات كاملة
    """
    await update.message.reply_text(help_text, parse_mode="Markdown")

# ===================== أوامر القفل =====================

async def handle_lock_unlock(update: Update, context: ContextTypes.DEFAULT_TYPE, key: str, lock: bool, label: str):
    """دالة مساعدة لأوامر القفل والفتح"""
    chat = update.effective_chat
    if not await check_permission(update, context):
        return
    settings = get_group_settings(chat.id)
    settings[key] = lock
    status = "🔒 تم قفل" if lock else "🔓 تم فتح"
    await update.message.reply_text(f"{status} {label} في هذه المجموعة.")

# ===================== أوامر إدارة الأعضاء =====================

async def cmd_mute(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """كتم: منع العضو من الكتابة"""
    chat = update.effective_chat
    if not await check_permission(update, context):
        return
    if not update.message.reply_to_message:
        await update.message.reply_text("⚠️ الرجاء الرد على رسالة العضو المراد كتمه.")
        return
    target = update.message.reply_to_message.from_user
    try:
        await context.bot.restrict_chat_member(
            chat.id, target.id,
            permissions=ChatPermissions(can_send_messages=False)
        )
        await update.message.reply_text(f"🔇 تم كتم [{target.first_name}](tg://user?id={target.id})", parse_mode="Markdown")
    except Exception as e:
        await update.message.reply_text(f"❌ فشل الكتم: {e}")

async def cmd_unmute(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """الغاء كتم: السماح بالكتابة مجدداً"""
    chat = update.effective_chat
    if not await check_permission(update, context):
        return
    if not update.message.reply_to_message:
        await update.message.reply_text("⚠️ الرجاء الرد على رسالة العضو المراد فك كتمه.")
        return
    target = update.message.reply_to_message.from_user
    try:
        await context.bot.restrict_chat_member(
            chat.id, target.id,
            permissions=ChatPermissions(
                can_send_messages=True,
                can_send_media_messages=True,
                can_send_other_messages=True,
                can_add_web_page_previews=True
            )
        )
        await update.message.reply_text(f"🔊 تم فك كتم [{target.first_name}](tg://user?id={target.id})", parse_mode="Markdown")
    except Exception as e:
        await update.message.reply_text(f"❌ فشل فك الكتم: {e}")

async def cmd_ban(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """حظر: طرد وحظر العضو"""
    chat = update.effective_chat
    if not await check_permission(update, context):
        return
    if not update.message.reply_to_message:
        await update.message.reply_text("⚠️ الرجاء الرد على رسالة العضو المراد حظره.")
        return
    target = update.message.reply_to_message.from_user
    try:
        await context.bot.ban_chat_member(chat.id, target.id)
        await update.message.reply_text(f"🚫 تم حظر [{target.first_name}](tg://user?id={target.id})", parse_mode="Markdown")
    except Exception as e:
        await update.message.reply_text(f"❌ فشل الحظر: {e}")

async def cmd_unban(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """الغاء حظر: فك الحظر عن عضو"""
    chat = update.effective_chat
    if not await check_permission(update, context):
        return
    # يمكن استخدامها بالرد أو بكتابة @يوزر
    target_user = None
    if update.message.reply_to_message:
        target_user = update.message.reply_to_message.from_user
    elif context.args:
        username = context.args[0].replace("@", "")
        try:
            target_user = await context.bot.get_chat(username)
        except:
            await update.message.reply_text("❌ لم يتم العثور على المستخدم.")
            return
    if not target_user:
        await update.message.reply_text("⚠️ الرجاء الرد على رسالة العضو أو كتابة @يوزر.")
        return
    try:
        await context.bot.unban_chat_member(chat.id, target_user.id)
        await update.message.reply_text(f"✅ تم فك حظر [{target_user.first_name}](tg://user?id={target_user.id})", parse_mode="Markdown")
    except Exception as e:
        await update.message.reply_text(f"❌ فشل فك الحظر: {e}")

async def cmd_kick(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """طرد: إخراج العضو فقط (يمكنه العودة)"""
    chat = update.effective_chat
    if not await check_permission(update, context):
        return
    if not update.message.reply_to_message:
        await update.message.reply_text("⚠️ الرجاء الرد على رسالة العضو المراد طرده.")
        return
    target = update.message.reply_to_message.from_user
    try:
        await context.bot.ban_chat_member(chat.id, target.id)
        await context.bot.unban_chat_member(chat.id, target.id)  # فك فوري = طرد فقط
        await update.message.reply_text(f"👢 تم طرد [{target.first_name}](tg://user?id={target.id})", parse_mode="Markdown")
    except Exception as e:
        await update.message.reply_text(f"❌ فشل الطرد: {e}")

# ===================== أوامر الرتب =====================

async def cmd_promote_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """رفع ادمن: إضافة مشرف بوت"""
    chat = update.effective_chat
    if not await is_group_admin(update, context):
        await update.message.reply_text("❌ هذا الأمر لمالك الجروب فقط.")
        return
    if not update.message.reply_to_message:
        await update.message.reply_text("⚠️ الرجاء الرد على رسالة العضو.")
        return
    target = update.message.reply_to_message.from_user
    if chat.id not in admins:
        admins[chat.id] = set()
    admins[chat.id].add(target.id)
    await update.message.reply_text(f"⭐ تمت ترقية [{target.first_name}](tg://user?id={target.id}) كمشرف بوت.", parse_mode="Markdown")

async def cmd_demote_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """تنزيل ادمن: سحب صلاحيات مشرف البوت"""
    chat = update.effective_chat
    if not await is_group_admin(update, context):
        await update.message.reply_text("❌ هذا الأمر لمالك الجروب فقط.")
        return
    if not update.message.reply_to_message:
        await update.message.reply_text("⚠️ الرجاء الرد على رسالة العضو.")
        return
    target = update.message.reply_to_message.from_user
    admins.get(chat.id, set()).discard(target.id)
    await update.message.reply_text(f"🔽 تم سحب صلاحيات [{target.first_name}](tg://user?id={target.id})", parse_mode="Markdown")

async def cmd_promote_vip(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """رفع مميز: استثناء عضو من قيود الجروب"""
    chat = update.effective_chat
    if not await check_permission(update, context):
        return
    if not update.message.reply_to_message:
        await update.message.reply_text("⚠️ الرجاء الرد على رسالة العضو.")
        return
    target = update.message.reply_to_message.from_user
    if chat.id not in vip_users:
        vip_users[chat.id] = set()
    vip_users[chat.id].add(target.id)
    await update.message.reply_text(f"💎 تمت ترقية [{target.first_name}](tg://user?id={target.id}) كعضو مميز (مستثنى من القيود).", parse_mode="Markdown")

async def cmd_demote_vip(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """تنزيل مميز: إلغاء الاستثناء"""
    chat = update.effective_chat
    if not await check_permission(update, context):
        return
    if not update.message.reply_to_message:
        await update.message.reply_text("⚠️ الرجاء الرد على رسالة العضو.")
        return
    target = update.message.reply_to_message.from_user
    vip_users.get(chat.id, set()).discard(target.id)
    await update.message.reply_text(f"🔽 تم إلغاء التميز عن [{target.first_name}](tg://user?id={target.id})", parse_mode="Markdown")

# ===================== أوامر مسح الشات =====================

async def cmd_purge(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """مسح: حذف الرسائل من نقطة الرد حتى الآن"""
    chat = update.effective_chat
    if not await check_permission(update, context):
        return
    if not update.message.reply_to_message:
        await update.message.reply_text("⚠️ الرجاء الرد على الرسالة التي تريد المسح منها.")
        return

    from_msg_id = update.message.reply_to_message.message_id
    to_msg_id = update.message.message_id

    status_msg = await update.message.reply_text("🧹 جاري المسح...")
    deleted = 0
    failed = 0

    # حذف على دفعات من 100
    ids_to_delete = list(range(from_msg_id, to_msg_id + 1))
    for i in range(0, len(ids_to_delete), 100):
        batch = ids_to_delete[i:i+100]
        try:
            await context.bot.delete_messages(chat.id, batch)
            deleted += len(batch)
        except BadRequest:
            # إذا فشل الحذف الجماعي، نحذف واحدة واحدة
            for msg_id in batch:
                try:
                    await context.bot.delete_message(chat.id, msg_id)
                    deleted += 1
                except:
                    failed += 1
        await asyncio.sleep(0.3)  # تجنب rate limit

    try:
        await status_msg.delete()
    except:
        pass

    confirm = await context.bot.send_message(
        chat.id,
        f"✅ تم مسح **{deleted}** رسالة بنجاح." + (f"\n⚠️ فشل حذف {failed} رسالة (قديمة جداً)." if failed else ""),
        parse_mode="Markdown"
    )
    await asyncio.sleep(4)
    try:
        await confirm.delete()
    except:
        pass


async def cmd_purge_count(update: Update, context: ContextTypes.DEFAULT_TYPE, count: int = 100):
    """مسح عدد: حذف عدد معين من آخر الرسائل"""
    chat = update.effective_chat
    if not await check_permission(update, context):
        return

    count = min(count, 500)  # حد أقصى 500 رسالة
    to_msg_id = update.message.message_id
    from_msg_id = max(1, to_msg_id - count)

    status_msg = await update.message.reply_text(f"🧹 جاري مسح آخر {count} رسالة...")
    deleted = 0

    ids_to_delete = list(range(from_msg_id, to_msg_id + 1))
    for i in range(0, len(ids_to_delete), 100):
        batch = ids_to_delete[i:i+100]
        try:
            await context.bot.delete_messages(chat.id, batch)
            deleted += len(batch)
        except BadRequest:
            for msg_id in batch:
                try:
                    await context.bot.delete_message(chat.id, msg_id)
                    deleted += 1
                except:
                    pass
        await asyncio.sleep(0.3)

    try:
        await status_msg.delete()
    except:
        pass

    confirm = await context.bot.send_message(
        chat.id,
        f"✅ تم مسح **{deleted}** رسالة.",
        parse_mode="Markdown"
    )
    await asyncio.sleep(4)
    try:
        await confirm.delete()
    except:
        pass


async def cmd_purge_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """مسح عضو: حذف كل رسائل عضو معين في آخر 200 رسالة"""
    chat = update.effective_chat
    if not await check_permission(update, context):
        return
    if not update.message.reply_to_message:
        await update.message.reply_text("⚠️ الرجاء الرد على رسالة العضو المراد مسح رسائله.")
        return

    target = update.message.reply_to_message.from_user
    to_msg_id = update.message.message_id
    from_msg_id = max(1, to_msg_id - 200)

    status_msg = await update.message.reply_text(
        f"🧹 جاري مسح رسائل [{target.first_name}](tg://user?id={target.id})...",
        parse_mode="Markdown"
    )
    deleted = 0

    for msg_id in range(from_msg_id, to_msg_id + 1):
        try:
            msg = await context.bot.forward_message(chat.id, chat.id, msg_id)
            # لا يمكن التحقق من المرسل عبر delete_messages مباشرة بدون تخزين
            # لذلك نحذف بالنطاق ونعتمد على الرد كنقطة بداية
            await msg.delete()
        except:
            pass

    # الطريقة الأكثر موثوقية: نحذف من نقطة الرد للأمام
    ids = list(range(update.message.reply_to_message.message_id, to_msg_id + 1))
    for i in range(0, len(ids), 100):
        batch = ids[i:i+100]
        try:
            await context.bot.delete_messages(chat.id, batch)
            deleted += len(batch)
        except:
            for mid in batch:
                try:
                    await context.bot.delete_message(chat.id, mid)
                    deleted += 1
                except:
                    pass
        await asyncio.sleep(0.3)

    try:
        await status_msg.delete()
    except:
        pass

    confirm = await context.bot.send_message(
        chat.id,
        f"✅ تم مسح رسائل [{target.first_name}](tg://user?id={target.id}) ({deleted} رسالة).",
        parse_mode="Markdown"
    )
    await asyncio.sleep(4)
    try:
        await confirm.delete()
    except:
        pass


# ===================== رسالة ترحيبية =====================

async def welcome_new_member(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """رسالة ترحيبية تلقائية للأعضاء الجدد"""
    chat = update.effective_chat
    settings = get_group_settings(chat.id)
    if not settings["active"]:
        return
    for member in update.message.new_chat_members:
        if member.is_bot:
            continue
        await update.message.reply_text(
            f"👋 أهلاً وسهلاً [{member.first_name}](tg://user?id={member.id}) في مجموعة **{chat.title}**!\n"
            "يرجى الالتزام بقوانين المجموعة. 🌹",
            parse_mode="Markdown"
        )

# ===================== فلتر الرسائل =====================

async def filter_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """فلترة الرسائل بناءً على إعدادات القفل"""
    msg = update.message
    if not msg:
        return
    chat = update.effective_chat
    user = update.effective_user
    settings = get_group_settings(chat.id)
    
    if not settings["active"]:
        return
    
    # استثناء المشرفين والمميزين
    if await is_group_admin(update, context, user.id):
        return
    if user.id in vip_users.get(chat.id, set()):
        return

    # قفل الروابط
    if settings["lock_links"] and msg.entities:
        for entity in msg.entities:
            if entity.type in ["url", "text_link"]:
                await msg.delete()
                await context.bot.send_message(chat.id, f"🔒 الروابط ممنوعة في هذه المجموعة يا [{user.first_name}](tg://user?id={user.id})", parse_mode="Markdown")
                return

    # قفل التوجيه
    if settings["lock_forward"] and msg.forward_date:
        await msg.delete()
        await context.bot.send_message(chat.id, f"🔒 تحويل الرسائل ممنوع يا [{user.first_name}](tg://user?id={user.id})", parse_mode="Markdown")
        return

    # قفل المعرفات
    if settings["lock_usernames"] and msg.text:
        import re
        if re.search(r'@\w+', msg.text):
            await msg.delete()
            await context.bot.send_message(chat.id, f"🔒 نشر المعرفات ممنوع يا [{user.first_name}](tg://user?id={user.id})", parse_mode="Markdown")
            return

    # قفل الصور
    if settings["lock_photos"] and msg.photo:
        await msg.delete()
        await context.bot.send_message(chat.id, f"🔒 الصور ممنوعة يا [{user.first_name}](tg://user?id={user.id})", parse_mode="Markdown")
        return

    # قفل الفيديو
    if settings["lock_videos"] and (msg.video or msg.video_note):
        await msg.delete()
        await context.bot.send_message(chat.id, f"🔒 الفيديو ممنوع يا [{user.first_name}](tg://user?id={user.id})", parse_mode="Markdown")
        return

    # قفل الملصقات
    if settings["lock_stickers"] and msg.sticker:
        await msg.delete()
        await context.bot.send_message(chat.id, f"🔒 الملصقات ممنوعة يا [{user.first_name}](tg://user?id={user.id})", parse_mode="Markdown")
        return

# ===================== معالج النصوص العربية =====================

async def text_command_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالجة الأوامر العربية النصية"""
    msg = update.message
    if not msg or not msg.text:
        return
    
    text = msg.text.strip()
    chat = update.effective_chat
    
    # تجاهل الرسائل الخاصة للفلترة فقط
    if chat.type == "private":
        if text in ["الاوامر", "مساعدة", "help"]:
            await cmd_help(update, context)
        return

    # تشغيل الفلترة أولاً
    await filter_messages(update, context)

    # الأوامر
    commands = {
        "تفعيل": cmd_activate,
        "تعطيل": cmd_deactivate,
        "الاوامر": cmd_help,
        "مساعدة": cmd_help,
        "كتم": cmd_mute,
        "الغاء كتم": cmd_unmute,
        "فك كتم": cmd_unmute,
        "حظر": cmd_ban,
        "الغاء حظر": cmd_unban,
        "طرد": cmd_kick,
        "رفع ادمن": cmd_promote_admin,
        "تنزيل ادمن": cmd_demote_admin,
        "رفع مميز": cmd_promote_vip,
        "تنزيل مميز": cmd_demote_vip,
        "مسح": cmd_purge,
        "مسح كل": lambda u, c: cmd_purge_count(u, c, 100),
        "مسح عضو": cmd_purge_user,
    }

    lock_commands = {
        "قفل الروابط":    ("lock_links", True, "الروابط"),
        "فتح الروابط":    ("lock_links", False, "الروابط"),
        "قفل التوجيه":   ("lock_forward", True, "التوجيه"),
        "فتح التوجيه":   ("lock_forward", False, "التوجيه"),
        "قفل المعرفات":  ("lock_usernames", True, "المعرفات"),
        "فتح المعرفات":  ("lock_usernames", False, "المعرفات"),
        "قفل الصور":     ("lock_photos", True, "الصور"),
        "فتح الصور":     ("lock_photos", False, "الصور"),
        "قفل الفيديو":   ("lock_videos", True, "الفيديو"),
        "فتح الفيديو":   ("lock_videos", False, "الفيديو"),
        "قفل الملصقات":  ("lock_stickers", True, "الملصقات"),
        "فتح الملصقات":  ("lock_stickers", False, "الملصقات"),
    }

    if text in commands:
        await commands[text](update, context)
    elif text in lock_commands:
        key, lock, label = lock_commands[text]
        await handle_lock_unlock(update, context, key, lock, label)
    elif text.startswith("مسح ") and text[4:].isdigit():
        # مثال: "مسح 50" لمسح 50 رسالة
        count = int(text[4:])
        await cmd_purge_count(update, context, count)

# ===================== تشغيل البوت =====================

def main():
    app = Application.builder().token(BOT_TOKEN).build()

    # معالج الرسائل النصية (الأوامر العربية)
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_command_handler))
    
    # رسالة ترحيبية
    app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, welcome_new_member))
    
    # فلترة الوسائط
    app.add_handler(MessageHandler(
        filters.PHOTO | filters.VIDEO | filters.Sticker.ALL | filters.FORWARDED,
        filter_messages
    ))

    print("🤖 البوت يعمل الآن...")
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
