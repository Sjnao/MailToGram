import logging
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from email_reader import EmailReader


class Bot:

    def __init__(self, config, mail_reader: EmailReader):
        logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                            level=logging.INFO)

        self.logger = logging.getLogger(__name__)
        self.mail_reader = mail_reader

        self.updater = Updater(token=config['token'], use_context=True)
        dp = self.updater.dispatcher
        dp.add_handler(CommandHandler("help", self._help))

        dp.add_handler(CommandHandler("set", self._set_timer,
                                      pass_args=True,
                                      pass_job_queue=True,
                                      pass_chat_data=True))
        dp.add_handler(CommandHandler("unset", self._unset, pass_chat_data=True))

        # log all errors
        dp.add_error_handler(self._error)

    def start(self):
        # Start the Bot
        self.updater.start_polling()

        # Run the bot until you press Ctrl-C or the process receives SIGINT,
        # SIGTERM or SIGABRT. This should be used most of the time, since
        # start_polling() is non-blocking and will stop the bot gracefully.
        self.updater.idle()

    @staticmethod
    def _help(update, context):
        """Send a message when the command /help is issued."""
        update.message.reply_text('Help!')

    def _error(self, update, context):
        """Log Errors caused by Updates."""
        self.logger.warning('Update "%s" caused error "%s"', update, context._error)

    def _alarm(self, context):
        """Send the alarm message."""
        msgs = self.mail_reader.get_unseen_mail()
        job = context.job
        for msg in msgs:
            context.bot.send_message(job.context, text=msg.decode())

    def _set_timer(self, update, context):
        """Add a job to the queue."""
        chat_id = update.message.chat_id
        try:
            # args[0] should contain the time for the timer in seconds
            due = int(context.args[0])
            if due < 0:
                update.message.reply_text('Sorry we can not go back to future!')
                return

            # Add job to queue and stop current one if there is a timer already
            if 'job' in context.chat_data:
                old_job = context.chat_data['job']
                old_job.schedule_removal()
            new_job = context.job_queue.run_repeating(self._alarm, interval=due, context=chat_id)
            context.chat_data['job'] = new_job

            update.message.reply_text('Timer successfully set!')

        except (IndexError, ValueError):
            update.message.reply_text('Usage: /set <seconds>')

    def _unset(self, update, context):
        """Remove the job if the user changed their mind."""
        if 'job' not in context.chat_data:
            update.message.reply_text('You have no active timer')
            return

        job = context.chat_data['job']
        job.schedule_removal()
        del context.chat_data['job']

        update.message.reply_text('Timer successfully unset!')

