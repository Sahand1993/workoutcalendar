from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from django.template import loader
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.views.generic.base import View
from django.contrib.auth import authenticate, login, logout
from django.core.serializers import serialize

from .tables import maketable, addWorkouts
from .forms import NameForm, ContactForm, AddLiftForm, UserForm, LoginForm
from .models import Workout, LiftActivity, CardioActivity, Lifts, Cardios
from .validators import WorkoutDataValidator

from calendar import monthrange, month_name
from datetime import datetime

def first_day_next_month(year, month):
	"""Helper function"""
	if month == 12:
		return {'year':year+1, 'month':1, 'day':1}
	return {'year':year, 'month':month+1, 'day':1}

def get_workouts_in_month(user, year = None, month = None):
	"""	Helper function

		Returns the workouts in the month specified for
		the user with the specified email address.
		Returns those in the current month if date is
		not provided
	"""
	if year and month:

		days_in_month = monthrange(year, month)[1]

	else:

		today = timezone.now()
		year = today.year
		month = today.month

		days_in_month = monthrange(today.year, today.month)[1]

	return Workout.objects.filter(
		datetime__gte = datetime(year=year, month=month, day=1)).filter(
		datetime__lt = datetime(**first_day_next_month(year,month))).filter(
		user = user)

def redirect_to_calendar(request):
	today = timezone.now()
	return calendar(request, year = today.year, month = today.month)

def calendar(request, year = None, month = None):

	if not request.user.is_authenticated:
		return prompt_login(request)

	user_email = request.user.email
	template_name = 'workoutcal/calendar.html'

	if not (year and month):

		today = timezone.now()
		year = today.year
		month = today.month

	else:

		year = int(year)
		month = int(month)

	workouts_in_month = get_workouts_in_month(request.user, year, month)

	table = maketable(year, month)
	table_with_workouts = addWorkouts(table, year, month, workouts_in_month)

	template = loader.get_template(template_name)

	context = {
		'title': 'WorkoutCal',
		'workout_list': workouts_in_month,
		'table': {'year':year, 'month':month, 'table':table_with_workouts},
		'monthname':_(month_name[month]),
	}
	return HttpResponse(template.render(context, request))

class DetailView(View):
	def get(self, request, workout_id):
		if not request.user.is_authenticated:
			return prompt_login(request)

		try:
			workout = Workout.objects.filter(id=workout_id)[0]
		except IndexError:
			return HttpResponse('404')

		#Adding range(len(setlist)) to each liftserie
	#	for serie in workout.lifts.series:
	#		serie.no_of_sets_range = range(len(serie.setlist))

		if not request.user == workout.user:
			return HttpResponse('404')

		template_name = 'workoutcal/detail.html'
		#template_name = 'workoutcal/test.html'
		template = loader.get_template(template_name)

		context = {
			'title': 'Workout Details',
			'workout': workout,
			'datetime': str(workout.datetime),
			'lift_rows': len(workout.lifts.series),
			'cardio_rows': len(workout.cardios.series),
			'no_of_lift_series_range': range(len(workout.lifts.series)),
			'range_list': [range(len(serie.setlist)) for serie in workout.lifts.series],
		}

		return HttpResponse(template.render(context, request))

def delete_workout(request, id):
	if not request.user.is_authenticated:
		return prompt_login(request)

	try:
		workout = Workout.objects.filter(id=id)[0]
	except IndexError:
		return HttpResponse('workout does not exist and can thus not be deleted')
	if request.user == workout.user:
		workout.delete()

	return redirect('workoutcal:calendar', year = workout.datetime.year, month = workout.datetime.month)

class AddWorkoutView(View):
	def get(self, request, year=None, month=None, day=None, id=None):
		template_name = 'workoutcal/addworkout.html'
		template = loader.get_template(template_name)
		date_time = datetime(year=int(year), month=int(month), day=int(day))
		context = {
			'datetime':str(date_time),
			'date':date_time, # this is a datetime type, but used as a date in the template
			'current_name':request.user.username,
			'title':'Add workout',
			'range':range(4),
		}
		return HttpResponse(template.render(context, request))

	def post(self, request, year=None, month=None, day=None, id=None):

		validator = WorkoutDataValidator(request.POST)
		validator.is_valid()

		lift_series = validator.get_lifts_generator()
		cardio_series = validator.get_cardio_generator()

		lifts = Lifts(series = [lift_serie for lift_serie in lift_series()])
		cardios = Cardios(series = [cardio_serie for cardio_serie in cardio_series()])

		workout = Workout(datetime = validator.get_datetime(), user=request.user, lifts = lifts, cardios = cardios)

		workout.save()

		return calendar(request, year, month)

def edit(request):
	return HttpResponse('Edit view.')

def get_name(request):
	if request.method == 'POST':
		form = NameForm(request.POST)
		if form.is_valid():
			# Här ska vi göra något med form.cleaned_data
			return HttpResponseRedirect('/thanks/')
	else:
		form = NameForm()
	return render(request, 'workoutcal/name.html', {'form': form})

def get_contact_form(request):
	if request.method == 'POST':
		form = ContactForm(request.POST) # populate the ContactForm with POST data.
		if form.is_valid():
			# Gör något med data
			return HttpResponseRedirect('/thanks/')
	else:
		form = ContactForm()
	return render(request, 'workoutcal/name.html', {'form': form})

def get_lifts(request):
	if request.method == 'GET':
		search_str = request.GET['lift_name'].lower()
		lift_activities = LiftActivity.objects.filter(name__startswith=search_str)
		data = serialize('json', lift_activities)
		return HttpResponse(data)

def get_cardio(request): # Can we combine get_lifts and get_cardio into one somehow?
	if request.method == 'GET':
		search_str = request.GET['cardio_name'].lower()
		cardio_activities = CardioActivity.objects.filter(name__startswith=search_str)
		data = serialize('json', cardio_activities)
		return HttpResponse(data)

def add_lift(request):
	if request.method == 'POST':
		form = AddLiftForm(request.POST)
		if form.is_valid():
			name = form.cleaned_data['name'].lower()
			try:
				new_lift = Lift(name=name)
			except (NotUniqueError, DuplicateKeyError):
				#Liftname already exists
				pass

			form = AddLiftForm()
	else:
		form = AddLiftForm()
	return render(request, 'workoutcal/addlift.html', {'form':form, 'title':'Add lift'})

class UserFormView(View):
	"""Register"""
	form_class = UserForm
	template_name = 'workoutcal/register.html'

	def get(self, request):
		form = self.form_class(None)
		return render(request, self.template_name, {'form':form})
	def post(self, request):
		form = self.form_class(request.POST)

		if form.is_valid():

			user = form.save(commit=False)

			username = form.cleaned_data['username']
			password = form.cleaned_data['password']
			user.set_password(password)
			user.save()

			user = authenticate(username=username, password=password)

			if user is not None:
				if user.is_active:
					login(request, user)
					return redirect_to_calendar(request)

		return render(request, self.template_name, {'form': form})

class LoginView(View):

	form_class = LoginForm
	template_name = 'workoutcal/login.html'

	def post(self, request):

		form = self.form_class(request.POST)

		if form.is_valid():

			email = form.cleaned_data['email']
			password = form.cleaned_data['password']

			user = authenticate(email = email, password = password)

			if user is not None:

				if user.is_active:
					login(request, user)
					return calendar(request)
			else:
				return render(request, self.template_name, {'form':form, 'custom_error_message':'The user does not exist'})
		else:
			return render(request, self.template_name, {'form':form})

	def get(self, request):

		form = self.form_class(None)

		return render(request, self.template_name, {'form':form})

def logout_view(request):
	logout(request)
	return redirect('workoutcal:login')

def get_username(request):
	return HttpResponse(request.user.username)

def prompt_login(request):
	return render(request, 'workoutcal/prompt_login.html')