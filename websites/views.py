from .dubicars_models import Website, Update, DubicarsAd, DubicarsCategory
from .dubicars_scraper import get_dubicars_categories, create_page_objs, create_ads_objs, update_dubicars_ad, str_to_class
from .forms import UpdateForm
from django.http import HttpResponse, HttpResponseRedirect, Http404, JsonResponse
from django.shortcuts import render
from django.views.generic import CreateView, UpdateView, TemplateView, ListView
from django.views.generic.detail import DetailView
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

TABLES = [
    'DubicarsCategory',
    'Update',
    'DubicarsPage',
    'DubicarsAdCharacteristic',
    'DubicarsAdInteriorDesign',
    'DubicarsAdExteriorFeature',
    'DubicarsAdSecurity',
    'DubicarsAdService',
    'DubicarsAdFinance',
    'DubicarsAdWarranty',
    'DubicarsTag',
    'DubicarsAd',
    'DubiscrapeImage',
    'AdError',
]

# Create your views here.
def get_headers():
    return {'User-Agent': generate_user_agent(device_type="desktop", os=('mac', 'linux'))}

# class WebsiteListView(ListView):
#     model = Website

class WebsiteDetailView(UpdateView):
    model = Website
    form_class = UpdateForm
    success_url = './'

    def has_running_update(self):
        self.obj = self.get_object()
        return self.obj.update_set.filter(status='SCRAPING').count() > 0

    def get_context_data(self, **kwargs):
        context = super(WebsiteDetailView, self).get_context_data(**kwargs)
        context['total_ads_number'] = DubicarsAd.objects.all().count()
        context['has_running_update'] = self.has_running_update()
        return context

def clean_db(clean_tables):
    for table in clean_tables:
        str_to_class(table).objects.all().delete()

def update(request, *args, **kwargs):
    data = {}
    if request.method == 'POST' and request.is_ajax():

        ## CLEAN DB
        # clean_db(TABLES)

        website_id = int(request.POST['website_id'])
        website_obj = Website.objects.get(id=website_id)
        updates = Update.objects.filter()
        updates.update(status='STOPPED')

        # if not updates.filter(status='SCRAPING').exists():
        update_obj = Update.objects.create(
            website=website_obj,
            status='SCRAPING',
            current_stage='STAGE #1 - GETTING CATEGORIES',
            )

        data = {
                'status': update_obj.status,
                'current_stage': update_obj.current_stage,
                }
    return JsonResponse(data)


def update_stop(request, *args, **kwargs):
    data = {}
    if request.method == 'POST' and request.is_ajax():
        updates = Update.objects.all()
        updates.update(status='STOPPED')

        data = {
                'status': 'STOPPED',
                }

    return JsonResponse(data)


def create_dubicars_category_objs(dubicars_categories, instance):
    for category in dubicars_categories:
        name = category[0]
        url = category[1]
        dubicars_category, created = DubicarsCategory.objects.get_or_create(
            url=url,
            )
        dubicars_category.name = name
        dubicars_category.update = instance
        dubicars_category.save()

    return len(dubicars_categories)


@receiver(post_save, sender=Update)
def dubicars_category_post_save(sender, instance, **kwargs):

    if  kwargs['created']:

        ## CREATE CATEGORIES
        if instance.status != 'STOPPED':
            print(instance.current_stage)
            dubicars_categories = get_dubicars_categories(instance)
            total_category_number = create_dubicars_category_objs(dubicars_categories, instance)
            instance.total_category_number = total_category_number
            instance.save()

        ## CREATE PAGE URLS
        if instance.status != 'STOPPED':
            instance.current_stage = 'STAGE #2 - GETTING PAGES'
            instance.save()
            print(instance.current_stage)
            total_pages_number = create_page_objs(instance)
            instance.total_pages_number = total_pages_number
            instance.save()

        ## CREATE ADS
        if instance.status != 'STOPPED':
            instance.current_stage = 'STAGE #3 - GETTING ADS'
            instance.save()
            print(instance.current_stage)
            total_ads_number = create_ads_objs(instance)
            instance.total_ads_number = total_ads_number
            instance.save()

        ##UPDATE ADS
        if instance.status != 'STOPPED':
            instance.current_stage = 'STAGE #4 - UPDATING ADS'
            instance.save()
            print(instance.current_stage)
            update_dubicars_ad(instance)
            instance.status = 'STOPPED'
            instance.save()
















