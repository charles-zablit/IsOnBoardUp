from django.core.management.base import BaseCommand, CommandError
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from main.models import *
from time import strftime
from django.utils import timezone
from django.conf import settings
import os
from multiprocessing import Process, Queue

# Initializing the chromedriver
chrome_options = webdriver.ChromeOptions()
if not settings.DEBUG:
	chrome_options.binary_location = os.environ.get("GOOGLE_CHROME_BIN")
chrome_options.add_argument("--headless")
# chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument('--disable-gpu')
chrome_options.add_argument("--disable-notifications")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--incognito")
if not settings.DEBUG:
	driver = webdriver.Chrome(executable_path=os.environ.get("CHROMEDRIVER_PATH"), chrome_options=chrome_options)
else:
	driver = webdriver.Chrome(chrome_options=chrome_options)


def time_url(driver, url, queue):
	driver.get(url)

	if not settings.DEBUG:
		driver.find_element_by_id("username").send_keys(os.getenv("USERNAME"))
		driver.find_element_by_id ("password").send_keys(os.getenv("PASSWORD"))
	else:
		from IsOnBoardUp.auth_tokens import username, password
		driver.find_element_by_id("username").send_keys(username)
		driver.find_element_by_id ("password").send_keys(password)
	
	driver.find_element_by_class_name("bouton-connexion").click()
	navigation_start = driver.execute_script(
			"return window.performance.timing.navigationStart")
	dom_complete = driver.execute_script(
			"return window.performance.timing.domComplete")
	total_time = dom_complete - navigation_start
	total_time = round(total_time/1000, 1)
	queue.put(total_time)


def exec():
	attempts = 0
	total = 60
	url = "https://onboard.ec-nantes.fr"
	while total==60 and attempts<=3:
		driver = webdriver.Chrome()
		attempts += 1
		queue = Queue() #using to get the result
		proc = Process(target=time_url, args=(driver, url, queue,)) #creation of a process calling longfunction with the specified arguments
		proc.start() #lauching the processus on another thread
		try:
			total = queue.get(timeout=60) #getting the result under 1 second or stop
			proc.join() #proper delete if the computation has take less than timeout seconds
		except: #catching every exception type
			proc.terminate() #kill the process
			total = 60
		finally:
			driver.close()
	
	Stat = Stats(TimeStamp=timezone.localtime(timezone.now()), ResponseTime=total, NumberOfAttempts=attempts)
	Stat.save()
	# Make sure to avoid db overflow
	StatLen = Stats.objects.all().count()
	if StatLen > 9000:
		to_delete = Stats.objects.values()[:1].get()
		Stats.objects.filter(id=to_delete['id']).delete()

class Command(BaseCommand):
	def handle(self, *args, **options):
		exec()
		self.stdout.write(self.style.SUCCESS('Success'))
		return