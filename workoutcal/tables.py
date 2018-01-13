from datetime import datetime
from calendar import monthrange


def maketable(year, month):
	"""Makes a table for the same month as date is in. returns: [[1, 2, 3, 4, 5, 6, 7][8, 9, ...][...][...][...][...][29, 30, None, None, None, None, None]]"""

	weekday_of_first = datetime(year, month, 1).weekday()
	days_in_month = monthrange(year, month)[1]

	required_cells_in_html_table = days_in_month + weekday_of_first  # the number of cells in a month table, including the ones that are not part of the month, excluding the ones that come after the last day of the month.

	if required_cells_in_html_table % 7 == 0:
		rows_in_html_table = int(required_cells_in_html_table / 7)
	else:
		rows_in_html_table = int(required_cells_in_html_table // 7 + 1)

	table = []
	iday = 1

	row = []

	# adding the first row
	for k in range(weekday_of_first):  # empty cells before start of month
		row.append(None)

	row.append(str(iday))  # day 1
	iday += 1

	for l in range(7 - (weekday_of_first + 1)):  # rest of the days in the row
		row.append(str(iday))
		iday += 1

	table.append(row)  # add the row to the table

	# Adding the rest of the rows
	for i in range(rows_in_html_table - 1):
		row = []
		for j in range(7):  # Add the row
			if iday <= days_in_month:
				row.append(str(iday))
				iday += 1
			else:
				row.append(None)
		table.append(row)
	return table

def addWorkouts(tableIn, year, month, workouts = None):
	"""Takes table and the year and month it's for and returns a table of tuples (day_no, workoutobj) corresponding to the old table."""
	tableOut = []

	for rowIn in tableIn: # Change table elements to dicts
		rowOut = []
		for element in rowIn:
			rowOut.append({'day':element})
		tableOut.append(rowOut)

	if workouts:
		# Add the workouts
		for row in tableOut:
			for element in row:
				for workout in workouts:#Maybe not so efficient
					if not element['day']:
						continue
					if (year, month, int(element['day'])) == (workout.datetime.year, workout.datetime.month, workout.datetime.day):
						element['workout'] = workout
	else:
		for row in tableOut:
			for element in row:
				element['workout'] = None

	return tableOut
