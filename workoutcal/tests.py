from django.test import Client

from django.test import TestCase
from .views import maketable
import datetime


class CalendarViewTests(TestCase):
	date = datetime.datetime(2017, 9, 1)

	def test_table_no_of_rows(self):
		"""Table must have correct number of rows."""
		table = maketable(self.date.year, self.date.month)
		self.assertEquals(len(table), 5)

	def test_table_len_of_rows(self):
		"""Each table row must be 7 days long."""
		table = maketable(self.date.year, self.date.month)
		for i in range(len(table)):
			self.assertEquals(len(table[i]), 7)

	def test_table_no_of_not_none_objects(self):
		"""Table must have correct number of not none cells."""
		table = maketable(self.date.year, self.date.month)
		no_of_days = 0
		for i in range(len(table)):
			for j in range(7):
				if table[i][j] != None:
					no_of_days += 1

	def test_last_day(self):
		"""Last day of table must have correct day number"""
		table = maketable(self.date.year, self.date.month)
		biggest_number = 0
		for i in range(len(table)):
			for j in range(7):
				if table[i][j]:
					if biggest_number < int(table[i][j]):
						biggest_number = int(table[i][j])
		self.assertEquals(biggest_number, 30)

class WorkoutModelTests(TestCase):

	def test_create_and_save_workout(self):
		import datetime

		from workoutcal.models import LiftActivity, Lifts, LiftSerie, CardioActivity, Cardios, CardioSerie, User, Workout

		datetime = datetime.datetime(year=2017, month=12, day=30)

		user = User(email="sahandz@hotmail.com", username="sandi")

		user.save()

		user = User.objects.filter(username="sandi")[0]

		liftactivity = LiftActivity(name="benchpress")
		liftactivity.save()

		liftserie = LiftSerie(liftactivity, [(90, 2), (100, 1)])

		lifts = Lifts([liftserie])

		cardioactivity = CardioActivity(name="running")
		cardioactivity.save()

		cardioserie = CardioSerie(cardioactivity, 2700000)

		cardios = Cardios([cardioserie])

		workout = Workout(datetime = datetime, user=user, lifts=lifts, cardios=cardios)

		workout.save()