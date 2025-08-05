from .models import Structure

def structure_context(request):
    if request.user.is_authenticated:
        return {
            'has_structure': Structure.objects.filter(user=request.user).exists()
        }
    return {}