"""
Agent Foxtrot: Lead UX Engineer (Interface)
Mission: Build the Telegram Bot Wrapper.
"""

import logging
import os
import asyncio
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# Load environment variables
load_dotenv()

logger = logging.getLogger("AgentFoxtrot")

class AgentFoxtrot:
    def __init__(self, orchestrator):
        self.orchestrator = orchestrator
        self.token = os.getenv("TELEGRAM_TOKEN")
        if not self.token:
            logger.error("TELEGRAM_TOKEN not found in .env file.")
            raise ValueError("TELEGRAM_TOKEN not found in .env file.")
        
        self.application = None
        logger.info("Agent Foxtrot initialized.")
        
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        from src import config
        await update.message.reply_text(
            "🤖 Agent Foxtrot online.\n"
            "Use /generate [Theme] to start the factory.\n"
            "Example: /generate Firefighter\n\n"
            f"📊 Mission Control: {config.MISSION_CONTROL_SHEET_URL}"
        )

    async def generate_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not context.args:
            await update.message.reply_text("⚠️ Please provide a theme.\nUsage: /generate [Theme]")
            return

        theme = " ".join(context.args)
        from src import config
        
        # Initial Dashboard Message
        dashboard_msg = await update.message.reply_text(
            f"🚀 <b>Initiating Launch Sequence</b>\n"
            f"Theme: {theme}\n"
            f"⚙️ Phase: Initialization\n"
            f"📊 Progress: 0%\n"
            f"📝 Status: Starting engines...\n\n"
            f"📊 <a href='{config.MISSION_CONTROL_SHEET_URL}'>Mission Control</a>",
            parse_mode='HTML'
        )
        
        # Progress Callback
        async def progress_callback(msg_text):
            try:
                # Append Mission Control link to every update
                full_msg = f"{msg_text}\n\n📊 <a href='{config.MISSION_CONTROL_SHEET_URL}'>Mission Control</a>"
                # Only edit if content changed (Telegram API limitation/optimization)
                if full_msg != dashboard_msg.text:
                    await dashboard_msg.edit_text(full_msg, parse_mode='HTML')
            except Exception as e:
                logger.warning(f"Failed to update dashboard: {e}")

        try:
            # Start Job (Async)
            result = await self.orchestrator.start_job(theme, progress_callback)
            
            # Final Status Update
            await dashboard_msg.edit_text(
                f"✅ <b>Mission Accomplished!</b>\n"
                f"Theme: {theme}\n"
                f"⚙️ Phase: Complete\n"
                f"📊 Progress: 100%\n"
                f"📝 Status: Ready for download.\n\n"
                f"📊 <a href='{config.MISSION_CONTROL_SHEET_URL}'>Mission Control</a>",
                parse_mode='HTML'
            )
            
            # Send Visual Proof (Media Group)
            from telegram import InputMediaPhoto
            media_group = []
            
            # Helper to safely open files
            def get_photo(path, caption):
                if path and os.path.exists(path):
                    return InputMediaPhoto(open(path, 'rb'), caption=caption)
                return None

            # Cover is now generated as separate front/back panels
            for key, caption in (('cover_front', "Cover (Front)"),
                                 ('cover_back', "Cover (Back)"),
                                 ('cover', "Cover Page")):
                if key in result['previews']:
                    p = get_photo(result['previews'][key], caption)
                    if p: media_group.append(p)

            if 'knolling' in result['previews']:
                p = get_photo(result['previews']['knolling'], "Knolling Page")
                if p: media_group.append(p)
                
            if 'action' in result['previews']:
                p = get_photo(result['previews']['action'], "Action Page")
                if p: media_group.append(p)
            
            if media_group:
                await update.message.reply_media_group(media_group)
            
            # Deliver the PDF itself (a file:// link is useless to a Telegram user)
            pdf_path = result.get('pdf_path')
            if pdf_path and os.path.exists(pdf_path):
                with open(pdf_path, 'rb') as pdf_file:
                    await update.message.reply_document(
                        pdf_file, filename=os.path.basename(pdf_path),
                        caption="📕 Your book is ready!"
                    )
            else:
                await update.message.reply_text(f"📕 <b>PDF:</b> {result['drive_link']}", parse_mode='HTML')
            
        except Exception as e:
            logger.error(f"Failed to start job: {e}")
            await dashboard_msg.edit_text(
                f"❌ <b>Mission Failed</b>\n"
                f"Error: {e}\n\n"
                f"📊 <a href='{config.MISSION_CONTROL_SHEET_URL}'>Mission Control</a>",
                parse_mode='HTML'
            )

    def start(self):
        """
        Starts the Telegram bot.
        """
        logger.info("Starting Telegram Bot...")
        
        self.application = ApplicationBuilder().token(self.token).build()
        
        self.application.add_handler(CommandHandler("start", self.start_command))
        self.application.add_handler(CommandHandler("generate", self.generate_command))
        
        # Run the bot
        self.application.run_polling()
