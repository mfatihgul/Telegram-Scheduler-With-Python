import time
import telegram
from telegram import update
from telegram.error import Unauthorized
from telegram.ext.commandhandler import CommandHandler
from telegram.ext import Updater
import schedule
import re

class TelegramBot:
    def __init__(self):
        #Create a bot in Telegram with @Botfather and pass the bot token below
        self.TOKEN = "" #Bot Token

        self.bot = telegram.Bot(self.TOKEN)

        # Start message
        self.start_message = """
        ⏰ Welcome to the Reminder Bot
            Commands listed below 👇: 
            -> Daily Reminder
                /daily (Hour), (Reminder Text)
                    Example:
                        /daily 13:24, Drink water
            -> Weekly Reminder
                /weekly (Day), (Hour), (Reminder Text)
                    Example:
                        /weekly monday, 13:24, Go to the gym
        """
    
    #When the bot starts, start_message_handler will send the start_message
    def start_message_handler(self, update, context):
        chat_id = update.effective_chat.id
        context.bot.send_message(chat_id=chat_id, text=self.start_message)

    # A simple method to send message to Telegram bot
    def send_it(self, chat_id, text):
        error_count = 0
        while True:
            try:
                self.bot.send_message(chat_id=chat_id, text=text)
                break
            except Unauthorized:
                print(f"send_message_to_telegram -> Unauthorized Error")
            except Exception as e:
                print(f"send_message_to_telegram ->Error as {e}")
                error_count += 1
                if error_count == 6:
                    break
                time.sleep(1)

    #Check if the user send the correct time format for hour
    def isTimeFormat(self, input):
        try: 
            time.strptime(input, '%H:%M')
            return True
        except ValueError:
            return False
    
    # /weekly Telegram command
    def weekly(self, update, context):
        days = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"] 
        chat_id = update.effective_chat.id
        try:
            data_split = (update.message.text).split(" ") #When the user send a message, this command will split it with spaces
            command, period, hour = data_split[:3] #Weekly command has 4 parts. First 3 is command, day of the week and hour.
            #data_split will assign first three data to the variables

            notes = " ".join(data_split[3:]) #Notes can have spaces. After first three data assignment, notes will take the rest
            periodClean = re.sub('[^A-Za-z0-9]+', '', period) #Clean comma from period
            hourClean = re.sub('[^A-Za-z0-9:]+', '', hour) #Clean comma from hour
        except ValueError:
            self.send_it(chat_id=chat_id, text="Format is wrong")
            return 0

        ##Check if day format is correct
        if(periodClean not in days):
            self.send_it(chat_id=chat_id, text="Day format is wrong")
        
        ##Check if hour format is correct
        hourFormat = self.isTimeFormat(hourClean)
        if(hourFormat == False): 
            self.send_it(chat_id=chat_id, text= "Hour format is wrong")
            print("HOUR WRONG " + str(hourFormat))
        else: #if everthing is okay.
            try: #try to send the data to the weeklySchedule method
                self.weeklySchedule(periodClean, hourClean, notes, update)
                self.send_it(chat_id=chat_id, text=f"We will notify you every {periodClean} on {hourClean}") #Notify user
            except ValueError:
                self.send_it(chat_id=chat_id, text= "Wrong format!")
                return 0

    #Weekly Scheduler Method
    def weeklySchedule(self, period, hour, note, update):
        chat_id = update.effective_chat.id
        if(period == "monday"): #if given period is Monday, this statement will work
            schedule.every().monday.at(hour).do(lambda: self.send_it(chat_id=chat_id, text=note)) #Schedule a message every monday at given hour
            while True:
                schedule.run_pending()
                time.sleep(1)
        if(period == "tuesday"):
            schedule.every().tuesday.at(hour).do(lambda: self.send_it(chat_id=chat_id, text=note))
            while True:
                schedule.run_pending()
                time.sleep(1)
        if(period == "wednesday"):
            schedule.every().wednesday.at(hour).do(lambda: self.send_it(chat_id=chat_id, text=note))
            while True:
                schedule.run_pending()
                time.sleep(1)
        if(period == "thursday"):
            schedule.every().thursday.at(hour).do(lambda: self.send_it(chat_id=chat_id, text=note))
            while True:
                schedule.run_pending()
                time.sleep(1)
        if(period == "friday"):
            schedule.every().friday.at(hour).do(lambda: self.send_it(chat_id=chat_id, text=note))
            while True:
                schedule.run_pending()
                time.sleep(1)
        if(period == "saturday"):
            schedule.every().saturday.at(hour).do(lambda: self.send_it(chat_id=chat_id, text=note))
            while True:
                schedule.run_pending()
                time.sleep(1)
        if(period == "sunday"):
            schedule.every().sunday.at(hour).do(lambda: self.send_it(chat_id=chat_id, text=note))
            while True:
                schedule.run_pending()
                time.sleep(1)

    def daily(self, update, context):
        chat_id = update.effective_chat.id
        try:
            data_split = (update.message.text).split(" ") #Split data by spaces
            command, hour = data_split[:2] #First two command will be command and hour
            notes = " ".join(data_split[2:]) #Rest of them will be notes
            hourClean = re.sub('[^A-Za-z0-9:]+', '', hour) #Clean comma from hour
        except ValueError:
            self.send_it(chat_id=chat_id, text="Format is wrong") #If there's a ValueError, notify user
            return 0

        ##Check if hour format is correct
        hourFormat = self.isTimeFormat(hourClean)
        if(hourFormat == False):
            self.send_it(chat_id=chat_id, text= "Hour format is wrong") #notify user
            print("HOUR WRONG " + str(hourFormat))
        
        self.dailySchedule(hourClean, notes, update) #Send data to dailySchedule method
        self.send_it(chat_id=chat_id, text=f"We will notify you every day at {hourClean}") #Notify user

    #Daily Scheduler Method
    def dailySchedule(self, hour, note, update):
        chat_id = update.effective_chat.id
        schedule.every().day.at(hour).do(lambda: self.send_it(chat_id=chat_id, text=note)) #Schedule a message every day at given hour
        while True:
            schedule.run_pending()
            time.sleep(1)
    
            

    def main(self):
        updater = Updater(self.TOKEN, use_context=True)
        dp = updater.dispatcher
        dp.add_handler(CommandHandler('start', self.start_message_handler)) #Start message command
        dp.add_handler(CommandHandler('daily', self.daily))                 #Daily command
        dp.add_handler(CommandHandler('weekly', self.weekly))               #Weekly command

        updater.start_polling()
        updater.idle()

b= TelegramBot()
b.main()