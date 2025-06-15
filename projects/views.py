from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .forms import ProjectForm, ProjectPartForm, TaskForm, ProjectInvitationForm, ProjectMembershipForm
from .models import Project, ProjectPart, Task, ProjectInvitation, ProjectMembership
from django.http import HttpResponseForbidden, HttpResponseRedirect
from django.contrib.auth import get_user_model
User = get_user_model()
from django.contrib import messages



def _get_membership_forms(project):
    memberships = ProjectMembership.objects.filter(project=project).select_related('user')
    forms_list = [
        (membership, ProjectMembershipForm(prefix=str(membership.id), instance=membership))
        for membership in memberships
    ]
    return forms_list


@login_required
def create_project(request):
    if request.method == 'POST':
        form = ProjectForm(request.POST)
        if form.is_valid():
            project = form.save(commit=False)
            project.owner = request.user
            project.save()
            return redirect('home')  # Redirige vers la page d'accueil
    else:
        form = ProjectForm()

    return render(request, 'projects/create_project.html', {'form': form})

@login_required
def edit_project(request, slug):
    project = get_object_or_404(Project, slug=slug)

    if project.owner != request.user:
        return HttpResponseForbidden()

    if request.method == 'POST':
        form = ProjectForm(request.POST, instance=project)
        if form.is_valid():
            form.save()
            return redirect('home')
    else:
        form = ProjectForm(instance=project)

    return render(request, 'projects/edit_project.html', {'form': form, 'project': project})


@login_required
def delete_project(request, slug):
    project = get_object_or_404(Project, slug=slug)

    if project.owner != request.user:
        return HttpResponseForbidden()

    if request.method == 'POST':
        project.delete()
        return redirect('home')

    return render(request, 'projects/delete_project.html', {'project': project})

@login_required
def project_detail(request, slug):
    project = get_object_or_404(Project, slug=slug)
    parts = project.parts.all().prefetch_related('tasks')
    selected_user_id = request.GET.get('assigned_to')

    # 👇 On récupère les membres avec leurs rôles (ProjectMembership)
    memberships = ProjectMembership.objects.filter(project=project).select_related('user')

    # 👇 Récupérer toutes les tâches liées au projet
    all_tasks = Task.objects.filter(part__project=project)
    if selected_user_id:
        all_tasks = all_tasks.filter(assigned_to_id=selected_user_id)

    return render(request, 'projects/project_detail.html', {
        'project': project,
        'parts': parts,
        'tasks': all_tasks,
        'memberships': memberships,  # 👈 le bon nom à utiliser dans le template
        'selected_user_id': int(selected_user_id) if selected_user_id else None
    })


#-------------------------- Particionnage ------------------------------------

# Créer une partie
@login_required
def add_part(request, slug):
    project = get_object_or_404(Project, slug=slug)
    if not is_manager(request.user, project) and request.user != project.owner:
        return HttpResponseForbidden("Accès refusé.")

    if request.method == 'POST':
        form = ProjectPartForm(request.POST)
        if form.is_valid():
            part = form.save(commit=False)
            part.project = project
            part.save()
            return redirect('project_detail', slug=slug)
    else:
        form = ProjectPartForm()
    return render(request, 'projects/add_part.html', {'form': form, 'project': project})

# Modifier une partie
@login_required
def edit_part(request, part_id):
    part = get_object_or_404(ProjectPart, id=part_id)
    project = part.project
    if not is_manager(request.user, project) and request.user != project.owner:
        return HttpResponseForbidden("Accès refusé.")

    if request.method == 'POST':
        form = ProjectPartForm(request.POST, instance=part)
        if form.is_valid():
            form.save()
            return redirect('project_detail', slug=part.project.slug)
    else:
        form = ProjectPartForm(instance=part)
    return render(request, 'projects/edit_part.html', {'form': form, 'part': part})

# Supprimer une partie
@login_required
def delete_part(request, part_id):
    part = get_object_or_404(ProjectPart, id=part_id)
    project = part.project
    if not is_manager(request.user, project) and request.user != project.owner:
        return HttpResponseForbidden("Accès refusé.")

    slug = part.project.slug
    part.delete()
    return redirect('project_detail', slug=slug)

#-------------------------- Tâches ------------------------------------

# Créer une tâche
@login_required
def add_task(request, part_id):
    part = get_object_or_404(ProjectPart, id=part_id)
    project = part.project
    if not is_manager(request.user, project) and request.user != project.owner:
        return HttpResponseForbidden("Accès refusé.")

    if request.method == 'POST':
        form = TaskForm(request.POST, project=project)
        if form.is_valid():
            task = form.save(commit=False)
            task.part = part
            task.save()
            return redirect('project_detail', slug=project.slug)
    else:
        form = TaskForm(project=project)

    return render(request, 'projects/add_task.html', {'form': form, 'part': part})

@login_required
def edit_task(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    project = task.part.project
    if not is_manager(request.user, project) and request.user != project.owner:
        return HttpResponseForbidden("Accès refusé.")

    if request.method == 'POST':
        form = TaskForm(request.POST, instance=task, project=project)
        if form.is_valid():
            form.save()
            return redirect('project_detail', slug=project.slug)
    else:
        form = TaskForm(instance=task, project=project)

    return render(request, 'projects/edit_task.html', {'form': form, 'task': task})

@login_required
def delete_task(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    project = task.part.project
    if not is_manager(request.user, project) and request.user != project.owner:
        return HttpResponseForbidden("Accès refusé.")

    slug = task.part.project.slug
    task.delete()
    return redirect('project_detail', slug=slug)

#-------------------------- Invitations ------------------------------------

@login_required
def invite_to_project(request, slug):
    project = get_object_or_404(Project, slug=slug, owner=request.user)
    if request.method == 'POST':
        form = ProjectInvitationForm(request.POST)
        if form.is_valid():
            invitation = form.save(commit=False)
            invitation.project = project
            invitation.inviter = request.user
            invitation.save()
            return redirect('project_detail', slug=slug)
    else:
        form = ProjectInvitationForm()
    return render(request, 'projects/invite.html', {'form': form, 'project': project})


@login_required
def received_invitations(request):
    invitations = ProjectInvitation.objects.filter(invited_user=request.user, accepted=False)
    return render(request, 'projects/received_invitations.html', {'invitations': invitations})


@login_required
def accept_invitation(request, invitation_id):
    invitation = get_object_or_404(ProjectInvitation, id=invitation_id, invited_user=request.user)
    if invitation.accepted:
        return HttpResponseForbidden("This invitation has already been accepted.")
    ProjectMembership.objects.create(user=request.user, project=invitation.project, role='member')
    invitation.accepted = True
    invitation.save()
    return redirect('project_detail', slug=invitation.project.slug)

from .utils import is_manager  # si tu l'as mis dans utils.py

def some_project_view(request, slug):
    project = get_object_or_404(Project, slug=slug)

    if not is_manager(request.user, project) and project.owner != request.user:
        return HttpResponseForbidden("You don't have permission to do this.")

from django.http import HttpResponseForbidden
from .utils import is_manager

@login_required
def remove_member(request, slug, user_id):
    project = get_object_or_404(Project, slug=slug)
    member_to_remove = get_object_or_404(ProjectMembership, project=project, user__id=user_id)

    # Le propriétaire peut retirer n'importe qui
    if request.user == project.owner:
        member_to_remove.delete()
        messages.success(request, f"{member_to_remove.user.username} a été retiré du projet.")
        return redirect('manage_members', slug=slug)

    # Vérifie que le demandeur est membre
    try:
        requester_membership = ProjectMembership.objects.get(project=project, user=request.user)
    except ProjectMembership.DoesNotExist:
        messages.error(request, "Vous n'êtes pas membre de ce projet.")
        return redirect('manage_members', slug=slug)

    # Un "manager" peut retirer uniquement les membres simples
    if requester_membership.role == 'manager':
        if member_to_remove.role == 'member' and member_to_remove.user != project.owner:
            member_to_remove.delete()
            messages.success(request, f"{member_to_remove.user.username} a été retiré du projet.")
            return redirect('manage_members', slug=slug)
        else:
            messages.error(request, "Vous ne pouvez pas retirer ce membre.")
            return redirect('manage_members', slug=slug)

    # Les membres simples ne peuvent retirer personne
    messages.error(request, "Vous n'avez pas la permission de retirer des membres.")
    return redirect('manage_members', slug=slug)

@login_required
def add_member(request, slug):
    project = get_object_or_404(Project, slug=slug)

    # Vérification des permissions
    if request.user != project.owner:
        try:
            membership = ProjectMembership.objects.get(project=project, user=request.user)
            if membership.role != 'manager':
                return HttpResponseForbidden("Seuls le propriétaire ou les managers peuvent ajouter des membres.")
        except ProjectMembership.DoesNotExist:
            return HttpResponseForbidden("Vous n'êtes pas membre de ce projet.")

    if request.method == 'POST':
        username = request.POST.get('username')
        try:
            user_to_add = User.objects.get(username=username)
        except User.DoesNotExist:
            messages.error(request, "Cet utilisateur n'existe pas.")
            return redirect('manage_members', slug=slug)

        if ProjectMembership.objects.filter(project=project, user=user_to_add).exists():
            messages.error(request, "Cet utilisateur est déjà membre du projet.")
            return redirect('manage_members', slug=slug)

        ProjectMembership.objects.create(project=project, user=user_to_add, role='member')
        messages.success(request, f"{user_to_add.username} a été ajouté au projet.")
        return redirect('manage_members', slug=slug)

    # Cas non POST : on redirige
    return redirect('manage_members', slug=slug)


@login_required
def manage_members(request, slug):
    project = get_object_or_404(Project, slug=slug)
    user = request.user

    memberships = ProjectMembership.objects.filter(project=project).select_related('user')

    try:
        current_user_membership = memberships.get(user=user)
        user_role = current_user_membership.role
    except ProjectMembership.DoesNotExist:
        user_role = None

    user_is_owner = user == project.owner
    user_is_manager = user_role == 'manager'
    can_edit = user_is_owner or user_is_manager

    if request.method == 'POST':
        if 'update_members' in request.POST:
            for membership in memberships:
                if membership.user == project.owner:
                    continue
                form = ProjectMembershipForm(request.POST, prefix=str(membership.id), instance=membership)
                if can_edit and form.is_valid():
                    form.save()
            messages.success(request, "Les rôles ont été mis à jour.")

        elif 'add_member' in request.POST:
            username_to_add = request.POST.get('username')
            if username_to_add:
                try:
                    user_to_add = User.objects.get(username=username_to_add)
                    if user_to_add == project.owner or ProjectMembership.objects.filter(project=project, user=user_to_add).exists():
                        messages.error(request, "Cet utilisateur est déjà membre ou est le propriétaire.")
                    else:
                        ProjectMembership.objects.create(project=project, user=user_to_add, role='member')
                        messages.success(request, f"{user_to_add.username} a été ajouté au projet.")
                        return redirect('manage_members', slug=slug)
                except User.DoesNotExist:
                    messages.error(request, "Cet utilisateur n'existe pas.")
            else:
                messages.error(request, "Veuillez entrer un nom d'utilisateur.")

    forms_list = []
    for membership in memberships:
        form = ProjectMembershipForm(instance=membership, prefix=str(membership.id))
        forms_list.append((membership, form))

    return render(request, 'projects/manage_members.html', {
        'project': project,
        'forms_list': forms_list,
        'user': user,
        'user_is_owner': user_is_owner,
        'user_is_manager': user_is_manager,
        'can_edit': can_edit
    })