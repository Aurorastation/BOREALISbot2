from borealis import BotBorealis
import time

try:
	print("Initializing BOREALIS and its subcomponents.")
	bot = BotBorealis("config.yml")

	print("Initialization completed. Readying subcomponents.")
	bot.setup()

	print("Subcomponents ready. All systems functional.")
	print("Starting BOREALIS.")
	bot.start_borealis()
except Exception as e:
	print("Danger! Exception caught!")
	print(e)

print("Bot exited.")
