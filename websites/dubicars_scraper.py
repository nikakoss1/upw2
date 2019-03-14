import requests, sys, random, os, shutil, decimal
from user_agent import generate_user_agent
from lxml import html, etree
from django.conf import settings
from django.core.files import File

from .dubicars_models import (
    AdError,
    DubicarsAd,
    DubicarsAdCharacteristic,
    DubicarsAdExteriorFeature,
    DubicarsAdFinance,
    DubicarsAdInteriorDesign,
    DubicarsAdSecurity,
    DubicarsAdService,
    DubicarsAdWarranty,
    DubicarsCategory,
    DubicarsPage,
    DubiscrapeImage,
    DubicarsTag,
    Update,
    )
from multiprocessing.dummy import Pool

CLASSNAMES = {
    'INTERIOR DESIGN':('DubicarsAdInteriorDesign','dubicars_ad_interior_design'),
    'EXTERIOR FEATURES':('DubicarsAdExteriorFeature','dubicars_ad_exterior_design'),
    'SECURITY & ENVIRONMENT':('DubicarsAdSecurity','dubicars_ad_security'),
    'SERVICE':('DubicarsAdService','dubicars_ad_service'),
    'FINANCE':('DubicarsAdFinance','dubicars_ad_finance'),
    'WARRANTY':('DubicarsAdWarranty','dubicars_ad_warranty'),
}

# PARAMS
THREADS = 50
MAX_IMAGE_DOWNLOAD = 2
DEMO_UPDATE_NUMBER = 50


pool = Pool(THREADS)

def get_directory():
    if settings.DEBUG:
        DIRECTORY = '/devapps/dubiscraper/src/tmp'
    else:
        DIRECTORY = '/webapps/xhub/src/tmp'
    return DIRECTORY

DIRECTORY = get_directory()

def id_generator(size=20, chars='adefghjkmnpqrstwxwz23456789'):
    return ''.join(random.choice(chars) for _ in range(size))

def str_to_class(classname):
    return getattr(sys.modules[__name__], classname)

def get_headers():
    return {'User-Agent': generate_user_agent(device_type="desktop", os=('mac', 'linux'))}

def fetch_url(url):
    headers = get_headers()
    return requests.get(url, headers=headers)


############### STAGE #1 - GETTING CATEGORIES ###############

def get_root_categories(ul_elems):
    root_categories = []
    for ul in ul_elems:
        for a in ul.xpath('.//a'):
            category_url = a.xpath('@href')[0]
            category_name = a.xpath('text()')[0]
            root_categories.append((category_name, category_url))
    return root_categories

def get_categories(responses):
    try:
        categories = []
        excepts = ['show-all',]
        for response in responses:
            fromstring = html.fromstring(response.content)
            ul_elems_min = fromstring.xpath('//div[@id="search-link-box"]/ul')
            ul_elems_extra = fromstring.xpath('//div[@id="search-link-box"]/div[@class="extra"]/ul')
            ul_elems = ul_elems_min + ul_elems_extra
            for ul in ul_elems:
                for a in ul.xpath('.//a'):
                    link = a.xpath('@href')[0]
                    category_url = 'https://www.dubicars.com{0}'.format(link)
                    category_name = a.xpath('text()')[0]
                    for ex in excepts:
                        if not ex in str(category_url):
                            categories.append((category_name, category_url))
    except Exception as e:
        AdError.objects.create(stage='STAGE #1 - GETTING CATEGORIES', step='CATEGORIES1', exception=e)
    return categories

def get_dubicars_categories(instance):
    dubicars_categories = []
    headers = get_headers()
    root_url = instance.website.url
    response = requests.get(root_url, headers=headers)
    fromstring = html.fromstring(response.content)

    # ROOT CATEGORIES
    try:
        ul_elems = fromstring.xpath('//div[@id="content"]/div[@class="bp-2-show"]//ul')
        root_categories = get_root_categories(ul_elems)
    except Exception as e:
        AdError.objects.create(stage='STAGE #1 - GETTING CATEGORIES', step='ROOT CATEGORIES', exception=e)
        return dubicars_categories

    # CATEGORIES
    try:
        fetched_urls = []
        while len(root_categories) > 0:
            lst = []

            for i in root_categories:
                lst.append(i)
                root_categories.remove(i)

            responses = pool.map(lambda url: requests.get(url[1]), lst)
            categories = get_categories(responses)

            for category in categories:
                if not category[1] in fetched_urls:
                    root_categories.append(category)
                    fetched_urls.append(category)
                dubicars_categories.append(category)
            print('RESULT: ', len(dubicars_categories))
    except Exception as e:
        AdError.objects.create(stage='STAGE #1 - GETTING CATEGORIES', step='CATEGORIES2', exception=e)
        return dubicars_categories

    return dubicars_categories


############### STAGE #2 - GETTING PAGES ###############

def get_page_urls(responses, instance):
    page_urls = []
    try:
        for response in responses:
            fromstring = html.fromstring(response.content)
            try:
                last_page = fromstring.xpath('//ul[@id="pagination-desktop"]//a')[-2]
            except:
                page_urls.append(response.url)
                continue
            current_page_url = last_page.xpath('@href')[0].split('?')[0]
            last_page_url = last_page.xpath('@href')[0].split('=')[0]
            last_page_number = int(last_page.xpath('text()')[0])
            for i in range(2,last_page_number+1):
                page_urls.append('{0}={1}'.format(last_page_url,i))
            page_urls.append(current_page_url)

    except Exception as e:
        AdError.objects.create(stage='STAGE #2 - GETTING PAGES', step='PAGES', exception=e)

    return page_urls

def create_page_objs(instance):
    try:
        category_urls = list(DubicarsCategory.objects.values_list('url', flat=True))
        responses = pool.map(lambda url: requests.get(url), category_urls)
        page_urls = get_page_urls(responses, instance)
        for page_url in page_urls:
            page_obj = DubicarsPage.objects.get_or_create(url=page_url)[0]
            page_obj.update = instance
            page_obj.save()
    except Exception as e:
        AdError.objects.create(stage='STAGE #2 - GETTING PAGES', step='CREATE PAGE OBJS', exception=e)

    return instance.dubicarspage_set.all().count()


############### STAGE #3 - GETTING ADS ###############

def get_ad_urls(responses):
    ad_urls = []
    try:
        for response in responses:
            fromstring = html.fromstring(response.content)
            li_elems = fromstring.xpath('//section[@id="serp-list-new"]//li')
            for li in li_elems:
                tag_objs = []
                try:
                    a_elem = li.xpath('.//div[@class="bp-2-show description"]//h3/a')[0]
                    tags = li.xpath('.//div[@class="tags-container"]/*/text()')
                    short_desc = li.xpath('.//p[@class="bp-2-show short-desc"]/text()')[0]
                    for tag in tags:
                        tag_obj, created = DubicarsTag.objects.get_or_create(name=tag)
                        tag_objs.append(tag_obj)
                    ad_url = a_elem.xpath('@href')[0]
                    ad_name = a_elem.xpath('text()')[0]
                    ad_urls.append((ad_name, ad_url,tag_objs,short_desc))
                except Exception as e:
                    continue
    except Exception as e:
        print(e)
        AdError.objects.create(stage='STAGE #2 - GETTING ADS', step='PAGES', exception=e)
    return ad_urls

def chunks(lst, n):
    """Yield successive n-sized chunks from l."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]

def create_ads_objs(instance):
    try:
        page_urls = list(DubicarsPage.objects.all().values_list('url', flat=True))
        for part_urls in list(chunks(page_urls, 200)):
            responses = pool.map(lambda url: requests.get(url), part_urls)
            ad_urls = get_ad_urls(responses)
            for ad_url in ad_urls:
                dubicars_ad = DubicarsAd.objects.get_or_create(url=ad_url[1])[0]
                dubicars_ad.name = ad_url[1]
                dubicars_ad.update = instance
                dubicars_ad.short_desc = ad_url[3]
                dubicars_ad.save()
                dubicars_ad.dubicars_tags.set(ad_url[2])
    except Exception as e:
        AdError.objects.create(stage='STAGE #3 - GETTING ADS', step='CREATE ADS', exception=e)
    return instance.dubicarsad_set.all().count()


############### STAGE #3 - UPDATING ADS ###############

def get_price(row):
    try:
        raw_price = row.xpath('.//strong[@class="money"]/text()')[0]
        curr = raw_price.split(' ')[0]
        price = raw_price.split(' ')[1]
    except Exception as e:
        print(e)
        curr = ''
        price = 'ask for price'
    return curr, price

def get_get_item_name(item_name):
    return item_name[0].strip().replace(':','').replace(' ','_')

def get_clean_item_name(item_name):
    return item_name[0].replace(':','')

def create_charact_obj(item_name, item_value, dubicars_ad):
    get_item_name = get_get_item_name(item_name)
    clean_name = get_clean_item_name(item_name)
    charact_obj = DubicarsAdCharacteristic.objects.get_or_create(get_name=get_item_name)[0]
    charact_obj.value = item_value[0]
    charact_obj.name = clean_name
    charact_obj.save()
    dubicars_ad.dubicar_ad_charact.add(charact_obj)
    return charact_obj

def get_item_details(fromstring, dubicars_ad):
    try:
        rows = fromstring.xpath('//section[@id="item-details"]//tr[th[@scope="row"]]')
        for row in rows:
            item_name = row.xpath('./th/text()')
            item_value = row.xpath('./td/text()')
            charact_obj = create_charact_obj(item_name, item_value, dubicars_ad)
            if 'Price:' in item_name:
                curr, price = get_price(row)
                dubicars_ad.curr = curr
                dubicars_ad.price = price
                dubicars_ad.save()
    except Exception as e:
        AdError.objects.create(stage='STAGE #3 - UPDATING ADS', step='ITEM DETAILS', exception=e)
    return

def get_item_description(fromstring, dubicars_ad):
    try:
        elems = fromstring.xpath('//p[@itemprop="description"]')
        raw_value_lst = []
        for elem in elems:
            raw_value = etree.tostring(elem, method='html', with_tail=False)
            raw_value_lst.append(raw_value)


        dubicars_ad.desc = b''.join(raw_value_lst)
        dubicars_ad.save()
    except Exception as e:
        AdError.objects.create(stage='STAGE #3 - UPDATING ADS', step='ITEM DESCRIPTION', exception=e)
    return dubicars_ad

def get_classname(heading):
    classname = CLASSNAMES[heading][0]
    field = CLASSNAMES[heading][1]
    return (classname, field)

def get_items(item_features_elems, heading):
    item_features = []
    try:

        pattern = './/div[h3[contains(text(),"{0}")]]//li'.format(heading)
        li_elems = item_features_elems.xpath(pattern)
        for li in li_elems:
            item_value = li.xpath('text()')[0]
            item_features.append(item_value)
    except Exception as e:
        AdError.objects.create(stage='STAGE #3 - UPDATING ADS', step='GET ITEM FEATURES', exception=e)
    return item_features

def get_item_features(fromstring, dubicars_ad):
    item_features_elems = fromstring.xpath('//section[@id="item-features"]')[0]
    headings = [
        'INTERIOR DESIGN',
        'EXTERIOR FEATURES',
        'SECURITY & ENVIRONMENT',
        'SERVICE',
        'FINANCE',
        'WARRANTY',
    ]

    for heading in headings:
        classname, field = get_classname(heading)
        item_features = get_items(item_features_elems, heading)
        objs = []
        for item_feature in item_features:
            item_obj = str_to_class(classname).objects.get_or_create(name=item_feature)[0]
            objs.append(item_obj)
        getattr(dubicars_ad, field).set(objs)

def get_related_items(fromstring, dubicars_ad):
    related_objs = []
    related_elems = fromstring.xpath('//section[@id="related-items"]//li//a')
    for elem in related_elems:
        name = elem.xpath('./text()')[0].strip()
        link = elem.xpath('./@href')[0].strip()
        url = 'https://www.dubicars.com{0}'.format(link)
        obj, created = DubicarsCategory.objects.get_or_create(url=url)
        obj.name = name
        obj.save()
        related_objs.append(obj)
    dubicars_ad.other_vendor_models.set(related_objs)

def get_similar_items(fromstring, dubicars_ad):
    similar_objs = []
    similar_elems = fromstring.xpath('//section[@id="similar-items"]/ul[@class="item-grid-alt"]//h3//a')
    for elem in similar_elems:
        name = elem.xpath('./text()')[1].strip()
        if name == '':
            continue
        url = elem.xpath('./@href')[0].strip()
        obj, created = DubicarsAd.objects.get_or_create(url=url)
        obj.name = name
        obj.save()
        similar_objs.append(obj)
    dubicars_ad.similar_models.set(similar_objs)
    return

def get_contact_items(fromstring, dubicars_ad):
    block = fromstring.xpath('//section[@id="dealer-info"]')[0]
    phone = block.xpath('.//p[@id="contact-buttons"]/a/@href')[0].replace('tel:','')
    try:
        maps_coords = block.xpath('.//a[@class="icon-directions"]/@href')[0].split('daddr=')[1]
        dubicars_ad.maps_coords = maps_coords
    except:
        pass
    dubicars_ad.phone = phone
    dubicars_ad.save()

def get_seo_items(fromstring, dubicars_ad):
    seo_description = fromstring.xpath('//meta[@name="description"]/@content')[0]
    seo_title = fromstring.xpath('//title/text()')[0]
    seo_h1 = fromstring.xpath('//h1[span[@itemprop="name"]]/span/text()')[0]
    dubicars_ad.seo_description = seo_description
    dubicars_ad.seo_title = seo_title
    dubicars_ad.seo_h1 = seo_h1
    dubicars_ad.save()

def get_category_url(link):
    url = 'https://www.dubicars.com{0}'.format(link)
    if 'www.dubicars.com' in link:
        return link
    return url

def get_reversed(lst):
    reversed_lst = []
    for x in reversed(lst):
        reversed_lst.append(x)
    return reversed_lst

def get_breadcrumbs(fromstring, dubicars_ad):
    span_elems = fromstring.xpath('//span[@typeof="v:Breadcrumb"]')
    lst = []
    for span in span_elems:
        link = span.xpath('./a/@href')[0]
        category_url = get_category_url(link).strip()
        category_name = span.xpath('./a/text()')[0].strip()
        obj, created = DubicarsCategory.objects.get_or_create(url=category_url)
        obj.name = category_name
        obj.save()
        lst.append(obj)

    reversed_lst = get_reversed(lst)
    for i in range(0,len(reversed_lst)):
        the_last = reversed_lst[i]
        try:
            the_next = reversed_lst[i+1]
        except:
            the_next = None
        the_last.parent = the_next
        the_last.save()

    # SET CATEGORIES OD THE AD
    dubicars_ad.category.set(reversed_lst)
    return reversed_lst

def get_clean_url(item):
    for raw_link in item.split(','):
        if 'images/' in raw_link:
            return 'https://www.dubicars.com/{0}'.format(raw_link.strip().replace("'",""))
    return

def get_images(fromstring, dubicars_ad):
    lst = []
    items = fromstring.xpath('//div[@class="slides"]//li//script/text()')
    for item in items:
        url = get_clean_url(item)
        lst.append(url)
    return lst

def get_file_ext(file_link):
    filename = file_link.split('/')[-1].split('.')[0]
    ext = file_link.split('/')[-1].split('.')[1]
    print(filename, ext)
    return filename, ext
    # try:
    #     return file_link.split('?')[0]
    # except:
    #     return filename, ext

def download_images(images, dubicars_ad):
    try:
        for url in images[:MAX_IMAGE_DOWNLOAD]:
            file_name, ext = get_file_ext(url)
            filename = '{0}.{1}'.format(file_name, ext)

            if not os.path.exists(DIRECTORY):
                os.makedirs(DIRECTORY)

            # CHECK FOR IMAGE EXIST
            images = DubiscrapeImage.objects.filter(name=file_name)
            if not images.exists():

                # DOWNLOAD IMAGE FROM SRC
                response = requests.get(url, stream=True)
                file_path = os.path.join(DIRECTORY, filename)
                with open(file_path, 'wb') as out_file:
                    shutil.copyfileobj(response.raw, out_file)
                del response

                # UPLOAD IMAGE
                dubiscrape_ad_image_obj = DubiscrapeImage.objects.create(name=file_name)
                with open(file_path, 'rb') as image_file:
                    dubiscrape_ad_image_obj.image.save(filename, File(image_file), save=True)
                    dubiscrape_ad_image_obj.dubicar_ad = dubicars_ad
                    dubiscrape_ad_image_obj.save()
                os.remove(file_path)
    except Exception as e:
        AdError.objects.create(stage='STAGE #3 - UPDATING ADS', step='DOWNLOAD IMAGES', exception=e)

def update_dubicars_ad(instance):
    counter = 0
    ad_urls = list(DubicarsAd.objects.all().values_list('url', flat=True))[:DEMO_UPDATE_NUMBER]
    for part_urls in list(chunks(ad_urls, 500)):
        responses = pool.map(lambda url: requests.get(url), part_urls)
        for response in responses:
            fromstring = html.fromstring(response.content)
            try:
                dubicars_ad = DubicarsAd.objects.get(url=response.url)
            except Exception as e:
                AdError.objects.create(stage='STAGE #3 - UPDATING ADS', step='GET THE AD OBJ', exception=e)
                continue

            print(dubicars_ad.url)
            if dubicars_ad.price == None:
                get_item_details(fromstring, dubicars_ad)
                get_item_description(fromstring, dubicars_ad)
                try:
                    get_item_features(fromstring, dubicars_ad)
                except:
                    pass
                get_related_items(fromstring, dubicars_ad)
                get_similar_items(fromstring, dubicars_ad)
                get_contact_items(fromstring, dubicars_ad)
                get_seo_items(fromstring, dubicars_ad)
                get_breadcrumbs(fromstring, dubicars_ad)
                images = get_images(fromstring, dubicars_ad)
                download_images(images, dubicars_ad)
            else:
                get_item_details(fromstring, dubicars_ad)

            counter += 1

        instance.total_updated_ads_number = counter
        instance.save()

    return











