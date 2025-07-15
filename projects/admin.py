from django.contrib import admin
from projects.models import Project, ProjectMembership, ProjectPart, Task
# Register your models here.

admin.site.register(Project)
admin.site.register(ProjectMembership)
admin.site.register(ProjectPart)
admin.site.register(Task)