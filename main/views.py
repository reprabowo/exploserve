from datetime import datetime
from django.conf import settings
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import HttpResponse, HttpResponseForbidden, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from .permissions import can_manage_user, can_delete_user
from .utils import fetch_sinta_scores, fetch_sinta_inst_scores, fetch_sinta_ps_scores
from .models import (
    Profile,
    Institution,
    ProgramStudi,
    ResearchGrant,
    FooterColumn,
    Announcement,
    AnnouncementFile,
)
from .forms import (
    UserRegistrationForm,
    ProfileForm,
    InstitutionForm,
    ProgramStudiForm,
    ResearchGrantForm,
    FooterColumnForm,
    AnnouncementForm,
    AnnouncementFilesForm,
)

# ======================================================
# Home, Dashboard, and Profile Views
# ======================================================


def home(request):
    announcements = Announcement.objects.filter(audience="sitewide").order_by(
        "-created_at"
    )[:6]
    return render(request, "index.html", {"announcements": announcements})


def dashboard(request):
    profiles = Profile.objects.all()
    if not request.user.is_authenticated:
        return redirect("login")
    user_inst = request.user.profile.institution
    # For System Owner and System Admin, show all announcements that have a selected institution.
    if request.user.profile.role in ["system_owner", "system_admin"]:
        announcements = Announcement.objects.filter(institution__isnull=False).order_by(
            "-created_at"
        )[:6]
    else:
        announcements = Announcement.objects.filter(institution=user_inst).order_by(
            "-created_at"
        )[:3]
    context = {
        "announcements": announcements,
    }
    return render(request, "dashboard.html", {
        "profiles": profiles,
        "announcements": announcements,
    })


@login_required
def profile_detail(request, user_id=None):
    # 1) pick which user you’re viewing
    if user_id is None:
        user_obj = request.user
    else:
        user_obj = get_object_or_404(User, id=user_id)

    profile_obj = get_object_or_404(Profile, user=user_obj)

    # 2) compute two flags, based on your existing logic
    can_edit   = can_manage_user(request.user, user_obj)
    can_delete = can_delete_user(request.user, user_obj)

    # 3) render, passing the flags alongside your existing context
    return render(request, "profile_detail.html", {
        "user_obj":    user_obj,
        "profile_obj": profile_obj,
        "can_edit":    can_edit,
        "can_delete":  can_delete,
    })


@login_required
def edit_profile(request):
    # Get the target user and associated profile.
    user_obj = request.user
    profile_obj = get_object_or_404(Profile, user=user_obj)
    
    # 1. permission check
    if not can_manage_user(request.user, user_obj):
        return HttpResponseForbidden("You do not have permission to manage this user.")
    
    # Store the original password hash so we can restore it if needed.
    original_password = user_obj.password
            
    if request.method == "POST":
        # Make a mutable copy of POST data so we can check the password field.
        post_data = request.POST.copy()
        new_password = post_data.get("password", "").strip()
        
        # Instantiate the forms with the POST data and the existing instances. 
        user_form = UserRegistrationForm(post_data, instance=user_obj)
        profile_form = ProfileForm(
            request.POST, 
            request.FILES, 
            instance=profile_obj,
            current_user=request.user
        )
        
        if user_form.is_valid() and profile_form.is_valid():
            # 2. save user (with optional password change)
            user = user_form.save(commit=False)
            if new_password:
                user.set_password(new_password)
            else:
                user.password = original_password
            user.save()

            # make sure session keeps working if they changed their own password
            if new_password and user == request.user:
                update_session_auth_hash(request, user)
                
            # 3. prevent lower level roles from toggling reviewer flag
            if request.user.profile.role not in [
                "system_owner",
                "system_admin",
                "institution_admin",
            ]:
                profile_form.cleaned_data[
                    "is_reviewer_assigned"
                ] = profile_obj.is_reviewer_assigned

            # 4. now process the profile
            profile = profile_form.save(commit=False)

            # 5. only scrape and assign SINTA fields if there really is a SINTA ID
            if profile.sinta_id:
                (
                    first_score,
                    second_score,
                    third_score,
                    fourth_score,
                    scraped_name,
                    name_match
                ) = fetch_sinta_scores(
                    profile.sinta_id,                   # only the person's SINTA ID
                    local_name=profile.nama_lengkap     # if your function accepts this kwarg
                )
                
                if first_score is not None:
                    profile.sinta_score = first_score
                if second_score is not None:
                    profile.sinta_score3 = second_score
                if third_score is not None:
                    profile.sinta_scoresc = third_score
                if fourth_score is not None:
                    profile.sinta_scorego = fourth_score

                # always store scraped name & match flag (even if False)
                profile.sinta_name_scraped = scraped_name or ""
                profile.sinta_name_match   = bool(name_match)

            # 6. finally save profile
            profile_obj.save()

            return redirect("profile_detail")
            
    else:
        user_form = UserRegistrationForm(instance=user_obj)
        profile_form = ProfileForm(
            instance=profile_obj,
            current_user=request.user
        )
        
    return render(
        request, 
        "user_form.html", {
            "user_form":    user_form,
            "profile_form": profile_form,
        }
    )


def fetch_sinta_data(request, sinta_id):
    if request.method != "POST":
        return redirect("home")

    profile_obj = get_object_or_404(Profile, sinta_id=sinta_id)

    # unpack six values now
    first_score, second_score, third_score, fourth_score, sinta_name, name_match = fetch_sinta_scores(
        sinta_id,
        local_name=profile_obj.nama_lengkap
    )

    if first_score is not None:
        profile_obj.sinta_score = first_score
    if second_score is not None:
        profile_obj.sinta_score3 = second_score
    if third_score is not None:
        profile_obj.sinta_scoresc = third_score
    if fourth_score is not None:
        profile_obj.sinta_scorego = fourth_score

    # always set scraped name & match flag (so you clear it if no match)
    profile_obj.sinta_name_scraped = sinta_name or ""
    profile_obj.sinta_name_match   = bool(name_match)
    

    profile_obj.save()

    # redirect back to your profile detail url
    return redirect(reverse("profile_detail", args=[profile_obj.user.id]))


# ======================================================
# User Management Views (System Owner Only)
# ======================================================


def is_system_owner(user):
    try:
        return user.profile.role == "system_owner"
    except Profile.DoesNotExist:
        return False


@login_required
@user_passes_test(
    lambda u: u.is_authenticated
    and u.profile.role in ["system_owner", "system_admin", "institution_admin"]
    )
def user_list(request):
    users = User.objects.select_related("profile").all()

    # Filtering
    name_query = request.GET.get("name", "")
    email_query = request.GET.get("email", "")
    role_query = request.GET.get("role", "")
    institution_id = request.GET.get("institution", "")

    if name_query:
        users = users.filter(profile__nama_lengkap__icontains=name_query)
    if email_query:
        users = users.filter(email__icontains=email_query)
    if role_query:
        users = users.filter(profile__role=role_query)
    if institution_id:
        users = users.filter(profile__institution__id=institution_id)

    # Default sort: ID descending
    users = users.order_by("-id")

    # Pagination
    show_all = request.GET.get("show_all")
    if not show_all:
        paginator = Paginator(users, 10)  # 10 users per page
        page_number = request.GET.get("page")
        users = paginator.get_page(page_number)
    else:
        paginator = None  # skip pagination if "show all" is used

    return render(
        request,
        "user_list.html",
        {
            "users": users,
            "paginator": paginator,
            "roles": Profile.ROLE_CHOICES,
            "institutions": Institution.objects.all(),
            "show_all": show_all,
        },
    )


@login_required
@user_passes_test(
    lambda u: u.is_authenticated
    and u.profile.role in ["system_owner", "system_admin", "institution_admin"]
)
def create_user(request):
    if request.method == "POST":
        user_form = UserRegistrationForm(request.POST)
        # pass current_user so your ProfileForm __init__ can adjust role/institution fields
        profile_form = ProfileForm(
            request.POST,
            request.FILES,
            current_user=request.user
        )

        if user_form.is_valid() and profile_form.is_valid():
            # require a password
            if not user_form.cleaned_data["password"]:
                user_form.add_error("password", "Password is required.")
                return render(request, "user_form.html", {
                    "user_form": user_form,
                    "profile_form": profile_form,
                })

            # save the user
            user = user_form.save(commit=False)
            user.set_password(user_form.cleaned_data["password"])
            user.save()

            # save the profile
            profile = profile_form.save(commit=False)
            profile.user = user

            # if institution_admin, force the profile's institution to your own
            if request.user.profile.role == "institution_admin":
                profile.institution = request.user.profile.institution

            profile.save()

            # ─── EMAIL SEND ────────────────────────────────────────────────────────
            # Build a login link
            login_url = request.build_absolute_uri(
                reverse("login")
            )
            subject = "Welcome to ExploServe!"
            message = (
                f"Hello {profile.nama_lengkap},\n\n"
                "Your account has been created.  You can log in here:\n"
                f"{login_url}\n\n"
                "Thank you for joining ExploServe.\n"
            )
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
                fail_silently=False,
            )
            # ────────────────────────────────────────────────────────────────────────

            return redirect("user_list")

    else:
        user_form = UserRegistrationForm()
        profile_form = ProfileForm(current_user=request.user)

    return render(request, "user_form.html", {
        "user_form": user_form,
        "profile_form": profile_form,
    })


@login_required
def update_user(request, user_id):
    # Get the target user and associated profile.
    user_obj    = get_object_or_404(User, id=user_id)
    profile_obj = get_object_or_404(Profile, user=user_obj)

    # 1. permission check
    if not can_manage_user(request.user, user_obj):
        return HttpResponseForbidden("You do not have permission to manage this user.")

    # Store the original password hash so we can restore it if needed.
    original_password = user_obj.password

    if request.method == "POST":
        # Make a mutable copy of POST data so we can check the password field.
        post_data    = request.POST.copy()
        new_password = post_data.get("password", "").strip()

        # Instantiate the forms with the POST data and the existing instances. 
        user_form    = UserRegistrationForm(post_data, instance=user_obj)
        profile_form = ProfileForm(
            request.POST, 
            request.FILES, 
            instance=profile_obj,
            current_user=request.user
        )

        if user_form.is_valid() and profile_form.is_valid():
            # 2. save user (with optional password change)
            user = user_form.save(commit=False)
            if new_password:
                user.set_password(new_password)
            else:
                user.password = original_password
            user.save()

            # make sure session keeps working if they changed their own password
            if new_password and user == request.user:
                update_session_auth_hash(request, user)

            # 3. prevent lower level roles from toggling reviewer flag
            if request.user.profile.role not in [
                "system_owner", 
                "system_admin", 
                "institution_admin"
            ]:
                profile_form.cleaned_data[
                    "is_reviewer_assigned"
                ] = profile_obj.is_reviewer_assigned

            # 4. now process the profile
            profile = profile_form.save(commit=False)

            # 5. only scrape and assign SINTA fields if there really is a SINTA ID
            if profile.sinta_id:
                (
                    first_score,
                    second_score,
                    third_score,
                    fourth_score,
                    scraped_name,
                    name_match
                ) = fetch_sinta_scores(
                    profile.sinta_id,                   # only the person's SINTA ID
                    local_name=profile.nama_lengkap     # if your function accepts this kwarg
                )

                if first_score is not None:
                    profile.sinta_score = first_score
                if second_score is not None:
                    profile.sinta_score3 = second_score
                if third_score is not None:
                    profile.sinta_scoresc = third_score
                if fourth_score is not None:
                    profile.sinta_scorego = fourth_score

                # always store scraped name & match flag (even if False)
                profile.sinta_name_scraped = scraped_name or ""
                profile.sinta_name_match   = bool(name_match)

            # 6. finally save profile
            profile.save()

            return redirect("user_list")

    else:
        user_form    = UserRegistrationForm(instance=user_obj)
        profile_form = ProfileForm(
            instance=profile_obj,
            current_user=request.user
        )

    return render(
        request, 
        "user_form.html", {
            "user_form":    user_form,
            "profile_form": profile_form,
        }
    )


@login_required
def delete_user(request, user_id):
    user_obj = get_object_or_404(User, id=user_id)

    # Check if the current user can delete the target user.
    if not can_delete_user(request.user, user_obj):
        return HttpResponseForbidden("You do not have permission to delete this user.")

    if request.method == "POST":
        user_obj.delete()
        return redirect("user_list")

    return render(request, "user_confirm_delete.html", {"user": user_obj})


def parse_score(score_str):
    if not score_str:
        return -1  # treat missing values as lowest
    score_str = score_str.replace(".", "").replace(",", ".")
    try:
        return float(score_str)
    except ValueError:
        return -1


@login_required
def user_list_public(request):
    query = request.GET.get("q", "")
    institution_id = request.GET.get("institution")
    program_id = request.GET.get("program")
    role = request.GET.get("role")
    sort = request.GET.get("sort")

    profiles = Profile.objects.select_related(
        "user", "institution", "program_studi"
    ).all()

    # Apply filters
    if query:
        profiles = profiles.filter(
            Q(nama_lengkap__icontains=query) | Q(research_interest__icontains=query)
        )
    if institution_id:
        profiles = profiles.filter(institution__id=institution_id)
    if program_id:
        profiles = profiles.filter(program_studi__id=program_id)
    if role:
        profiles = profiles.filter(role=role)

    # Apply sorting
    if sort == "name":
        profiles = profiles.order_by("nama_lengkap")
    elif sort == "sinta":
        profiles = list(profiles)
        profiles = [p for p in profiles if p.sinta_score]
        profiles.sort(key=lambda p: parse_score(p.sinta_score), reverse=True)
    elif sort == "sinta3":
        profiles = list(profiles)
        profiles = [p for p in profiles if p.sinta_score3]
        profiles.sort(key=lambda p: parse_score(p.sinta_score3), reverse=True)
    elif sort == "scopus":
        profiles = list(profiles)
        profiles = [p for p in profiles if p.sinta_scoresc]
        profiles.sort(key=lambda p: parse_score(p.sinta_scoresc), reverse=True)
    elif sort == "google":
        profiles = list(profiles)
        profiles = [p for p in profiles if p.sinta_scorego]
        profiles.sort(key=lambda p: parse_score(p.sinta_scorego), reverse=True)
    else:
        profiles = profiles.order_by("nama_lengkap")

    # Pagination (10 per page)
    show_all = request.GET.get("show", "") == "all"
    if show_all:
        page_obj = profiles
        is_paginated = False
    else:
        paginator = Paginator(profiles, 10)
        page_number = request.GET.get("page")
        page_obj = paginator.get_page(page_number)
        is_paginated = paginator.num_pages > 1

    context = {
        "page_obj": page_obj,
        "paginator": paginator if not show_all else None,
        "is_paginated": is_paginated,
        "institutions": Institution.objects.all(),
        "programs": ProgramStudi.objects.all(),
        "roles": Profile.ROLE_CHOICES,
    }

    return render(request, "user_list_public.html", context)


# ======================================================
# Institution Public Views
# ======================================================

def institution_list(request):
    search_query = request.GET.get("search", "").strip()
    akreditasi_filter = request.GET.get("akreditasi", "")
    klaster_filter = request.GET.get("klaster", "")
    show_all = request.GET.get("show") == "all"

    institutions = Institution.objects.all()

    if search_query:
        institutions = institutions.filter(name__icontains=search_query)

    if akreditasi_filter:
        institutions = institutions.filter(akreditasi=akreditasi_filter)

    if klaster_filter:
        institutions = institutions.filter(klaster_pt=klaster_filter)

    if not show_all:
        paginator = Paginator(institutions, 10)  # 10 per page
        page_number = request.GET.get("page")
        page_obj = paginator.get_page(page_number)
    else:
        page_obj = institutions

    return render(
        request,
        "institution_list.html",
        {
            "institutions": page_obj,
            "search_query": search_query,
            "akreditasi_filter": akreditasi_filter,
            "klaster_filter": klaster_filter,
            "show_all": show_all,
            "is_paginated": not show_all and institutions.count() > 10,
        },
    )


def institution_profile(request, institution_id):
    institution = get_object_or_404(Institution, id=institution_id)
    query = request.GET.get("q", "").strip()

    study_programs = institution.study_programs.all()
    all_researchers = Profile.objects.filter(institution=institution)

    if query:
        # Narrow down researchers based on the search
        filtered_researchers = all_researchers.filter(
            Q(nama_lengkap__icontains=query)
            | Q(gelar_depan__icontains=query)
            | Q(gelar_belakang__icontains=query)
            | Q(user__email__icontains=query)
            | Q(program_studi__nama_program_studi__icontains=query)
        )

        # Limit study programs to those referenced in results
        program_ids = filtered_researchers.values_list(
            "program_studi_id", flat=True
        ).distinct()
        study_programs = study_programs.filter(id__in=program_ids)
    else:
        filtered_researchers = all_researchers

    # Pair each program with its affiliated researchers
    programs_with_researchers = []
    for program in study_programs:
        affiliated = filtered_researchers.filter(program_studi=program)
        programs_with_researchers.append((program, affiliated))

    # Researchers with no program
    other_researchers = filtered_researchers.filter(program_studi__isnull=True)

    return render(
        request,
        "institution_profile.html",
        {
            "institution": institution,
            "programs_with_researchers": programs_with_researchers,
            "other_researchers": other_researchers,
            "query": query,
        },
    )


# ======================================================
# Institution Management Views
# ======================================================


def is_institution_manager(user):
    try:
        return user.profile.role in [
            "system_owner",
            "system_admin",
            "institution_admin",
        ]
    except Profile.DoesNotExist:
        return False


@login_required
@user_passes_test(is_institution_manager)
def institution_manage_list(request):
    # ——————————————————————————————————————————————
    # 1) Base queryset by role
    # ——————————————————————————————————————————————
    user_role = request.user.profile.role
    if user_role in ["system_owner", "system_admin"]:
        qs = Institution.objects.all()
    elif user_role == "institution_admin":
        qs = Institution.objects.filter(pk=request.user.profile.institution.pk)
    else:
        qs = Institution.objects.none()

    # ——————————————————————————————————————————————
    # 2) Pull filter & pagination params
    # ——————————————————————————————————————————————
    search_query   = request.GET.get("search", "").strip()
    klaster_filter = request.GET.get("klaster", "").strip()
    akreditasi_filter = request.GET.get("akreditasi", "").strip()
    show_all       = request.GET.get("show", "").lower() == "all"
    page_number    = request.GET.get("page")

    # ——————————————————————————————————————————————
    # 3) Apply filters
    # ——————————————————————————————————————————————
    if search_query:
        qs = qs.filter(name__icontains=search_query)
    if klaster_filter:
        qs = qs.filter(klaster_pt=klaster_filter)
    if akreditasi_filter:
        qs = qs.filter(akreditasi=akreditasi_filter)

    # ——————————————————————————————————————————————
    # 4) Paginate unless “show=all”
    # ——————————————————————————————————————————————
    if not show_all:
        paginator    = Paginator(qs.order_by("name"), 10)
        institutions = paginator.get_page(page_number)
        is_paginated = institutions.has_other_pages()
    else:
        # show everything
        institutions = qs.order_by("name")
        is_paginated = False

    # ——————————————————————————————————————————————
    # 5) Render with exactly the context your template expects
    # ——————————————————————————————————————————————
    return render(request, "institution_manage_list.html", {
        "institutions":    institutions,    # Page (if paginated) or full QS
        "is_paginated":    is_paginated,
        "search_query":    search_query,
        "klaster_filter":  klaster_filter,
        "akreditasi_filter": akreditasi_filter,
        # template uses request.GET.show=="all" to render the “Paginate” link
    })


@login_required
@user_passes_test(is_institution_manager)
def create_institution(request):
    # Institutional Admin should not be allowed to create new institutions
    if request.user.profile.role == "institution_admin":
        return HttpResponse("Not authorized", status=403)

    if request.method == "POST":
        form = InstitutionForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect("institution_manage_list")
    else:
        form = InstitutionForm()
    return render(request, "institution_form.html", {"form": form, "action": "Create"})


@login_required
@user_passes_test(is_institution_manager)
def update_institution(request, institution_id):
    institution = get_object_or_404(Institution, id=institution_id)

    # Institutional Admin can only update their own institution
    if request.user.profile.role == "institution_admin":
        if institution.pk != request.user.profile.institution.pk:
            return HttpResponse("Not authorized", status=403)

    if request.method == "POST":
        form = InstitutionForm(request.POST, request.FILES, instance=institution)
        if form.is_valid():
            # Save the institution form first
            institution = form.save()

            # Now, fetch and update the SINTA scores if a SINTA ID exists
            sinta_id = institution.sinta_id  # get sinta_id from the instance
            if sinta_id:
                first_inst_score, second_inst_score = fetch_sinta_inst_scores(sinta_id)
                if first_inst_score:
                    institution.sinta_score = first_inst_score
                if second_inst_score:
                    institution.sinta_score3 = second_inst_score
                institution.save()

            return redirect("institution_profile", institution_id=institution.id)
    else:
        form = InstitutionForm(instance=institution)
    return render(request, "institution_form.html", {"form": form, "action": "Update"})


@login_required
@user_passes_test(is_institution_manager)
def delete_institution(request, institution_id):
    institution = get_object_or_404(Institution, id=institution_id)
    if request.user.profile.role == "institution_admin":
        return HttpResponse("Not authorized", status=403)
    if request.method == "POST":
        institution.delete()
        return redirect("institution_manage_list")
    return render(
        request, "institution_confirm_delete.html", {"institution": institution}
    )


# ======================================================
# Study Program Management Views
# ======================================================


@login_required
@user_passes_test(is_institution_manager)
def programstudi_list(request):
    programs = ProgramStudi.objects.all()
    user = request.user
    query = request.GET.get("q", "")
    jenjang = request.GET.get("jenjang", "")
    status = request.GET.get("status", "")
    akreditasi_ps = request.GET.get("akreditasi_ps", "")
    sort = request.GET.get("sort", "nama_program_studi")
    show_all = request.GET.get("show", "") == "all"

    # Limit to own institution for institution_admin
    if user.profile.role == "institution_admin":
        programs = programs.filter(institution=user.profile.institution)

    # Apply filters
    if query:
        programs = programs.filter(
            Q(nama_program_studi__icontains=query)
            | Q(ps_id__icontains=query)
            | Q(sinta_id__icontains=query)
        )

    if jenjang:
        programs = programs.filter(jenjang=jenjang)
    if status:
        programs = programs.filter(status=status)
    if akreditasi_ps:
        programs = programs.filter(akreditasi_ps=akreditasi_ps)

    # Apply sorting
    if sort in ["nama_program_studi", "sinta_score", "jenjang"]:
        programs = programs.order_by(sort)

    # Pagination
    if not show_all:
        paginator = Paginator(programs, 10)
        page_number = request.GET.get("page")
        page_obj = paginator.get_page(page_number)
    else:
        page_obj = programs  # show all

    context = {
        "programs": page_obj,
        "query": query,
        "jenjang": jenjang,
        "status": status,
        "akreditasi_ps": akreditasi_ps,
        "sort": sort,
        "show_all": show_all,
        "is_paginated": not show_all and page_obj.has_other_pages(),
    }
    return render(request, "programstudi_list.html", context)


@login_required
@user_passes_test(is_institution_manager)
def create_programstudi(request):
    if request.method == "POST":
        form = ProgramStudiForm(request.POST, current_user=request.user)
        if form.is_valid():
            program = form.save(commit=False)
            # Force institution_admin to use their own institution
            if request.user.profile.role == "institution_admin":
                program.institution = request.user.profile.institution
            program.save()
            return redirect("programstudi_list")
    else:
        form = ProgramStudiForm(current_user=request.user)
    return render(request, "programstudi_form.html", {"form": form, "action": "Create"})


@login_required
@user_passes_test(is_institution_manager)
def update_programstudi(request, program_id):
    program = get_object_or_404(ProgramStudi, id=program_id)

    # Authorization check for institutional admin
    if request.user.profile.role == "institution_admin":
        if program.institution != request.user.profile.institution:
            return HttpResponse("Not authorized", status=403)

    if request.method == "POST":
        form = ProgramStudiForm(
            request.POST, instance=program, current_user=request.user
        )
        if form.is_valid():
            program = form.save()

            # ✅ Triple check that all 3 IDs exist
            if (
                program.institution
                and program.institution.sinta_id
                and program.institution.pt_id
                and program.sinta_id
            ):

                from main.utils import fetch_sinta_ps_scores

                first_ps_score, second_ps_score = fetch_sinta_ps_scores(
                    program.institution.sinta_id,  # inst_sinta_id
                    program.institution.pt_id,  # inst_pt_id
                    program.sinta_id,  # ps_sinta_id
                )

                if first_ps_score:
                    program.sinta_score = first_ps_score
                if second_ps_score:
                    program.sinta_score3 = second_ps_score
                program.save()

            return redirect("programstudi_detail", program_id=program.id)
    else:
        form = ProgramStudiForm(instance=program, current_user=request.user)

    return render(request, "programstudi_form.html", {"form": form, "action": "Update"})


@login_required
@user_passes_test(is_institution_manager)
def delete_programstudi(request, program_id):
    program = get_object_or_404(ProgramStudi, id=program_id)
    if request.method == "POST":
        program.delete()
        return redirect("programstudi_list")
    return render(request, "programstudi_confirm_delete.html", {"program": program})


@login_required
def programstudi_detail(request, program_id):
    program = get_object_or_404(ProgramStudi, id=program_id)
    researchers = Profile.objects.filter(program_studi=program)

    first_ps_score = None
    second_ps_score = None

    if program.institution and program.institution.sinta_id and program.sinta_id:
        first_ps_score, second_ps_score = fetch_sinta_ps_scores(
            inst_sinta_id=program.institution.sinta_id,
            inst_pt_id=program.institution.pt_id,
            ps_sinta_id=program.sinta_id,
        )

    context = {
        "program": program,
        "researchers": researchers,
        "sinta_score": first_ps_score,
        "sinta_score3": second_ps_score,
    }
    return render(request, "programstudi_detail.html", context)


# ======================================================
# Research Grant Management Views
# ======================================================


@login_required
@user_passes_test(is_institution_manager)
def research_grant_list(request):
    grants = ResearchGrant.objects.all()
    return render(request, "research_grant_list.html", {"grants": grants})


@login_required
@user_passes_test(is_institution_manager)
def create_research_grant(request):
    if request.method == "POST":
        form = ResearchGrantForm(request.POST, request.FILES)
        if form.is_valid():
            grant = form.save(commit=False)
            grant.created_by = request.user
            grant.save()
            return redirect("research_grant_list")
    else:
        form = ResearchGrantForm()
    return render(
        request, "research_grant_form.html", {"form": form, "action": "Create"}
    )


@login_required
@user_passes_test(is_institution_manager)
def update_research_grant(request, grant_id):
    grant = get_object_or_404(ResearchGrant, id=grant_id)
    if request.method == "POST":
        form = ResearchGrantForm(request.POST, request.FILES, instance=grant)
        if form.is_valid():
            form.save()
            return redirect("research_grant_list")
    else:
        form = ResearchGrantForm(instance=grant)
    return render(
        request, "research_grant_form.html", {"form": form, "action": "Update"}
    )


@login_required
@user_passes_test(is_institution_manager)
def delete_research_grant(request, grant_id):
    grant = get_object_or_404(ResearchGrant, id=grant_id)
    if request.method == "POST":
        grant.delete()
        return redirect("research_grant_list")
    return render(request, "research_grant_confirm_delete.html", {"grant": grant})


@login_required
def research_grant_detail(request, grant_id):
    grant = get_object_or_404(ResearchGrant, id=grant_id)
    return render(request, "research_grant_detail.html", {"grant": grant})


# ======================================================
# Announcement Management Views
# ======================================================


@login_required
@user_passes_test(is_institution_manager)
def announcement_list(request):
    user_role = request.user.profile.role

    # Base queryset
    if user_role in ["system_owner", "system_admin"]:
        qs = Announcement.objects.all()
    elif user_role == "institution_admin":
        qs = Announcement.objects.filter(institution=request.user.profile.institution)
    else:
        qs = Announcement.objects.none()

    # — Title search —
    search = request.GET.get("search", "").strip()
    if search:
        qs = qs.filter(title__icontains=search)

    # — Audience filter —
    audience = request.GET.get("audience", "")
    if audience in ["sitewide", "selected_institution"]:
        qs = qs.filter(audience=audience)

    # — Institution filter —
    inst = request.GET.get("institution", "")
    if inst.isdigit():
        qs = qs.filter(institution_id=int(inst))

    # — Date range filters —
    date_from = request.GET.get("date_from")
    if date_from:
        try:
            df = datetime.strptime(date_from, "%Y-%m-%d").date()
            qs = qs.filter(created_at__date__gte=df)
        except ValueError:
            pass

    date_to = request.GET.get("date_to")
    if date_to:
        try:
            dt = datetime.strptime(date_to, "%Y-%m-%d").date()
            qs = qs.filter(created_at__date__lte=dt)
        except ValueError:
            pass

    # Always show newest first
    qs = qs.order_by("-created_at")

    return render(
        request,
        "announcement_list.html",
        {
            "announcements": qs,
            # so we can rebuild selects in the template:
            "search": search,
            "audience": audience,
            "selected_inst": inst,
            "date_from": date_from,
            "date_to": date_to,
            "all_institutions": Institution.objects.all(),
        },
    )


@login_required
@user_passes_test(is_institution_manager)
def create_announcement(request):
    if request.method == 'POST':
        form = AnnouncementForm(request.POST, request.FILES, user=request.user)
        if form.is_valid():
            ann = form.save(commit=False)
            ann.created_by = request.user
            ann.save()
            # handle attachments
            for f in request.FILES.getlist('attachment_files'):
                AnnouncementFile.objects.create(announcement=ann, file=f)
            return redirect('announcement_list')
    else:
        form = AnnouncementForm(user=request.user)

    return render(request, 'announcement_form.html', {
        'form': form, 'action': 'Create', 'announcement': None
    })


@login_required
@user_passes_test(is_institution_manager)
def update_announcement(request, announcement_id):
    ann = get_object_or_404(Announcement, id=announcement_id)

    # institutional_admin can only edit their own institution’s announcements
    if (request.user.profile.role == 'institution_admin'
            and ann.institution != request.user.profile.institution):
        return HttpResponseForbidden("Not allowed")

    if request.method == 'POST':
        form = AnnouncementForm(request.POST, request.FILES, instance=ann, user=request.user)
        if form.is_valid():
            ann = form.save()
            for f in request.FILES.getlist('attachment_files'):
                AnnouncementFile.objects.create(announcement=ann, file=f)
            return redirect('announcement_list')
    else:
        form = AnnouncementForm(instance=ann, user=request.user)

    return render(request, 'announcement_form.html', {
        'form': form, 'action': 'Update', 'announcement': ann
    })


@login_required
@user_passes_test(is_institution_manager)
def delete_attachment_file(request, file_id):
    attach = get_object_or_404(AnnouncementFile, id=file_id)
    ann = attach.announcement
    if request.method == 'POST':
        attach.delete()
        return redirect('update_announcement', announcement_id=ann.id)
    return render(request, 'announcement_attachment_confirm_delete.html', {
        'attachment': attach, 'announcement': ann
    })


@login_required
@user_passes_test(is_institution_manager)
def delete_announcement(request, announcement_id):
    announcement = get_object_or_404(Announcement, id=announcement_id)
    if request.method == "POST":
        announcement.delete()
        return redirect("announcement_list")
    return render(
        request, "announcement_confirm_delete.html", {"announcement": announcement}
    )


def announcement_detail(request, announcement_id):
    announcement = get_object_or_404(Announcement, id=announcement_id)
    return render(request, "announcement_detail.html", {"announcement": announcement})


def announcement_public_list(request):
    qs = Announcement.objects.filter(audience="sitewide")

    # title search
    search = request.GET.get("search", "").strip()
    if search:
        # you can also add content__icontains if you like
        qs = qs.filter(title__icontains=search)

    # date from
    date_from = request.GET.get("date_from")
    if date_from:
        try:
            df = datetime.strptime(date_from, "%Y-%m-%d").date()
            qs = qs.filter(created_at__date__gte=df)
        except ValueError:
            pass

    # date to
    date_to = request.GET.get("date_to")
    if date_to:
        try:
            dt = datetime.strptime(date_to, "%Y-%m-%d").date()
            qs = qs.filter(created_at__date__lte=dt)
        except ValueError:
            pass

    # sort
    sort = request.GET.get("sort", "newest")
    if sort == "oldest":
        qs = qs.order_by("created_at")
    else:
        qs = qs.order_by("-created_at")

    return render(
        request,
        "announcement_public_list.html",
        {
            "announcements": qs,
        },
    )


def dashboard_announcements(request):
    if not request.user.is_authenticated:
        return redirect("login")
    # Fetch only non-sitewide announcements (assuming these have an associated institution)
    announcements = Announcement.objects.filter(institution__isnull=False).order_by(
        "-created_at"
    )
    return render(
        request, "dashboard_announcements.html", {"announcements": announcements}
    )


@login_required
@user_passes_test(is_institution_manager)
def dashboard_announcements(request):
    # 1) base: only institution‑specific announcements
    qs = Announcement.objects.filter(audience="selected_institution")

    # 2) role‑scoping
    role = request.user.profile.role
    if role in ["system_owner", "system_admin"]:
        ann = qs
    else:
        ann = qs.filter(institution=request.user.profile.institution)

    # 3) search by title?
    search = request.GET.get("search", "").strip()
    if search:
        ann = ann.filter(title__icontains=search)

    # 4) date from
    date_from = request.GET.get("date_from")
    if date_from:
        try:
            df = datetime.strptime(date_from, "%Y-%m-%d").date()
            ann = ann.filter(created_at__date__gte=df)
        except ValueError:
            pass

    # 5) date to
    date_to = request.GET.get("date_to")
    if date_to:
        try:
            dt = datetime.strptime(date_to, "%Y-%m-%d").date()
            ann = ann.filter(created_at__date__lte=dt)
        except ValueError:
            pass

    # 6) sort order
    sort = request.GET.get("sort", "newest")
    if sort == "oldest":
        ann = ann.order_by("created_at")
    else:
        ann = ann.order_by("-created_at")

    return render(
        request,
        "dashboard_announcements.html",
        {
            "announcements": ann,
        },
    )


# ======================================================
# Footer Management Views
# ======================================================


def is_top_admin(user):
    try:
        return user.profile.role in ["system_owner", "system_admin"]
    except Exception:
        return False


@login_required
@user_passes_test(is_top_admin)
def footer_column_list(request):
    columns = FooterColumn.objects.all()
    return render(request, "footer_column_list.html", {"columns": columns})


@login_required
@user_passes_test(is_top_admin)
def create_footer_column(request):
    if request.method == "POST":
        form = FooterColumnForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("footer_column_list")
    else:
        form = FooterColumnForm()
    return render(
        request, "footer_column_form.html", {"form": form, "action": "Create"}
    )


@login_required
@user_passes_test(is_top_admin)
def update_footer_column(request, column_id):
    column = get_object_or_404(FooterColumn, id=column_id)
    if request.method == "POST":
        form = FooterColumnForm(request.POST, instance=column)
        if form.is_valid():
            form.save()
            return redirect("footer_column_list")
    else:
        form = FooterColumnForm(instance=column)
    return render(
        request, "footer_column_form.html", {"form": form, "action": "Update"}
    )


@login_required
@user_passes_test(is_top_admin)
def delete_footer_column(request, column_id):
    column = get_object_or_404(FooterColumn, id=column_id)
    if request.method == "POST":
        column.delete()
        return redirect("footer_column_list")
    return render(request, "footer_column_confirm_delete.html", {"column": column})


# ======================================================
# Search Functionality
# ======================================================


def search(request):
    query = request.GET.get("q", "")
    profiles = Profile.objects.filter(
        Q(nama_lengkap__icontains=query)
        | Q(gelar_depan__icontains=query)
        | Q(gelar_belakang__icontains=query)
    )
    institutions = Institution.objects.filter(
        Q(name__icontains=query)
        | Q(address__icontains=query)
        | Q(description__icontains=query)
    )
    programstudi = ProgramStudi.objects.filter(Q(nama_program_studi__icontains=query))
    researchgrant = ResearchGrant.objects.filter(
        Q(title__icontains=query) | Q(description__icontains=query)
    )
    context = {
        "query": query,
        "profiles": profiles,
        "institutions": institutions,
        "programstudi": programstudi,
        "researchgrant": researchgrant,
    }
    return render(request, "search_results.html", context)


@login_required
def test_upload(request):
    if request.method == "POST":
        files = request.FILES.getlist("files")
        for f in files:
            try:
                af = AnnouncementFile.objects.create(
                    announcement=Announcement.objects.first(),  # Just for testing
                    file=f,
                )
                print("Test saved file:", af.file.url)
            except Exception as e:
                print("Test error saving file:", e)
        return render(request, "test_upload.html", {"uploaded": files})
    return render(request, "test_upload.html")

@login_required
def ajax_load_programs(request):
    inst_id = request.GET.get('institution')
    qs = ProgramStudi.objects.filter(institution_id=inst_id).order_by('nama_program_studi')
    # build a list of dicts with exactly the keys you want
    data = [
        {"id": p.id, "name": p.nama_program_studi}
        for p in qs
    ]
    return JsonResponse(data, safe=False)

