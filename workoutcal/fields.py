import json

from django.contrib.postgres.fields import JSONField
from workoutcal import models

def parse_lifts(value):
	"""Takes a string of json and turns it into a Lifts object"""
	try:
		series = json.loads(value)
	except TypeError:
		if not isinstance(value, list):
			raise TypeError
		series = value

	serie_objects = []
	for serie in series:
		try:
			liftname = serie['liftname']
		except:
			liftname = None
		try:
			setlist = serie['setlist']
		except KeyError:
			setlist = None
		activity = models.LiftActivity.objects.filter(name=liftname)[0] #We assume that the lift was checked for existence when the value was added to the database
		serie_object = models.LiftSerie(activity, setlist)
		serie_objects.append(serie_object)

	lifts_object = models.Lifts(serie_objects)
	return lifts_object

def parse_cardios(value):
	"""Takes a string of json and turns it into a Cardios object. Or takes a converted python object structure and converts them into Cardios object"""
	try:
		series = json.loads(value)
	except TypeError:
		series = value

	serie_objects = []
	for serie in series:
		cardioname = serie['cardioname']
		try:
			duration = serie['duration']
			distance = serie['distance']
		except KeyError:
			duration, distance = None, None
		activity = models.CardioActivity(name=cardioname)
		serie_object = models.CardioSerie(activity, duration, distance)
		serie_objects.append(serie_object)

	cardios_object = models.Cardios(serie_objects)
	return cardios_object

class LiftsField(JSONField):
	"""Field representing a models.Lifts object"""

	def from_db_value(self, value, expression, connection, context):
		if value is None:
			return value
		new_val = parse_lifts(value)
		return new_val

	def to_python(self, value):
		if isinstance(value, models.Lifts):
			return value
		if value is None:
			return value
		return parse_lifts(value)

	def get_prep_value(self, value):
		if not value:
			return value
		lifts_pre_json = [serie_object.pre_json() for serie_object in value.series]
		return json.dumps(lifts_pre_json)

class CardiosField(JSONField):
	"""Field representing a models.Cardios object"""

	def from_db_value(self, value, expression, connection, context):
		if value is None:
			return value
		return parse_cardios(value)

	def to_python(self, value):
		if isinstance(value, models.Cardios):
			return value
		if value is None:
			return value
		return parse_cardios(value)

	def get_prep_value(self, value):
		if value == None:
			return value
		cardios_pre_json = [serie_object.pre_json() for serie_object in value.series]
		return json.dumps(cardios_pre_json)

