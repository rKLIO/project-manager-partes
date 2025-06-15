from .models import ProjectMembership

def is_manager(user, project):
    return ProjectMembership.objects.filter(user=user, project=project, role='manager').exists()

def get_user_role(user, project):
    if project.owner == user:
        return 'owner'
    try:
        membership = ProjectMembership.objects.get(user=user, project=project)
        return membership.role
    except ProjectMembership.DoesNotExist:
        return None

