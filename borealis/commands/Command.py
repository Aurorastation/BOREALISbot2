class BorealisCommand():
	"""The base class for all commands."""
	def __init__(self):
		pass

	@classmethod
	def doCommand(cls, bot, message, params):
		pass

	@classmethod
	def getName(cls):
		return ""

	@classmethod
	def getDescription(cls):
		return ""

	@classmethod
	def getParams(cls):
		return ""

	@classmethod
	def getAuths(cls):
		return []

	@classmethod
	def verifyParams(cls, params):
		if cls.getParams() == "":
			return True

		params_req = len(cls.getParams().split("> <"))

		return len(params) == params_req
