from django.db import models
from django.conf import settings
from django.utils.text import slugify

class Project(models.Model):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='owned_projects')
    title = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    slug = models.SlugField(unique=True, blank=True)  # 👈 Ajout du champ slug
    created_at = models.DateTimeField(auto_now_add=True)

    members = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        through='ProjectMembership',
        related_name='member_projects'
    )

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)  # Génère un slug à partir du titre
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title
    
class ProjectMembership(models.Model):
    ROLE_CHOICES = (
        ('member', 'Member'),
        ('manager', 'Manager'),
    )

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='member')
    date_joined = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'project')

    def __str__(self):
        return f"{self.user.username} - {self.project.title} ({self.role})"

class ProjectPart(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='parts')
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    def __str__(self):
        return f"{self.project.title} - {self.title}"

from django.contrib.auth import get_user_model
User = get_user_model()

class Task(models.Model):
    part = models.ForeignKey(ProjectPart, on_delete=models.CASCADE, related_name='tasks')
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    completed = models.BooleanField(default=False)
    due_date = models.DateField(null=True, blank=True)
    assigned_to = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name='assigned_tasks')

    def __str__(self):
        return self.title

#------------------------------ Invitation ------------------------------------

class ProjectInvitation(models.Model):
    project = models.ForeignKey('Project', on_delete=models.CASCADE, related_name='invitations')
    invited_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='project_invitations')
    inviter = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='sent_invitations')
    created_at = models.DateTimeField(auto_now_add=True)
    accepted = models.BooleanField(default=False)
    
    class Meta:
        unique_together = ('project', 'invited_user')  # empêche les invitations en double

    def __str__(self):
        return f"Invitation for {self.invited_user.username} to {self.project.title}"