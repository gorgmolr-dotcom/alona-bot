"""
بوت حماية تيليجرام - Arabic Telegram Protection Bot
المطور: أحمد الجمال @Ahmedjammal1988
المكتبة: python-telegram-bot v20.3
"""

import logging
import asyncio
import os
import re
import random
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
    user_id = update.effective_user.id
    if await is_developer(user_id):
        return True
    if await is_group_admin(update, context, user_id):
        return True
    await update.message.reply_text("❌ ليس لديك صلاحية لاستخدام هذا الأمر.")
    return False

def get_thread_kwargs(update: Update):
    msg = update.effective_message
    if msg and msg.message_thread_id is not None:
        return {"message_thread_id": msg.message_thread_id}
    return {}

def build_smart_reply(text: str, user_name: str):
    normalized = text.lower()
    normalized = re.sub(r"[ًٌٍَُِّْـ]", "", normalized)
    normalized = normalized.replace("أ", "ا").replace("إ", "ا").replace("آ", "ا")
    normalized = normalized.replace("ة", "ه")
    normalized = re.sub(r"[^\w\s\u0600-\u06FF]", " ", normalized)
    normalized = re.sub(r"\s+", " ", normalized).strip()

    greeting_keys = ["السلام عليكم", "سلام عليكم", "سلام", "هلا", "اهلا", "مرحبا", "ياهلا", "يا هلا", "hi", "hello"]
    how_are_you_keys = ["كيفك", "شلونك", "كيف الحال", "اخبارك", "عامل ايه", "كيف حالك", "علومك", "طمني"]
    thanks_keys = ["شكرا", "مشكور", "يعطيك العافيه", "تسلم", "يسلمو", "ممتن", "الف شكر", "يعطيك الف عافيه"]
    morning_keys = ["صباح الخير", "صباح النور", "صبحكم", "صباحو", "صباح الفل", "صبح"]
    evening_keys = ["مساء الخير", "مساء النور", "مساك", "مساكم", "مساؤكم", "مسى الخير"]
    goodbye_keys = ["باي", "مع السلامه", "مع السلامة", "اشوفك", "نشوفك", "تصبحون", "تصبح على خير", "وداعا"]
    love_keys = ["احبك", "بحبك", "احب البوت", "افضل بوت", "روعه", "رهيب", "فخم", "جامد"]
    prayer_keys = ["الحمد لله", "ماشاء الله", "ان شاء الله", "جزاك الله", "الله يبارك", "اللهم", "يارب", "استغفر الله"]
    help_keys = ["ساعدني", "مساعده", "مساعدة", "احتاج مساعده", "ابغى مساعده", "ابي مساعده", "عندي مشكله", "عندي مشكلة"]
    welcome_keys = ["نورت", "منور", "منوره", "ياهلا بك", "هلا بك", "اهلا بك", "اهلين وسهلين"]

    replies = {
        "greeting": [
            "وعليكم السلام يا {name} 🌹 نورت المكان كله، وأهلًا وسهلًا فيك. إذا بدك أي مساعدة أنا حاضر مباشرة وبأجمل خدمة.",
            "يا هلا فيك يا {name} ✨ حضورك جميل جدًا، وأي سؤال أو طلب عندك ارسله وأنا أرد عليك بسرعة وبأسلوب مرتب وواضح.",
            "مرحبًا يا {name} 🤍 أسعدتني رسالتك، وأنا موجود دائمًا للمساعدة والرد المباشر بأي وقت تحتاجني فيه.",
            "هلا وغلا يا {name} 💫 نورت المجموعة، وإذا عندك استفسار أو بدك دعم أنا جاهز بخدمة سريعة وكاملة.",
            "أهلين يا {name} 🌟 كل الاحترام لك، وأنا موجود حتى أخدمك بردود واضحة وحديثة ومباشرة.",
            "يا مرحبا مليون يا {name} 💙 حضورك ينعش المكان، وأنا جاهز لأي طلب بطريقة أنيقة وسريعة.",
            "هلا بالحضور الراقي يا {name} 🌸 سعدت برسالتك جدًا، وأنا معك لأي استفسار بوضوح كامل.",
            "أهلاً يا {name} ✨ نورتنا والله، وكل ما تحتاجه اكتبه مباشرة وأنا أتولى الباقي."
        ],
        "how_are_you": [
            "أنا تمام جدًا يا {name} الحمد لله 😄 والأجمل إنك موجود. قلّي شو تحتاج وأنا أساعدك خطوة بخطوة وبكل سرور.",
            "بخير يا {name} 🌷 تسلم على سؤالك الجميل. إذا عندك أي فكرة أو طلب، اكتبها مباشرة وأنا أتعامل معها فورًا.",
            "الحمد لله ممتاز يا {name} 🤍 وأتمنى يومك يكون مليان إنجاز وراحة. أنا حاضر لأي مساعدة الآن.",
            "تمام وبأفضل حال يا {name} ✨ شكراً لذوقك. أرسل اللي بدك إياه وأنا أجاوبك برد مرتب ومفيد.",
            "أموري تمام يا {name} 🌹 وإن شاء الله أنت بألف خير. أنا جاهز لأي طلب بشكل فوري وواضح.",
            "أنا بخير والحمد لله يا {name} 🌟 وأتمنى لك يوم حلو. إذا عندك شغلة بدك تنجزها أنا حاضر.",
            "كويس جدًا يا {name} 💫 شكلك ذوق من أسلوبك، خلينا نكمل أي طلب عندك بشكل ممتاز.",
            "الحمد لله تمام يا {name} 💙 وجودك يسعدني، وأي شيء تحب أسويه لك أنا جاهز."
        ],
        "thanks": [
            "العفو يا {name} 🤝 هذا واجبي، ويسعدني دائمًا أكون عند حسن ظنك بخدمة سريعة ومرتبة.",
            "تسلم يا {name} 🌟 كلامك يسعدني جدًا، وأنا دائمًا موجود حتى أساعدك بأفضل شكل ممكن.",
            "ولا يهمك يا {name} 💙 أي وقت تحتاجني أنا حاضر، والأولوية دائمًا لخدمتك بأعلى جودة.",
            "الشكر لك يا {name} 🌹 على أسلوبك الجميل، وأنا مستمر معك في أي طلب جديد.",
            "على راسي يا {name} ✨ يسعدني دعمك، وأي شيء تحتاجه بعد أنا جاهز مباشرة.",
            "العفو يا بطل يا {name} 🌼 رضاك أهم شيء، وأنا مستمر بخدمتك بكل احتراف.",
            "تستاهل كل خير يا {name} 💫 إذا في أي خطوة بعدها أنا موجود بدون تأخير.",
            "حياك الله يا {name} 🌷 كلماتك ترفع المعنويات، وشرف لي أكون عون لك."
        ],
        "morning": [
            "صباح الورد يا {name} ☀️ يومك جميل وإنجازاتك أكبر، وإن احتجت مساعدة أنا حاضر من الآن.",
            "صباح النور والسعادة يا {name} 🌼 بداية موفقة لك، وأنا جاهز لأي استفسار أو طلب.",
            "صباح الخير يا {name} 💫 أتمنى لك يومًا رائعًا، وأنا هنا لأي دعم مباشر وسريع.",
            "صباحك عسل يا {name} 🌷 الله يعطيك يوم مليء بالنجاح والراحة، وأنا بخدمتك دائمًا.",
            "صباح التفاؤل يا {name} ✨ أتمنى لك إنجازات قوية، وأنا جاهز أساعدك بأي خطوة.",
            "صباحك خير وبركة يا {name} 💙 يوم جديد وفرص جديدة، وأنا معك لأي شيء تحتاجه.",
            "صباح الابتسامة يا {name} 🌸 جعل يومك كله رضا ونجاح، وأي طلب أنا حاضر."
        ],
        "evening": [
            "مساء الخير يا {name} 🌙 مساء هادئ وجميل عليك، وإذا تحتاج أي شيء أنا متواجد فورًا.",
            "مساء النور يا {name} ✨ أتمنى لك أمسية سعيدة، وأنا جاهز للرد على أي استفسار عندك.",
            "مساك ورد يا {name} 🌹 حضورك لطيف جدًا، وإذا عندك طلب أنا معك مباشرة.",
            "مساء جميل يا {name} 💙 كل التقدير لك، وأنا حاضر لأي مساعدة بشكل سريع ومنظم.",
            "مساء الراحة يا {name} 🌟 أتمنى لك وقت هادئ ولطيف، وأنا موجود لأي دعم.",
            "مساك سعادة يا {name} 🌼 إذا عندك استفسار أو فكرة، اكتبها وأنا أجاوبك مباشرة.",
            "مساء الفل يا {name} 💫 حضورك مميز جدًا، وأنا بخدمتك بكل وقت."
        ],
        "goodbye": [
            "في أمان الله يا {name} 🌹 نورتنا، ونتشرف برجعتك بأي وقت.",
            "مع السلامة يا {name} ✨ يومك سعيد، وأنا موجود وقت ما تحتاجني.",
            "نشوفك على خير يا {name} 💙 كان حضورك رائع، وبانتظارك دائمًا.",
            "الله معك يا {name} 🌟 وخذ راحتك، وأنا حاضر أول ما ترجع.",
            "وداعًا مؤقتًا يا {name} 🌸 ناطرينك ترجع بالنور والفرح."
        ],
        "love": [
            "يا بعد قلبي يا {name} 🤍 كلامك يسعدني جدًا، وراح أظل أقدملك أفضل ردود وخدمة.",
            "تسلم يا {name} 🌹 ذوقك عالي، ووعد مني أكون دائمًا عند حسن ظنك.",
            "محبتك على الراس يا {name} 💫 هذا الدعم يخليني أقدم لك مستوى أقوى كل مرة.",
            "أنت الرهيب يا {name} 💙 شكرًا لك، وأنا جاهز دومًا لأي طلب منك.",
            "يا لطيف الذوق يا {name} 🌟 وجودك يرفع الحماس، وأنا معك خطوة بخطوة."
        ],
        "prayer": [
            "آمين يا رب يا {name} 🤲 الله يكتب لك الخير كله ويبارك في وقتك وعملك.",
            "جزاك الله خيرًا يا {name} 🌹 كلام طيب من قلب طيب، الله يسعدك ويوفقك.",
            "ما شاء الله عليك يا {name} ✨ الله يزيدك من فضله ويجعل أيامك كلها بركة.",
            "الحمد لله دائمًا يا {name} 💙 أسأل الله لك راحة البال والتوفيق في كل خطوة.",
            "الله يفتحها بوجهك يا {name} 🌟 ويديم عليك الصحة والسرور."
        ],
        "help": [
            "أكيد يا {name} 🤝 أنا حاضر لمساعدتك فورًا. اكتب المشكلة أو الطلب بالتفصيل وأنا أحلها معك خطوة بخطوة.",
            "ولا يهمك يا {name} 💫 أنا معك بالكامل. فقط أرسل المطلوب بوضوح، وبجهز لك رد مباشر ومفيد.",
            "حاضر يا {name} 🌹 اشرح لي ماذا تحتاج تحديدًا، وأنا أعطيك أفضل حل بشكل سريع ومنظم.",
            "تم يا {name} ✨ أنا جاهز للدعم الآن. اكتب سؤالك وأنا أرد عليك بطريقة واضحة وسهلة.",
            "على راسي يا {name} 🌟 قلّي المطلوب الآن، وأنا أساعدك حتى توصل للنتيجة اللي تريدها."
        ],
        "welcome": [
            "وجودك نور يا {name} 🌸 الله يحييك، ويا هلا بك بيننا دائمًا.",
            "يا مرحبا فيك يا {name} 💙 نورت المكان وحضورك يسعدنا.",
            "منور يا {name} ✨ أهلاً وسهلاً فيك، وكلنا سعداء بوجودك.",
            "هلا وغلا يا {name} 🌹 شرفتنا، وإن شاء الله تقضي وقت جميل معنا.",
            "يا هلا بك يا {name} 🌟 أهلاً بعضو راقٍ وكلام أجمل."
        ],
    }

    if any(key in normalized for key in greeting_keys):
        return random.choice(replies["greeting"]).format(name=user_name)
    if any(key in normalized for key in how_are_you_keys):
        return random.choice(replies["how_are_you"]).format(name=user_name)
    if any(key in normalized for key in thanks_keys):
        return random.choice(replies["thanks"]).format(name=user_name)
    if any(key in normalized for key in morning_keys):
        return random.choice(replies["morning"]).format(name=user_name)
    if any(key in normalized for key in evening_keys):
        return random.choice(replies["evening"]).format(name=user_name)
    if any(key in normalized for key in goodbye_keys):
        return random.choice(replies["goodbye"]).format(name=user_name)
    if any(key in normalized for key in love_keys):
        return random.choice(replies["love"]).format(name=user_name)
    if any(key in normalized for key in prayer_keys):
        return random.choice(replies["prayer"]).format(name=user_name)
    if any(key in normalized for key in help_keys):
        return random.choice(replies["help"]).format(name=user_name)
    if any(key in normalized for key in welcome_keys):
        return random.choice(replies["welcome"]).format(name=user_name)
    return None

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
    if update.effective_chat.type != "private":
        if not await check_permission(update, context):
            return
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
    confirm = await context.bot.send_message(
        chat_id,
        f"✅ تم مسح *{deleted}* رسالة.",
        parse_mode="Markdown",
        **get_thread_kwargs(update)
    )
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
    confirm = await context.bot.send_message(
        chat_id,
        f"✅ تم مسح *{deleted}* رسالة.",
        parse_mode="Markdown",
        **get_thread_kwargs(update)
    )
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
        parse_mode="Markdown",
        **get_thread_kwargs(update)
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
                await context.bot.send_message(
                    chat.id,
                    f"🔒 الروابط ممنوعة يا [{user.first_name}](tg://user?id={user.id})",
                    parse_mode="Markdown",
                    **get_thread_kwargs(update)
                )
                return
    if settings["lock_forward"] and msg.forward_date:
        await msg.delete()
        await context.bot.send_message(
            chat.id,
            f"🔒 تحويل الرسائل ممنوع يا [{user.first_name}](tg://user?id={user.id})",
            parse_mode="Markdown",
            **get_thread_kwargs(update)
        )
        return
    if settings["lock_usernames"] and msg.text:
        if re.search(r'@\w+', msg.text):
            await msg.delete()
            await context.bot.send_message(
                chat.id,
                f"🔒 نشر المعرفات ممنوع يا [{user.first_name}](tg://user?id={user.id})",
                parse_mode="Markdown",
                **get_thread_kwargs(update)
            )
            return
    if settings["lock_photos"] and msg.photo:
        await msg.delete()
        await context.bot.send_message(
            chat.id,
            f"🔒 الصور ممنوعة يا [{user.first_name}](tg://user?id={user.id})",
            parse_mode="Markdown",
            **get_thread_kwargs(update)
        )
        return
    if settings["lock_videos"] and (msg.video or msg.video_note):
        await msg.delete()
        await context.bot.send_message(
            chat.id,
            f"🔒 الفيديو ممنوع يا [{user.first_name}](tg://user?id={user.id})",
            parse_mode="Markdown",
            **get_thread_kwargs(update)
        )
        return
    if settings["lock_stickers"] and msg.sticker:
        await msg.delete()
        await context.bot.send_message(
            chat.id,
            f"🔒 الملصقات ممنوعة يا [{user.first_name}](tg://user?id={user.id})",
            parse_mode="Markdown",
            **get_thread_kwargs(update)
        )
        return

# ===================== معالج الأوامر =====================

async def text_command_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message
    if not msg or not msg.text:
        return
    if update.effective_user and update.effective_user.is_bot:
        return
    text = msg.text.strip()
    chat = update.effective_chat
    if chat.type == "private":
        if text in ["الاوامر", "مساعدة"]:
            await cmd_help(update, context)
        elif text == "معلومات البوت":
            await cmd_bot_info(update, context)
        else:
            smart_reply = build_smart_reply(text, update.effective_user.first_name)
            if smart_reply:
                await msg.reply_text(smart_reply)
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
    elif get_group_settings(chat.id)["active"]:
        smart_reply = build_smart_reply(text, update.effective_user.first_name)
        if smart_reply:
            await context.bot.send_message(
                chat.id,
                smart_reply,
                **get_thread_kwargs(update)
            )

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
