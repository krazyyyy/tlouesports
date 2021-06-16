from .models import AdminOptions

def management(request):
    try:
        options = AdminOptions.objects.get(access_name="admin")
    except:
        options = None
    return {
        'options': options
    }