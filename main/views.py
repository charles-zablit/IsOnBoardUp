from django.shortcuts import render
from django.http import JsonResponse
from .models import *
from django.db.models import Avg
from json import dumps
from django.utils.timezone import localtime
from datetime import timedelta


# Main view
def MainView(request):
	# Handle the visitor count
	try:
		NumberOfVisitors = Visits.objects.all()[0]
		NumberOfVisitors.Visitors += 1
		NumberOfVisitors.save()
	except:
		Visits(Visitors=1).save()

	# Handle de values to be displayed on the page
	Statistics = Stats.objects.all().order_by('-id')[0]
	IsDown = Statistics.ResponseTime >= 59

	LastCheck = localtime(Statistics.TimeStamp).strftime("%H:%M")

	AverageLoginTime = Stats.objects.exclude(ResponseTime=60.0).aggregate(Avg('ResponseTime'))["ResponseTime__avg"]
	AverageLoginTime  = round(AverageLoginTime, 1)
	
	AverageNumberOfRetries = Stats.objects.aggregate(Avg('NumberOfAttempts'))["NumberOfAttempts__avg"]
	AverageNumberOfRetries = round(AverageNumberOfRetries, 1)

	TotalFailed = Stats.objects.filter(ResponseTime=60.0).count()
	Total = Stats.objects.count()

	DonutData = {
			'total_failed': TotalFailed,
			'total': Total
		}
	
	# Putting everything in a dictionnary
	data = {
		'isdown': IsDown, 
		'averagelogin': AverageLoginTime, 
		'lastcheck': LastCheck,
		'donut_data': dumps(DonutData),
		'visitors_count': NumberOfVisitors.Visitors,
		'averageretry': AverageNumberOfRetries,
		'numberofqueries': Total
		}
	
	return render(request, 'main/index.html', data)

# Secondary view to handle AJAX requests
def get_data(request, request_length):
	# Variables init
	TimeStamps = []
	ResponseTime = []
	NumberOfAttempts = []

	if(request_length==0):
		days = 1/24
	elif(request_length==1):
		days = 1/2
	elif(request_length==2):
		days = 1
	else:
		days = 7
	
	# Generating the queryset
	Statistics = Stats.objects.all().order_by('-TimeStamp')

	# Looping over the queryset to process it
	_i = 0
	_stat = Statistics[_i]
	
	while (localtime(_stat.TimeStamp)).timestamp() > (localtime()-timedelta(days=days)).timestamp():
		TimeStamps.append(localtime(_stat.TimeStamp).strftime("%H:%M"))
		ResponseTime.append(_stat.ResponseTime)
		NumberOfAttempts.append(_stat.NumberOfAttempts)
		_i += 1
		if _i==len(Statistics):
			break
		_stat = Statistics[_i]
	
	TimeStamps = TimeStamps[::-1]
	ResponseTime = ResponseTime[::-1]
	NumberOfAttempts = NumberOfAttempts[::-1]
	
	# Putting everything in a dictionnary
	data = {
		'timestamps': TimeStamps,
		'responsetime': ResponseTime,
		'numberofattempts': NumberOfAttempts
		}
	return JsonResponse(data)