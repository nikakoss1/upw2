from django.db import models
from tinymce.models import HTMLField

UPDATE_STATUS_CHOICES = [
    ('SCRAPING','SCRAPING'),
    ('STOPPED','STOPPED'),
]

STAGE = [
    ('#1','STAGE #1 - GETTING CATEGORIES'),
    ('#2','STAGE #2 - GETTING PAGES'),
    ('#3','STAGE #3 - GETTING ADS'),
    ('#4','STAGE #4 - UPDATING ADS'),
]

def dubicars_uploads(instance, filename, *args, **kwargs):
    return 'dubicars/%s' % filename

class Website(models.Model):
    name = models.CharField('name of the website', max_length=255)
    url = models.URLField('root URL of the website',)
    content = models.TextField('Any comments to the website', null=True, blank=True)
    created = models.DateField(auto_now_add=True, auto_now=False)
    updated = models.DateField(auto_now_add=False, auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return '{0}'.format(self.name)


class DubicarsCategory(models.Model):
    name = models.CharField('name of the category', max_length=255)
    url = models.URLField('URL of the category',)
    content = HTMLField(null=True)

    # RELATED
    parent = models.ForeignKey('self', related_name='parent_category', null=True, on_delete=models.CASCADE)

    # SEO
    seo_title = models.CharField('category seo-title', max_length=255, null=True, blank=True)
    seo_keywords = models.CharField('category seo-keywords', max_length=255, null=True, blank=True)
    seo_description = models.CharField('category seo-description', max_length=255, null=True, blank=True)
    seo_h1 = models.CharField('category seo-h1', max_length=255, null=True, blank=True)

    created = models.DateField(auto_now_add=True, auto_now=False)
    updated = models.DateField(auto_now_add=False, auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return '{0}'.format(self.name)


class Update(models.Model):
    website = models.ForeignKey(Website, on_delete=models.CASCADE)
    total_ads_number = models.IntegerField(default=0)
    total_category_number = models.IntegerField(default=0)
    total_pages_number = models.IntegerField(default=0)
    total_ads_number = models.IntegerField(default=0)
    total_updated_ads_number = models.IntegerField(default=0)
    status = models.CharField('Update Status', max_length=255, choices=UPDATE_STATUS_CHOICES, null=True, blank=True)
    current_stage = models.CharField('Stage', max_length=255, choices=STAGE, null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True, auto_now=False)
    updated = models.DateTimeField(auto_now_add=False, auto_now=True)

    class Meta:
        ordering = ['-created']

    def __str__(self):
        return '{0}'.format(self.created)


class DubicarsPage(models.Model):
    url = models.URLField('URL of the category',)

    # related
    update = models.ForeignKey(Update, null=True, on_delete=models.CASCADE)
    created = models.DateField(auto_now_add=True, auto_now=False)
    updated = models.DateField(auto_now_add=False, auto_now=True)

    def __str__(self):
        return '{0}'.format(self.url)


class DubicarsAdCharacteristic(models.Model):
    get_name = models.CharField('get name', max_length=255)
    name = models.CharField('name', max_length=255)
    value = models.CharField('value', max_length=555, null=True)

    def __str__(self):
        return '{0}: {1}'.format(self.name, self.value)


class DubicarsAdInteriorDesign(models.Model):
    name = models.CharField('name', max_length=255)

    def __str__(self):
        return '{0}'.format(self.name)


class DubicarsAdExteriorFeature(models.Model):
    name = models.CharField('name', max_length=255)

    def __str__(self):
        return '{0}'.format(self.name)


class DubicarsAdSecurity(models.Model):
    name = models.CharField('name', max_length=255)

    def __str__(self):
        return '{0}'.format(self.name)


class DubicarsAdService(models.Model):
    name = models.CharField('name', max_length=255)

    def __str__(self):
        return '{0}'.format(self.name)


class DubicarsAdFinance(models.Model):
    name = models.CharField('name', max_length=255)

    def __str__(self):
        return '{0}'.format(self.name)


class DubicarsAdWarranty(models.Model):
    name = models.CharField('name', max_length=255)

    def __str__(self):
        return '{0}'.format(self.name)


class DubicarsTag(models.Model):
    name = models.CharField('name', max_length=255)

    def __str__(self):
        return '{0}'.format(self.name)


class DubicarsAd(models.Model):
    name = models.CharField('ad title', max_length=255)
    url = models.URLField('ad URL',null=True)
    short_desc = models.TextField('Ad short description', null=True, blank=True)
    price = models.CharField('ad price', max_length=25, null=True)
    curr = models.CharField('ad curr', max_length=25, null=True)
    maps_coords = models.CharField('auto coords', max_length=255, null=True)
    desc = models.TextField('Ad description', null=True, blank=True)

    # CONTACT SELLER
    phone = models.CharField(max_length=255, null=True, blank=True)

    # SEO
    seo_title = models.CharField('ad seo-title', max_length=255, null=True, blank=True)
    seo_keywords = models.CharField('ad seo-keywords', max_length=255, null=True, blank=True)
    seo_description = models.CharField('ad seo-description', max_length=255, null=True, blank=True)
    seo_h1 = models.CharField('ad seo-h1', max_length=255, null=True, blank=True)

    # RELATED
    other_vendor_models = models.ManyToManyField(DubicarsCategory, related_name='other_vendor_models')
    similar_models = models.ManyToManyField('self', related_name='similar_models')
    category = models.ManyToManyField(DubicarsCategory)
    update = models.ForeignKey(Update, null=True, on_delete=models.CASCADE)
    dubicar_ad_charact = models.ManyToManyField(DubicarsAdCharacteristic)
    dubicars_ad_interior_design = models.ManyToManyField(DubicarsAdInteriorDesign)
    dubicars_ad_exterior_design = models.ManyToManyField(DubicarsAdExteriorFeature)
    dubicars_ad_security = models.ManyToManyField(DubicarsAdSecurity)
    dubicars_ad_finance = models.ManyToManyField(DubicarsAdFinance)
    dubicars_ad_warranty = models.ManyToManyField(DubicarsAdWarranty)
    dubicars_ad_service = models.ManyToManyField(DubicarsAdService)
    dubicars_tags = models.ManyToManyField(DubicarsTag)

    created = models.DateField(auto_now_add=True, auto_now=False)
    updated = models.DateField(auto_now_add=False, auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return '{0}'.format(self.name)


class DubiscrapeImage(models.Model):
    dubicar_ad = models.ForeignKey(DubicarsAd, null=True, on_delete=models.CASCADE)
    name = models.CharField('image name', max_length=255, null=True)
    image = models.ImageField(upload_to=dubicars_uploads, default='dubicars/noimage.jpg')
    created = models.DateField(auto_now_add=True, auto_now=False)
    updated = models.DateField(auto_now_add=False, auto_now=True)

    def __str__(self):
        return '{0}'.format(self.id)


class AdError(models.Model):
    stage = models.CharField(max_length=100)
    step = models.CharField(max_length=100)
    exception = models.TextField(null=True)
    ad = models.ForeignKey(DubicarsAd, null=True, on_delete=models.CASCADE)
    created = models.DateField(auto_now_add=True, auto_now=False)
    updated = models.DateField(auto_now_add=False, auto_now=True)

    def __str__(self):
        return '{0} | {1}'.format(self.step, self.exception)




















