from borealis import BotBorealis

bot = BotBorealis("config.yml")

print("Bot created. Setting up.")

bot.setup()

print("Setup done.")
print("Running bot.")

bot.start_borealis()
