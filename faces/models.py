from django.db import models
import datetime 
from settings import MEDIA_URL

# Create your models here.

class Face (models.Model):
	name = models.CharField(max_length=512)
	file = models.FileField(upload_to='userfiles', blank=True, null=True)
	created = models.DateTimeField(auto_now_add=True, blank=True, null=True)
	
	class Meta:
		ordering = ['-created']


	@property
	def pic(self):
		# return self.file
		return (MEDIA_URL+ self.file.name)


