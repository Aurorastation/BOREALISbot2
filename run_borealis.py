from borealis import BotBorealis
import time

while True:
	bot = None

	try:
		print("Welcome to BOREALIS.")
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

	print("Deleting bot!")
	# Delete the bot, run it again.
	del bot

	# Sleep for a bit before restarting!
	time.sleep(60)
	print("Restarting loop.\n\n\n")

# Should never get here, but just in case.
print("We somehow exited the main loop. :ree:")
input("Press Enter to exit.")
