from django.contrib import admin
from .models import Student,Material, MaterialRequest, Group, LabApparelRequest, Liability

admin.site.register(Student)
admin.site.register(Material)
admin.site.register(MaterialRequest)
admin.site.register(Group)
admin.site.register(LabApparelRequest)
admin.site.register(Liability)
