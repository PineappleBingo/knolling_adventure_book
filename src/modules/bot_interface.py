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
        await update.message.reply_text(f"🚀 Copy that! Initiating launch sequence for theme: '{theme}'...")
        
        # Handoff to Agent Omega (Orchestrator)
        # Note: In a real async app, we might want to run this in a separate thread or task
        # so we don't block the bot. For now, we'll assume start_job is synchronous or fast enough,
        # or we'll need to make start_job async.
        try:
            # We pass the update object so Omega can send messages back if needed
            # But for now, Omega just takes the theme.
            # Ideally, Omega should return a run_id or status.
            self.orchestrator.start_job(theme)
            from src import config
            await update.message.reply_text(
                f"✅ Job started for '{theme}'.\n"
                f"📊 Track progress in Mission Control: {config.MISSION_CONTROL_SHEET_URL}"
            )
        except Exception as e:
            logger.error(f"Failed to start job: {e}")
            await update.message.reply_text(f"❌ Error starting job: {e}")

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
