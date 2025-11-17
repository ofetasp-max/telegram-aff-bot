import os
import logging
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse

from telegram import ParseMode
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TOKEN = os.environ.get("BOT_TOKEN")
ADMINS_ENV = os.environ.get("ADMIN_IDS", "")
ADMINS = [int(x.strip()) for x in ADMINS_ENV.split(",") if x.strip().isdigit()]

AFF_AMAZON_TAG = os.environ.get("AFF_AMAZON_TAG")
AFF_SHOPEE_PREFIX = os.environ.get("AFF_SHOPEE_PREFIX")

def add_amazon_tag(url, tag):
    if not tag:
        return url
    parsed = urlparse(url)
    if "amazon." not in parsed.netloc.lower():
        return url
    qs = parse_qs(parsed.query, keep_blank_values=True)
    qs["tag"] = [tag]
    new_query = urlencode(qs, doseq=True)
    return urlunparse(parsed._replace(query=new_query))

def convert_affiliate(url):
    url = url.strip()
    converted = add_amazon_tag(url, AFF_AMAZON_TAG)
    if converted != url:
        return converted
    if AFF_SHOPEE_PREFIX and ("shopee" in url):
        return AFF_SHOPEE_PREFIX
    return url

def start(update, context):
    update.message.reply_text("🤖 Bot de promoções ativo! Use /promo.")

def promo(update, context):
    user_id = update.effective_user.id
    if user_id not in ADMINS:
        update.message.reply_text("❌ Você não é admin.")
        return

    text = " ".join(context.args)
    if not text:
        update.message.reply_text("Use: /promo [mensagem + link]")
        return

    words = text.split()
    final_words = [
        convert_affiliate(w) if w.startswith("http") else w
        for w in words
    ]

    final = " ".join(final_words)
    update.message.reply_text(f"🔥 Promoção:\n{final}", parse_mode=ParseMode.MARKDOWN)

def listener(update, context):
    text = update.message.text or ""
    if "http" in text:
        words = text.split()
        final_words = [
            convert_affiliate(w) if w.startswith("http") else w
            for w in words
        ]
        final = " ".join(final_words)
        update.message.reply_text("🔗 Link convertido: " + final)

def main():
    if not TOKEN:
        logger.error("BOT_TOKEN não configurado!")
        return
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("promo", promo))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, listener))

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
