from django.shortcuts import render, render_to_response
from django.http import HttpResponse

def home(request):
	# home_html = """ <h1>Hello, First site with Django 1.8</h1>
	# 	<a href="/blog/">blog</a><br>
	# 	<a href="/polls/">polls</a><br>"""
	# return HttpResponse(home_html)
	return render(request, 'firstsite/index-bootstrap.html') #, {'question': question})
	#return render_to_response('static/index-bootstrap.html')
