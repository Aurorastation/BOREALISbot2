from .Command import BorealisCommand
import requests

class commandPenguins(BorealisCommand):
	"""Forces bot.config.updateUsers() to run."""

	@classmethod
	async def doCommand(cls, bot, message, params):

		r = requests.get("http://penguin.wtf/")

		if r.status_code != 200:
			reply = "Nope, no penguins here. Sad."
		else:
			try:
				reply = r.content.decode(r.encoding)
			except Exception as e:
				reply = "Nope, no penguins here. Sad."

		await bot.send_message(message.channel, reply)

		return

	@classmethod
	def getName(cls):
		return "Penguins"

	@classmethod
	def getDescription(cls):
		return "Pingus are obviously superior to cats, though."

	@classmethod
	def getParams(cls):
		return ""

	@classmethod
	def getAuths(cls):
		return []
