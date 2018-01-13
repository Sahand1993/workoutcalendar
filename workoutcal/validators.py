from django.db.models.fields import DateTimeField, TimeField, FloatField, CharField, IntegerField
from django.core.exceptions import ValidationError
from django.utils.datastructures import MultiValueDictKeyError

from .models import LiftActivity, CardioActivity, LiftSerie, CardioSerie
from django.http import QueryDict

class WorkoutDataValidator(object):

	def __init__(self, data):
		"""data is a request.POST object"""
		self.lift_name_fields = AddWorkoutFields('lift_name')
		self.cardio_name_fields = AddWorkoutFields('cardio_name')
		self.sets_fields = AddWorkoutFields('sets')
		self.reps_fields = AddWorkoutFields('reps')
		self.weight_fields = AddWorkoutFields('weight')
		self.duration_fields = AddWorkoutFields('duration')
		self.distance_fields = AddWorkoutFields('distance')

		self.data = data.copy()
		self.max_fields = 500

	def is_valid(self):
		self.check_number_of_fields()
		self.validate_datetime()
		self.data_to_python()
		self.check_activities(LiftActivity, self.lift_name_fields)
		self.check_activities(CardioActivity, self.cardio_name_fields)

		if self.sets_fields.no_of_fields > self.lift_name_fields.no_of_fields:
			# If there are more filled in setsi than filled in lift_stringi, raise error
			raise ValidationError('More sets fields were sent in than lift_string fields')


		# Check on self.lift_name_fields.no_of_fields
		if self.duration_fields.no_of_fields > self.cardio_name_fields.no_of_fields:
			# If there are more durationi than cardio_namei, raise error
			raise ValidationError('More duration fields were sent in than cardio_string fields')

		if self.distance_fields.no_of_fields > self.cardio_name_fields.no_of_fields:
			# If there are more distancei than cardio_namei, raise error
			raise ValidationError('More distance fields were sent in than cardio_string fields')

		for i in range(self.lift_name_fields.no_of_fields):
			if self.data.getlist(self.reps_fields.keybase+str(i)):
				if not (self.data[self.sets_fields.keybase+str(i)] and self.data[self.lift_name_fields.keybase+str(i)]):
					# check that if there is repsi, there is also setsi and lift_stringi
					raise ValidationError('Corrupt data sent to server')

			# check that number of reps fields is the same as the number in sets field
			no_of_sets = self.data[self.sets_fields.keybase+str(i)]
			no_of_reps_fields = len(self.data.getlist(self.reps_fields.keybase+str(i)))

			if no_of_sets:
				if no_of_sets != no_of_reps_fields:
					raise ValidationError('number of repfields does not equal the number provided in setfields for sets{0}.\nNo OF repsfields: {1}\nNo OF sets: {2}'.format(i, no_of_reps_fields, no_of_sets))
			else:
				if not no_of_reps_fields == 0:
					raise ValidationError('setsfield is {0} but no of repsfields is {1}'.format(no_of_sets, no_of_reps_fields))

		for i in range(self.cardio_name_fields.no_of_fields):
			# if there is duration but not cardio_name. if there is distance but not cardio_name
			# Note that we're assuming that there is only one value in querydict for each key, and are thus only interested
			# in looking at the first one. We don't take responsibility for somebody sending in weird forms
			if self.data[self.duration_fields.keybase+str(i)] or self.data[self.distance_fields.keybase+str(i)]:
				if not self.data[self.cardio_name_fields.keybase+str(i)]:
					raise ValidationError('cardio_string field not provided although distance and/or durationfield was found.')

			## More validation?

		return self.data

	def check_number_of_fields(self):
		if len(self.data.keys()) > self.max_fields:
			raise ValidationError('Too many (key, value) pairs in QueryDict')

	def validate_datetime(self):
		datetime_string = self.data['datetime']
		datetimefield = DateTimeField() # To borrow validation code
		self.data['datetime'] = datetimefield.to_python(datetime_string)

	def data_to_python(self):
		"""
		Coerces every value in self.data with a key on the form
		r'(lift_string|cardio_string|sets|reps|weight|duration|distance)[0-9]+'
		to a python type.

		Raises ValidationError if we have any keys in the dictionary not on the above form.
		"""
		self.lift_name_fields.no_of_fields = self.many_querydict_string_to_python(self.lift_name_fields.keybase, CharField)
		self.cardio_name_fields.no_of_fields = self.many_querydict_string_to_python(self.cardio_name_fields.keybase, CharField)
		self.sets_fields.no_of_fields = self.many_querydict_string_to_python(self.sets_fields.keybase, IntegerField)
		self.reps_fields.no_of_fields = self.many_querydict_string_to_python(self.reps_fields.keybase, IntegerField)
		self.weight_fields.no_of_fields = self.many_querydict_string_to_python(self.weight_fields.keybase, FloatField)
		self.duration_fields.no_of_fields = self.many_querydict_string_to_python(self.duration_fields.keybase, FloatField)
		self.distance_fields.no_of_fields = self.many_querydict_string_to_python(self.distance_fields.keybase, FloatField)

		fields_found = sum([self.lift_name_fields.no_of_fields,
							self.cardio_name_fields.no_of_fields,
							self.sets_fields.no_of_fields,
							self.reps_fields.no_of_fields,
							self.weight_fields.no_of_fields,
							self.duration_fields.no_of_fields,
							self.distance_fields.no_of_fields,
						   ], 2) # 1 extra for date and 1 extra for csrfmiddlewaretoken

		if fields_found != len(self.data):
			raise ValidationError("Bad keys in data: "+str(self.data)+"\nfields_found: "+str(fields_found)+"\nlen(self.data): "+str(len(self.data)))

	def many_querydict_string_to_python(self, key_string, field_class):
		keys_matched = 0
		for i in range(self.max_fields):
			try:
				key = key_string+str(i)
				values = self.data.getlist(key)
				if values == []:
					continue
				converted_values = [self.string_to_python(value, field_class) for value in values]
				self.data.setlist(key, converted_values)
				keys_matched += 1
			except KeyError:
				break
		return keys_matched

	def string_to_python(self, string, field_class):

		field_object = field_class()
		value = field_object.to_python(string) if string else None
		return value

	def check_activities(self, model, addworkoutfields):
		"""Checks that lift or cardio activities exist in the database"""
		# We can assume that every lift_name has a number,
		# and is thus on the form lift_name[0-9]+

		for i in range(addworkoutfields.no_of_fields):
			try:
				key = addworkoutfields.keybase+str(i)
				lift_name = self.data[key]
				if not lift_name: # remove the lift_namei from data but also its sets and reps
					self.data.pop(key)
					continue
				if not model.objects.filter(name=lift_name):
					raise ValidationError("key {0} does not exist in database. If you want to have it in your workout, add it to the database.".format(str(key)))
			except MultiValueDictKeyError:
				continue

	def get_lifts_generator(self):

		def lifts_generator():

			for i in range(self.lift_name_fields.no_of_fields): #No of liftseries is as many as lift_name_fields.no_of_fields
				key = self.lift_name_fields.keybase+str(i)
				try:
					lift_name = self.data[key]
				except KeyError:
					continue

				if not lift_name:
					continue
				lift_activity = LiftActivity.objects.filter(name=lift_name)[0]

				key = self.reps_fields.keybase+str(i)
				repslist = self.data.getlist(key)

				key = self.weight_fields.keybase+str(i)
				weightlist = self.data.getlist(key)

				if not len(repslist) == len(weightlist):
					raise ValidationError('self.data contains faulty data. repslist and weightlist for lift does not contain same amount of values.')

				setlist = []
				for i in range(len(repslist)):
					setlist.append({'reps':repslist[i], 'weight':weightlist[i]})

				yield LiftSerie(lift_activity, setlist)

		return lifts_generator

	def get_cardio_generator(self):

		def cardio_generator():

			for i in range(self.cardio_name_fields.no_of_fields):

				key = self.cardio_name_fields.keybase+str(i)
				try:
					cardio_name = self.data[key]
				except KeyError:
					continue
				if not cardio_name:
					continue
				cardio_activity = CardioActivity.objects.filter(name=cardio_name)[0]

				key = self.duration_fields.keybase+str(i)
				duration = self.data[key]

				key = self.distance_fields.keybase+str(i)
				distance = self.data[key]

				yield CardioSerie(cardio_activity, duration, distance)

		return cardio_generator

	def get_datetime(self):
		return self.data['datetime']

class AddWorkoutFields(object):
	"""Just a container for holding field name in json data from user and other things"""
	def __init__(self, keybase):
		self.keybase = keybase #e.g. lift_string
		self.no_of_fields = None