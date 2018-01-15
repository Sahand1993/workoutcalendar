import collections

from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.contrib.postgres.fields import JSONField
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone

from workoutcal import fields

class User(AbstractUser):

	REQUIRED_FIELDS = []
	USERNAME_FIELD = 'email'
	email = models.EmailField(
		_('email address'),
		max_length=150,
		unique=True,
		help_text=_('Required. 150 characters or fewer. Must be a valid email address.'),
		error_messages={
			'unique':_("A user with that email address already exists."),
		},
	)

class CustomUserManager(BaseUserManager):
	def _create_user(self, email, password, is_staff, is_superuser, **extra_fields):
		now = timezone.now()
		if not email:
			raise ValueError('email must be set')
		email = self.normalize_email(email)
		user = User(email = email, is_staff=is_staff,
					is_superuser=is_superuser, date_joined=now,
					**extra_fields)
		user.set_password(password)
		user.save()
		return user

	def create_user(self, email, password, **extra_fields):
		return self._create_user(email, password, False, False, **extra_fields)

	def create_superuser(self, email, password, **extra_fields):
		return self._create_user(email, password, True, True, **extra_fields)

class Workout(models.Model):

	datetime = models.DateTimeField()
	user = models.ForeignKey(User, on_delete=models.CASCADE)
	lifts = fields.LiftsField(null=True)
	cardios = fields.CardiosField(null=True)

	def __str__(self):
		return str(self.datetime)+" "+self.user.email

	__repr__ = __str__

class Series(object):
	"""Series is a list of AbstractSerie objects"""
	def __init__(self, series, serie_class):
		self.series = []
		for serie in series:
			if type(serie) != serie_class:
				raise TypeError("List passed to constructor should only contain "+serie_class.__name__+" objects.")
			self.series.append(serie)

class Lifts(Series):
	def __init__(self, series):
		"""	Series is a list of LiftSeries """
		super().__init__(series, LiftSerie)

class Cardios(Series):
	def __init__(self, series):
		"""Cardios is a list of CardioSeries"""
		super().__init__(series, CardioSerie)

class AbstractSerie(object):

	def __init__(self, activity):
		"""activity is an Activity"""
		self.activity_name = activity.name

	def pre_json(self):
		"""	A function that returns a dict version of the serie.
			Should be implemented in subclasses. """
		raise NotImplementedError

	def __str__(self):
		return str(self.pre_json())

class LiftSerie(AbstractSerie):
	"""Represents a lift and the number of reps and weight for each set of it."""
	def __init__(self, lift_activity, setlist):
		"""	lift should be an instance of LiftActivity.
			setlist is a list containing (weight, reps) for each set
			that has been performed.
		"""
		if not (isinstance(setlist, collections.Sequence) and not isinstance(setlist, str)):
			raise TypeError("setlist has to behave as a list and can not be a string.")
		super().__init__(lift_activity)
		self.setlist = setlist

	def pre_json(self):
		return {
			"liftname" : self.activity_name,
			"setlist" : self.setlist,
		}

	def __str__(self):
		return "name: {0}\n(weight, reps): {1}".format(self.activity_name, str(self.setlist))

class CardioSerie(AbstractSerie):
	"""Represents a cardio activity and its duration."""
	def __init__(self, cardio_activity, duration, distance):
		"""activity is an instance of CardioActivity, duration is milliseconds"""

		if duration and not isinstance(duration, (int, float)):
			raise TypeError('duration has to be an int or a float')
		if distance and not isinstance(distance, (int, float)):
			raise TypeError('distance has to be an int or a float')

		super().__init__(cardio_activity)

		self.duration = duration
		self.distance = distance

	def __str__(self):
		return 'name: {0}\n(duration, distance): ({1}, {2})'.format(self.activity_name, self.duration, self.distance)

	def pre_json(self):
		return {
			"cardioname":self.activity_name,
			"duration":self.duration,
			'distance':self.distance,
		}

class Activity(models.Model):

	name = models.CharField(max_length = 100, unique = True)

	def __str__(self):
		return self.name
	__repr__ = __str__

	class Meta:
		abstract = True


class CardioActivity(Activity):
	pass

class LiftActivity(Activity):
	pass