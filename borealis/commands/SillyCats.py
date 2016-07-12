from .Command import BorealisCommand
import requests

class commandCats(BorealisCommand):
	"""Forces bot.config.updateUsers() to run."""

	@classmethod
	async def doCommand(cls, bot, message, params):

		r = requests.get("http://random.cat/meow")

		if r.status_code != 200:
			reply = "Oh no! I couldn't find any cats!"
		else:
			try:
				data = r.json()

				if data["file"]:
					reply = data["file"]
				else:
					reply = "Oh no! I couldn't find any cats!"
			except ValueError as e:
				reply = "Oh no! I couldn't find any cats!"

		await bot.send_message(message.channel, reply)

		return

	@classmethod
	def getName(cls):
		return "Cats"

	@classmethod
	def getDescription(cls):
		return "Yes. Cats."

	@classmethod
	def getParams(cls):
		return ""

	@classmethod
	def getAuths(cls):
		return []
