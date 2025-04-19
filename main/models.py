from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.db.models.signals import pre_save, post_delete
from django.dispatch import receiver
import os, uuid
# Make sure you have imported Institution and ProgramStudi if used below


def profile_photo_upload_path(instance, filename):
    """
    Rename profile photos to:
      MEDIA_ROOT/profiles/photos/user_<user_id>_<timestamp>.<ext>
    """
    ext = filename.split('.')[-1].lower()
    ts  = timezone.now().strftime("%Y%m%d%H%M%S")
    name = f"user_{instance.user.id}_{ts}.{ext}"
    return os.path.join("profiles", "photos", name)

def institution_logo_upload_path(instance, filename):
    """
    Rename institution logo to:
      MEDIA_ROOT/institutions/logos/institution_<institution_id>_<timestamp>.<ext>
    """
    ext = filename.split('.')[-1].lower()
    ts  = timezone.now().strftime("%Y%m%d%H%M%S")
    name = f"user_{instance.institution.id}_{ts}.{ext}"
    return os.path.join("institutions", "logos", name)

def announcement_file_upload_path(instance, filename):
    """
    Rename announcement attachments to:
      MEDIA_ROOT/announcements/files/announcement_<announcement_id>_<uuid>.<ext>
    """
    ext = filename.split('.')[-1].lower()
    uid = uuid.uuid4().hex
    name = f"announcement_{instance.announcement.id}_{uid}.{ext}"
    return os.path.join("announcements", "files", name)

def announcement_image_upload_path(instance, filename):
    """
    Rename uploaded announcement images to:
      MEDIA_ROOT/announcements/images/announcement_<uuid>_<timestamp>.<ext>
    """
    ext = os.path.splitext(filename)[1].lower()                # “.jpg”, “.png”, etc
    ts  = timezone.now().strftime("%Y%m%d%H%M%S")               # e.g. “20250416…”
    uid = uuid.uuid4().hex                                      # e.g. “9f1c…”  
    pk  = instance.id if instance.id else uid
    new_name = f"announcement_{pk}_{ts}{ext}"
    return os.path.join("announcements", "images", new_name)

def delete_file(path):
    """Safely delete a file if it exists on disk."""
    if path and os.path.isfile(path):
        os.remove(path)
        

class Institution(models.Model):
    name = models.CharField(max_length=255, unique=True, verbose_name=_("Institution Name"))
    logo = models.ImageField(upload_to='institutions/logos/', blank=True, null=True, verbose_name=_("Logo"))
    address = models.TextField(blank=True, null=True, verbose_name=_("Address"))
    description = models.TextField(blank=True, null=True, verbose_name=_("Description"))
    website = models.URLField(blank=True, null=True, verbose_name=_("Website"))
    pt_id = models.CharField(max_length=100, blank=True, null=True, verbose_name=_("PT ID"))
    sinta_id = models.CharField(max_length=100, blank=True, null=True, unique=True, verbose_name=_("Sinta ID"))
    sinta_score = models.CharField(max_length=100, blank=True, null=True, verbose_name=_("Sinta Score"))
    sinta_score3 = models.CharField(max_length=100, blank=True, null=True, verbose_name=_("Sinta Score 3"))  
      
    KLASTER_PT_CHOICES = [
        ('mandiri', _('Klaster Mandiri')),
        ('utama', _('Klaster Utama')),
        ('madya', _('Klaster Madya')),
        ('pratama', _('Klaster Pratama')),
        ('binaan', _('Klaster Binaan')),
    ]
    klaster_pt = models.CharField(max_length=20, choices=KLASTER_PT_CHOICES, blank=True, null=True, verbose_name=_("Klaster PT"))

    AKREDITASI_CHOICES = [
    ('internasional', 'Internasional'),
    ('unggul', 'Unggul'),
    ('baik_sekali', 'Baik Sekali'),
    ('baik', 'Baik'),
    ('a', 'A'),
    ('b', 'B'),
    ('c', 'C'),
    ('tidak_terakreditasi', 'Tidak Terakreditasi'),
    ]
    akreditasi = models.CharField(max_length=50, choices=AKREDITASI_CHOICES, blank=True, null=True, verbose_name=_("Akreditasi"))
    
    nama_pimpinan_pt = models.CharField(max_length=255, blank=True, null=True, verbose_name=_("Nama Pimpinan PT"))

    SEBUTAN_PIMPINAN_PT_CHOICES = [
        ('rektor', _('Rektor')),
        ('ketua', _('Ketua')),
        ('direktur', _('Direktur')),
    ]
    sebutan_pimpinan_pt = models.CharField(max_length=50, choices=SEBUTAN_PIMPINAN_PT_CHOICES, blank=True, null=True, verbose_name=_("Sebutan Pimpinan PT"))
    
    nidn_pimpinan_pt = models.CharField(max_length=100, blank=True, null=True, verbose_name=_("NIDN Pimpinan PT"))
    nama_pimpinan_unit_ppm = models.CharField(max_length=255, blank=True, null=True, verbose_name=_("Nama Pimpinan Unit Pengelola PPM"))
    nama_unit_ppm = models.CharField(max_length=255, blank=True, null=True, verbose_name=_("Nama Unit Pengelola PPM"))
    sebutan_pimpinan_unit_ppm = models.CharField(max_length=100, blank=True, null=True, verbose_name=_("Sebutan Pimpinan Unit Pengelola PPM"))
    nidn_pimpinan_unit_ppm = models.CharField(max_length=100, blank=True, null=True, verbose_name=_("NIDN Pimpinan Unit Pengelola PPM"))
    
    badan_penyelenggara = models.CharField(max_length=255, unique=False, verbose_name=_("Badan Penyelenggara"))
    logo_bp = models.ImageField(upload_to='institution_logo_upload_path', blank=True, null=True, verbose_name=_("Logo BP"))
    website_bp = models.URLField(blank=True, null=True, verbose_name=_("Website BP"))

    def __str__(self):
        return self.name


class ProgramStudi(models.Model):
    institution = models.ForeignKey(
        Institution, 
        on_delete=models.CASCADE, 
        related_name='study_programs', 
        verbose_name=_("Institution")
    )
    nama_program_studi = models.CharField(max_length=255, verbose_name=_("Nama Program Studi"))
    ps_id = models.CharField(max_length=100, blank=True, null=True, verbose_name=_("PS ID"))

    JENJANG_CHOICES = [
        ('S3', 'S3'),
        ('Sp-2', 'Sp-2'),
        ('Sp-1', 'Sp-1'),
        ('S2', 'S2'),
        ('S1', 'S1'),
        ('D4', 'D4'),
        ('D3', 'D3'),
        ('D2', 'D2'),
        ('D1', 'D1'),
    ]
    jenjang = models.CharField(max_length=10, choices=JENJANG_CHOICES, blank=True, null=True, verbose_name=_("Jenjang")    )

    STATUS_CHOICES = [
        ('Aktif', 'Aktif'),
        ('Alih Bentuk', 'Alih Bentuk'),
        ('Tutup', 'Tutup'),
        ('Alih Kelola', 'Alih Kelola'),
        ('Pembinaan', 'Pembinaan'),
    ]
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, blank=True, null=True, verbose_name=_("Status"))

    sinta_id = models.CharField(max_length=100, blank=True, null=True, unique=True, verbose_name=_("Sinta ID"))
    sinta_score = models.CharField(max_length=100, blank=True, null=True, verbose_name=_("Sinta Score"))
    sinta_score3 = models.CharField(max_length=100, blank=True, null=True, verbose_name=_("Sinta Score 3"))  

    AKREDITASI_CHOICES_PS = [
        ('internasional', 'Internasional'),
        ('unggul', 'Unggul'),
        ('baik_sekali', 'Baik Sekali'),
        ('baik', 'Baik'),
        ('a', 'A'),
        ('b', 'B'),
        ('c', 'C'),
        ('tidak_terakreditasi', 'Tidak Terakreditasi'),
    ]
    akreditasi_ps = models.CharField(max_length=30, choices=AKREDITASI_CHOICES_PS, blank=True, null=True, verbose_name=_("Akreditasi PS"))
    
    def __str__(self):
        return self.nama_program_studi



class Profile(models.Model):
    ROLE_CHOICES = [
        ('system_owner', _('System Owner')),
        ('system_admin', _('System Admin')),
        ('institution_admin', _('Institutional Admin')),
        ('researcher', _('Researcher')),
        ('reviewer', _('Reviewer')),
        ('student', _('Student')),         
        ('technician', _('Technician')),   
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    
    # Common fields
    nama_lengkap = models.CharField(max_length=255, blank=True, null=True, verbose_name=_("Nama Lengkap"))
    gelar_depan = models.CharField(max_length=100, blank=True, null=True, verbose_name=_("Gelar Depan"))
    gelar_belakang = models.CharField(max_length=100, blank=True, null=True, verbose_name=_("Gelar Belakang"))
    no_hp = models.CharField(max_length=50, blank=True, null=True, verbose_name=_("No HP"))
    
    institution = models.ForeignKey(
        'Institution', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name="researchers", 
        verbose_name=_("Institusi")
    )
    
    role = models.CharField(max_length=30, choices=ROLE_CHOICES, default='researcher', verbose_name=_("Role"))
    
    program_studi = models.ForeignKey(
        'ProgramStudi', 
        on_delete=models.SET_NULL, 
        blank=True, 
        null=True, 
        verbose_name=_("Program Studi")
    )
    
    # Other researcher fields
    nidn_nidk = models.CharField(max_length=100, blank=True, null=True, verbose_name=_("NIDN/NIDK"))
    jenjang_pendidikan = models.CharField(max_length=100, blank=True, null=True, verbose_name=_("Jenjang Pendidikan"))
    jabatan_akademik = models.CharField(max_length=100, blank=True, null=True, verbose_name=_("Jabatan Akademik"))
    research_interest = models.TextField(blank=True, null=True, verbose_name=_("Research Interest"))
    sinta_id = models.CharField(max_length=100, blank=True, null=True, unique=True, verbose_name=_("Sinta ID"))
    sinta_score = models.CharField(max_length=100, blank=True, null=True, verbose_name=_("Sinta Score"))
    sinta_score3 = models.CharField(max_length=100, blank=True, null=True, verbose_name=_("Sinta Score 3"))
    sinta_scoresc = models.CharField(max_length=100, blank=True, null=True, verbose_name=_("Sinta Score Scopus"))
    sinta_scorego = models.CharField(max_length=100, blank=True, null=True, verbose_name=_("Sinta Score Google Scholar"))
    sinta_name_scraped = models.CharField(_("SINTA Name (scraped)"), max_length=255, blank=True, null=True)
    sinta_name_match = models.BooleanField(_("Name matches SINTA?"), default=False, help_text="True if local full name ≈ scraped SINTA-profile name")
    orcid_id = models.CharField(max_length=100, blank=True, null=True, verbose_name=_("Orcid ID"))
    is_reviewer_assigned = models.BooleanField(default=False, verbose_name=_("Research Reviewer Assigned"))
    
    # Profile photo field
    profile_photo = models.ImageField(
        upload_to=profile_photo_upload_path, 
        blank=True, 
        null=True, 
        verbose_name=_("Profile Photo")    
    )
    
    def __str__(self):
        return f"{self.user.username} Profile"



class ResearchGrant(models.Model):
    OFFERED_TO_CHOICES = [
        ('all', _('Sitewide')),
        ('institution', _('Own Institution')),
    ]
    title = models.CharField(max_length=255, verbose_name=_("Title"))
    description = models.TextField(verbose_name=_("Description"))
    offered_to = models.CharField(max_length=20, choices=OFFERED_TO_CHOICES, default='all', verbose_name=_("Offered To"))
    start_year = models.PositiveIntegerField(verbose_name=_("Start Year"))
    end_year = models.PositiveIntegerField(verbose_name=_("End Year"))
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="grants_created", verbose_name=_("Created By"))
    institution = models.ForeignKey('Institution', on_delete=models.SET_NULL, null=True, blank=True, verbose_name=_("Institution"))
    qualification_criteria = models.TextField(blank=True, null=True, verbose_name=_("Qualification Criteria"))
    
    # Grant Components
    identitas_usulan = models.TextField(blank=True, null=True, verbose_name=_("Identitas Usulan"))
    substansi_dan_luaran = models.TextField(blank=True, null=True, verbose_name=_("Substansi dan Luaran"))
    rab = models.TextField(blank=True, null=True, verbose_name=_("RAB"))
    dokumen_pendukung = models.FileField(upload_to='grants/documents/', blank=True, null=True, verbose_name=_("Dokumen Pendukung"))
    konfirmasi_usulan = models.TextField(blank=True, null=True, verbose_name=_("Konfirmasi Usulan"))
    
    # Approval and Review
    approved_by_pt = models.BooleanField(default=False, verbose_name=_("Approved by Pimpinan PT"))
    approved_by_ppm = models.BooleanField(default=False, verbose_name=_("Approved by Unit Pengelola PPM"))
    reviewer = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="grants_review", verbose_name=_("Assigned Reviewer"))
    review_score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, verbose_name=_("Review Score"))
    final_decision = models.CharField(max_length=50, blank=True, null=True, verbose_name=_("Final Decision"))
    announcement = models.TextField(blank=True, null=True, verbose_name=_("Announcement"))
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.title



class FooterColumn(models.Model):
    title = models.CharField(max_length=255, verbose_name=_("Title"))
    content = models.TextField(verbose_name=_("Content"))
    order = models.PositiveIntegerField(default=0, verbose_name=_("Order"))

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.title
    
    

class Announcement(models.Model):
    AUDIENCE_CHOICES = [
        ('sitewide', 'Sitewide'),
        ('selected_institution', 'Selected Institution'),
    ]
    title = models.CharField(max_length=255, verbose_name="Title")
    audience = models.CharField(
        max_length=20,
        choices=AUDIENCE_CHOICES,
        default='sitewide',
        verbose_name="Audience"
    )
    content = models.TextField(verbose_name="Content")
    image = models.ImageField(
        upload_to=announcement_image_upload_path, 
        blank=True, 
        null=True, 
        verbose_name="Image Attachment"
    )
    institution = models.ForeignKey(
        Institution,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Institution"
    )
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="announcements_created", verbose_name="Created By")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created Date and Time")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Updated Date and Time")
    
    def __str__(self):
        return self.title


class AnnouncementFile(models.Model):
    announcement = models.ForeignKey(
        Announcement,
        on_delete=models.CASCADE,
        related_name='files',
        verbose_name="Announcement"
    )
    file = models.FileField(upload_to=announcement_file_upload_path, verbose_name="File Attachment")
    
    def __str__(self):
        return f"File for {self.announcement.title}"



# --- Before saving an Institution, if its logo fields have changed, delete the old ones ---
@receiver(pre_save, sender=Institution)
def institution_delete_old_logos(sender, instance, **kwargs):
    # Only run on updates, not on creates
    if not instance.pk:
        return
    old = sender.objects.filter(pk=instance.pk).first()
    if not old:
        return

    # logo (the main institution logo)
    if old.logo and old.logo != instance.logo:
        delete_file(old.logo.path)

    # logo_bp (the "badan penyelenggara" logo)
    if old.logo_bp and old.logo_bp != instance.logo_bp:
        delete_file(old.logo_bp.path)

# --- After deleting an Institution, also delete both files from disk ---
@receiver(post_delete, sender=Institution)
def institution_delete_logos_on_delete(sender, instance, **kwargs):
    if instance.logo:
        delete_file(instance.logo.path)
    if instance.logo_bp:
        delete_file(instance.logo_bp.path)

# ---- PROFILE PHOTO CLEANUP ----
@receiver(pre_save, sender=Profile)
def delete_old_profile_photo(sender, instance, **kwargs):
    if not instance.pk:
        return
    old = sender.objects.filter(pk=instance.pk).first()
    if old and old.profile_photo and old.profile_photo != instance.profile_photo:
        delete_file(old.profile_photo.path)

@receiver(post_delete, sender=Profile)
def delete_profile_photo_on_profile_delete(sender, instance, **kwargs):
    if instance.profile_photo:
        delete_file(instance.profile_photo.path)

# ---- ANNOUNCEMENT IMAGE CLEANUP ----
@receiver(pre_save, sender=Announcement)
def delete_old_announcement_image(sender, instance, **kwargs):
    if not instance.pk:
        return
    old = sender.objects.filter(pk=instance.pk).first()
    if old and old.image and old.image != instance.image:
        delete_file(old.image.path)

@receiver(post_delete, sender=Announcement)
def delete_announcement_image_on_delete(sender, instance, **kwargs):
    if instance.image:
        delete_file(instance.image.path)

# ---- ANNOUNCEMENT FILE ATTACHMENT CLEANUP ----
@receiver(pre_save, sender=AnnouncementFile)
def delete_old_announcement_file(sender, instance, **kwargs):
    if not instance.pk:
        return
    old = sender.objects.filter(pk=instance.pk).first()
    if old and old.file and old.file != instance.file:
        delete_file(old.file.path)

@receiver(post_delete, sender=AnnouncementFile)
def delete_announcement_file_on_delete(sender, instance, **kwargs):
    if instance.file:
        delete_file(instance.file.path)