from django.conf.urls import url
from . import views

app_name = 'workoutcal'
urlpatterns = [
	url(r'^$', views.redirect_to_calendar),
	url(r'^(?P<year>[0-9]+)/(?P<month>[1-9]|1[0-2])$', views.calendar, name='calendar'),
	url(r'^(?P<workout_id>[0-9]+)/$', views.DetailView.as_view(), name='detail'), #Detail of a workout. Shows lifts, duration, etc. All the attributes.
	url(r'^add/(?P<year>[0-9]+)/(?P<month>[0-9]+)/(?P<day>[0-9]+)(/(?P<id>[0-9]*))?$', views.AddWorkoutView.as_view(), name = 'add_workout'), #Adding a workout for the date in question. Can we change this so ^add/$ is for any date and the url call in template sends the date along?
	url(r'^edit/(?P<id>[0-9]+)/$', views.edit, name='edit'), #Editing an existing workout. id is id of workout object to edit.
	url(r'^delete/(?P<id>[0-9]+)/$', views.delete_workout, name='delete_workout'),
	url(r'^name/$', views.get_contact_form, name='contact_form'),
	url(r'^get_lifts/$', views.get_lifts, name='get_lifts'),
	url(r'^add_lift/$', views.add_lift, name='add_lift'),
	url(r'^get_cardio/$', views.get_cardio, name='get_cardio'),
	url(r'^login/$', views.LoginView.as_view(), name='login'),
	url(r'^logout/$', views.logout_view, name='logout'),
	url(r'^register/$', views.UserFormView.as_view(), name='register'),
	url(r'^username/$', views.get_username, name='username'),
]
