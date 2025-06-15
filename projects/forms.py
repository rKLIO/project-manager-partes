from django import forms
from .models import Project, ProjectPart, Task, ProjectInvitation, ProjectMembership
from django.contrib.auth import get_user_model

class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ['title', 'description']

class ProjectPartForm(forms.ModelForm):
    class Meta:
        model = ProjectPart
        fields = ['title', 'description']

class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['title', 'description', 'completed', 'due_date', 'assigned_to']

    def __init__(self, *args, **kwargs):
        project = kwargs.pop('project', None)  # on récupère le projet passé à la vue
        super().__init__(*args, **kwargs)
        if project:
            # Filtrer les membres du projet (via la relation ProjectMembership)
            self.fields['assigned_to'].queryset = User.objects.filter(projectmembership__project=project)
        else:
            self.fields['assigned_to'].queryset = User.objects.none()

User = get_user_model()

class ProjectInvitationForm(forms.ModelForm):
    invited_user = forms.ModelChoiceField(queryset=User.objects.all(), label="User to invite")

    class Meta:
        model = ProjectInvitation
        fields = ['invited_user']

class ProjectMembershipForm(forms.ModelForm):
    class Meta:
        model = ProjectMembership
        fields = ['role']
