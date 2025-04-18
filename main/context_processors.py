from .models import FooterColumn

def footer_columns(request):
    columns = FooterColumn.objects.all()
    return {'footer_columns': columns}
