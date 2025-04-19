from django import forms
from django.contrib.auth.models import User
from django.forms.widgets import ClearableFileInput
from django.utils.translation import gettext_lazy as _
from .models import Profile, Institution, ProgramStudi, ResearchGrant, FooterColumn, Announcement


class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput, 
        label=_("Password"), 
        required=False
    )
    
    class Meta:
        model = User
        fields = ['email', 'password']
        labels = {
            'email': _("Email"),
        }
    
    def save(self, commit=True):
        user = super().save(commit=False)
        # Automatically set the username to the email address.
        # Alternatively, you could create a unique username by appending a random number.
        user.username = self.cleaned_data['email']
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user
        
class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = [
            'nama_lengkap',
            'gelar_depan',
            'gelar_belakang',
            'role',
            'nidn_nidk',
            'jenjang_pendidikan',
            'jabatan_akademik',
            'institution',
            'program_studi',
            'research_interest',
            'sinta_id',
            'sinta_score',
            'sinta_score3', 
            'sinta_scoresc',
            'sinta_scorego',        
            'orcid_id',
            'is_reviewer_assigned',
            'no_hp',
            'profile_photo',
        ]
        labels = {
            'nama_lengkap': _("Nama Lengkap"),
            'gelar_depan': _("Gelar Depan"),
            'gelar_belakang': _("Gelar Belakang"),
            'role': _("Role"),
            'nidn_nidk': _("NIDN/NIDK"),
            'jenjang_pendidikan': _("Jenjang Pendidikan"),
            'jabatan_akademik': _("Jabatan Akademik"),
            'institution': _("Institusi"),
            'program_studi': _("Program Studi"),
            'research_interest': _("Research Interest"),
            'sinta_id': _("Sinta ID"),
            'sinta_score': _("Sinta Score Overall"),
            'sinta_score3': _("Sinta Score 3 Years"),
            'sinta_scoresc': _("Sinta Score Scopus"),
            'sinta_scorego': _("Sinta Score Google Scholar"),
            'orcid_id': _("Orcid ID"),
            'is_reviewer_assigned': _("Research Reviewer Assigned"),
            'no_hp': _("No HP"),
            'profile_photo': _("Profile Photo"),
        }
        widgets = {
            'role': forms.Select(attrs={'class': 'form-select'}),
            'institution': forms.Select(attrs={'class': 'form-select', 'id':'id_institution'}),
            'program_studi':forms.Select(attrs={'class': 'form-select', 'id':'id_program_studi'}),
            # Make sinta_score read-only
            'sinta_score': forms.TextInput(attrs={'readonly': 'readonly', 'class': 'form-control'}),
            'sinta_score3': forms.TextInput(attrs={'readonly': 'readonly', 'class': 'form-control'}),
            'sinta_scoresc': forms.TextInput(attrs={'readonly': 'readonly', 'class': 'form-control'}),
            'sinta_scorego': forms.TextInput(attrs={'readonly': 'readonly', 'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        current_user = kwargs.pop('current_user', None)
        super().__init__(*args, **kwargs)

        if current_user:
            user_role = current_user.profile.role

            # ✅ Disable institution selection for lower roles
            if user_role in ["institution_admin", "researcher", "reviewer", "student", "technician"]:
                self.fields['institution'].widget.attrs['disabled'] = 'disabled'

            # ✅ Adjust available role choices
            full_choices = Profile._meta.get_field('role').choices
            if user_role == "system_owner":
                allowed_choices = full_choices
            elif user_role == "system_admin":
                allowed_choices = [r for r in full_choices if r[0] in ["system_admin", "institution_admin"]]
            elif user_role == "institution_admin":
                allowed_choices = [r for r in full_choices if r[0] in ["researcher", "reviewer", "student", "technician"]]
            else:
                allowed_choices = []

            self.fields['role'].choices = allowed_choices

        # ✅ Filter program_studi by institution
        if self.instance and self.instance.institution:
            self.fields['program_studi'].queryset = ProgramStudi.objects.filter(institution=self.instance.institution)
        else:
            self.fields['program_studi'].queryset = ProgramStudi.objects.none()


class InstitutionForm(forms.ModelForm):
    class Meta:
        model = Institution
        fields = [
            'name',
            'logo',
            'address',
            'description',
            'website',
            'pt_id',
            'sinta_id',
            'sinta_score',
            'sinta_score3',
            'klaster_pt',
            'akreditasi',
            'nama_pimpinan_pt',
            'sebutan_pimpinan_pt',
            'nidn_pimpinan_pt',
            'nama_pimpinan_unit_ppm',
            'nama_unit_ppm',
            'sebutan_pimpinan_unit_ppm',
            'nidn_pimpinan_unit_ppm',
            'badan_penyelenggara',
            'logo_bp',
            'website_bp',
        ]
        labels = {
            'name': _("Institution Name"),
            'logo': _("Logo"),
            'address': _("Address"),
            'description': _("Description"),
            'website': _("Website"),
            'pt_id': _("PT ID"),
            'sinta_id': _("Sinta ID"),
            'sinta_score': _("Sinta Score Overall"),
            'sinta_score3': _("Sinta Score 3 Years"),
            'klaster_pt': _("Klaster PT"),
            'akreditasi': _("Akreditasi"),
            'nama_pimpinan_pt': _("Nama Pimpinan PT"),
            'sebutan_pimpinan_pt': _("Sebutan Pimpinan PT"),
            'nidn_pimpinan_pt': _("NIDN Pimpinan PT"),
            'nama_pimpinan_unit_ppm': _("Nama Pimpinan Unit Pengelola PPM"),
            'nama_unit_ppm': _("Nama Unit Pengelola PPM"),
            'sebutan_pimpinan_unit_ppm': _("Sebutan Pimpinan Unit Pengelola PPM"),
            'nidn_pimpinan_unit_ppm': _("NIDN Pimpinan Unit Pengelola PPM"),
            'badan_penyelenggara': _("Badan Penyelenggara"),
            'logo_bp': _("Logo Badan Penyelenggara"),
            'website_bp': _("Website Badan Penyelenggara"),
        }
        widgets = {
            'klaster_pt': forms.Select(attrs={'class': 'form-select'}),
            'akreditasi': forms.Select(attrs={'class': 'form-select'}),
            'sebutan_pimpinan_pt': forms.Select(attrs={'class': 'form-select'}),
            # Make sinta_score read-only
            'sinta_score': forms.TextInput(attrs={'readonly': 'readonly', 'class': 'form-control'}),
            'sinta_score3': forms.TextInput(attrs={'readonly': 'readonly', 'class': 'form-control'}),
        }

class ProgramStudiForm(forms.ModelForm):
    class Meta:
        model = ProgramStudi
        fields = [
            'institution',
            'nama_program_studi',
            'ps_id',
            'sinta_id',
            'sinta_score',
            'sinta_score3', 
            'jenjang',
            'status',
            'akreditasi_ps',
        ]
        labels = {
            'institution': _("Institution"),
            'nama_program_studi': _("Nama Program Studi"),
            'ps_id': _("PS ID"),
            'sinta_id': _("Sinta ID"),
            'sinta_score': _("Sinta Score Overall"),
            'sinta_score3': _("Sinta Score 3 Years"),
            'jenjang': _("Jenjang"),
            'status': _("Status"),
            'akreditasi_ps': _("Akreditasi PS"),
        }
        widgets = {
            'institution': forms.Select(attrs={'class': 'form-select'}),
            # Make sinta_score read-only
            'sinta_score': forms.TextInput(attrs={'readonly': 'readonly', 'class': 'form-control'}),
            'sinta_score3': forms.TextInput(attrs={'readonly': 'readonly', 'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        current_user = kwargs.pop('current_user', None)
        super().__init__(*args, **kwargs)

        if current_user and current_user.profile.role == "institution_admin":
            self.fields['institution'].initial = current_user.profile.institution
            self.fields['institution'].widget.attrs['disabled'] = 'disabled'

class ResearchGrantForm(forms.ModelForm):
    class Meta:
        model = ResearchGrant
        fields = [
            'title', 'description', 'offered_to', 'start_year', 'end_year', 'institution',
            'qualification_criteria', 'identitas_usulan', 'substansi_dan_luaran',
            'rab', 'dokumen_pendukung', 'konfirmasi_usulan',
            'approved_by_pt', 'approved_by_ppm', 'reviewer', 'review_score',
            'final_decision', 'announcement'
        ]
        labels = {
            'title': _("Title"),
            'description': _("Description"),
            'offered_to': _("Offered To"),
            'start_year': _("Start Year"),
            'end_year': _("End Year"),
            'institution': _("Institution"),
            'qualification_criteria': _("Qualification Criteria"),
            'identitas_usulan': _("Identitas Usulan"),
            'substansi_dan_luaran': _("Substansi dan Luaran"),
            'rab': _("RAB"),
            'dokumen_pendukung': _("Dokumen Pendukung"),
            'konfirmasi_usulan': _("Konfirmasi Usulan"),
            'approved_by_pt': _("Approved by Pimpinan PT"),
            'approved_by_ppm': _("Approved by Unit Pengelola PPM"),
            'reviewer': _("Assigned Reviewer"),
            'review_score': _("Review Score"),
            'final_decision': _("Final Decision"),
            'announcement': _("Announcement"),
        }
        widgets = {
            'offered_to': forms.Select(attrs={'class': 'form-select'}),
            'institution': forms.Select(attrs={'class': 'form-select'}),
            'qualification_criteria': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'identitas_usulan': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'substansi_dan_luaran': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'rab': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'konfirmasi_usulan': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'announcement': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

class FooterColumnForm(forms.ModelForm):
    class Meta:
        model = FooterColumn
        fields = ['title', 'content', 'order']
        labels = {
            'title': _("Title"),
            'content': _("Content (HTML allowed)"),
            'order': _("Order"),
        }
        widgets = {
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
            'order': forms.NumberInput(attrs={'class': 'form-control'}),
        }

class AnnouncementForm(forms.ModelForm):
    class Meta:
        model = Announcement
        fields = [
            "title", 
            "audience", 
            "institution",
            "content", 
            "image"
        ]
        widgets = {
            "title": forms.TextInput(attrs={'class': 'form-control'}),
            'audience': forms.RadioSelect(),
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
            'institution': forms.Select(attrs={'class': 'form-select', 'id': 'institution-field'}),
        }

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user

        # 1) Limit institution choices by role
        if user and hasattr(user, 'profile') and user.profile.role == 'institution_admin':
            self.fields['institution'].queryset = Institution.objects.filter(
                pk=user.profile.institution.pk
            )
        else:
            self.fields['institution'].queryset = Institution.objects.all()

        # 2) Set default audience _only_ when creating
        if not self.instance.pk:
            if user and hasattr(user, 'profile') and user.profile.role == 'institution_admin':
                self.fields['audience'].initial = 'selected_institution'
                self.fields['institution'].initial = user.profile.institution.pk
            else:
                self.fields['audience'].initial = 'sitewide'

        # 3) Figure out which audience value is “active” (POST > instance > initial)
        aud = (
            (self.data.get('audience') if hasattr(self, 'data') else None)
            or (self.instance.audience if self.instance.pk else None)
            or self.fields['audience'].initial
        )

        # 4) If sitewide—or if the user is an institutional_admin—disable the dropdown
        if aud == 'sitewide' or (user and user.profile.role == 'institution_admin'):
            self.fields['institution'].widget.attrs['disabled'] = True


class MultiFileInput(ClearableFileInput):
    allow_multiple_selected = True

class AnnouncementFilesForm(forms.Form):
    attachment_files = forms.FileField(
        widget=MultiFileInput(attrs={'multiple': True, 'class': 'form-control'}),
        required=False,
        label="File Attachments"
    )
    
    def clean_attachment_files(self):
        # Return the raw list of files from the request.
        return self.files.getlist('attachment_files')

