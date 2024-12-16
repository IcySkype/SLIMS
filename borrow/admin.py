from django.contrib import admin
from .models import Student,Material, MaterialRequest, Group, LabApparelRequest, Liability, Request, ItemInRequest


admin.site.register(Material)
admin.site.register(Request)
admin.site.register(MaterialRequest)
admin.site.register(ItemInRequest)
admin.site.register(LabApparelRequest)
admin.site.register(Group)
admin.site.register(Student)
admin.site.register(Liability)
