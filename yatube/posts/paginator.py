from django.core.paginator import Paginator
from django.conf import settings


def paginate_page(request, post_list):
    paginator = Paginator(post_list, settings.PAGE_ON_SIZE)
    page_number = request.GET.get('page')
    return paginator.get_page(page_number)
