#
# Copyright (C) 2015 Zubax Robotics <info@zubax.com>.
# Author: Pavel Kirienko <pavel.kirienko@zubax.com>
#

import os, re, logging, yaml
from functools import reduce
from . import app, cached, render_markdown_from_file, resolve_relative_path
from flask import request, render_template, redirect, send_file, Markup
from flask_menu import register_menu, current_menu
from bs4 import BeautifulSoup


logger = logging.getLogger(__name__)


def get_excerpt(markdown_source_path, url_root):
    main_page = render_markdown_from_file(markdown_source_path, url_root)
    borscht = BeautifulSoup(main_page, 'html5lib')
    disallowed_tags = ['div', 'img', 'table']
    for p in borscht.find_all('p'):
        if all(ch not in disallowed_tags for ch in p.children) and re.match(r'\S', p.text):
            return Markup(str(p))


def get_image(markdown_source_path, url_root):
    main_page = render_markdown_from_file(markdown_source_path, url_root)
    borscht = BeautifulSoup(main_page, 'html5lib')
    # Looking for an image tag with the correct ID
    for tag in borscht.recursiveChildGenerator():
        if tag.name is None:
            continue
        if tag.name == 'img' and tag.attrs.get('id') == 'preview':
            return tag.attrs['src']
    # Looking for an image before first h2 tag
    for tag in borscht.recursiveChildGenerator():
        if tag.name is None:
            continue
        if tag.name.startswith('h2'):
            return
        if tag.name == 'img':
            return tag.attrs['src']


class ProductInfo:
    def __init__(self, title, fs_root, url_root, weight, main_page_path):
        self.title = title
        self.fs_root = fs_root
        self.url_root = url_root
        self.weight = weight
        self.tutorials_url = None
        self.tutorial_items = []
        self.short_description_html = get_excerpt(main_page_path, url_root) or Markup(self.title)

        try:
            with open(resolve_relative_path(os.path.join(self.fs_root, 'options.yaml'))) as f:
                self.config = yaml.load(f)
                logger.info('Product config for %r: %r', self.title, self.config)
        except OSError:
            logger.info('Could not read config file for product %r', self.title)
            self.config = {}

    @property
    def support_url(self):
        return self.config.get('support_url', app.config['SUPPORT_URL'])

    @property
    def image_url(self):
        return self.url_root + '/image.jpg'


PRODUCTS = []


def find_product(item):
    for p in PRODUCTS:
        if item.url_path.startswith(p.url_root + '/'):
            return p


@app.route('/')
@register_menu(app, '.', 'Home', order=0)
@cached()
def index():
    products = sorted(PRODUCTS.copy(), key=lambda x: x.weight)
    logger.info('Rendering index page with %s products', len(products))
    return render_template('index.html', **locals())


@app.route('/search')
def search():
    logger.info('Search request %r', request.args['q'])
    return redirect('https://duckduckgo.com/?q=site:docs.zubax.com ' + request.args['q'])


def make_content_page_endpoint(item):
    if item.void:
        @app.before_first_request
        def register_node():
            if not current_menu.submenu(item.menu_path, False):
                current_menu.submenu(item.menu_path).register(None, item.title, item.weight, item=item)
    else:
        @cached()
        def endpoint():
            try:
                logger.info('Rendering %r, %r with relative URL %r', item.url_path, item.fs_path, item.parent_url)
                content = render_markdown_from_file(item.fs_path, item.parent_url)
                try:
                    page_title = re.findall(r'<h(\d)>([^<]+)</h\1>', content)[0][1]
                except IndexError:
                    page_title = item.title
                return render_template('content_page.html', content=content, title=page_title)
            except IsADirectoryError:
                if item.url_path.endswith('/tutorials') and item.category == 'Products':
                    logger.info('Rendering tutorial listing at %r', item.url_path)
                    docs = []
                    product = find_product(item)
                    for tut in product.tutorial_items:
                        docs.append({
                            'title': tut.title,
                            'url': tut.url_path,
                            'excerpt': get_excerpt(tut.fs_path, tut.parent_url),
                            'image_url': get_image(tut.fs_path, tut.parent_url),          # Not used now
                        })
                    page_title = product.title + ' &#8212; Tutorials'
                    return render_template('document_list.html', items=docs, title=page_title)
                else:
                    logger.info('Rendering one level up from %r', item.url_path)
                    return redirect(item.parent_url)

        endpoint.__name__ = 'content_page' + item.url_path.replace('/', '_')

        def active_when():
            if item.main_page:
                return request.path == item.parent_url
            else:
                return request.path == item.url_path

        if item.main_page:
            app.add_url_rule(item.parent_url, view_func=endpoint)
            register_menu(app, item.menu_path, item.title, 0, active_when=active_when, item=item)(endpoint)
        else:
            app.add_url_rule(item.url_path, view_func=endpoint)
            register_menu(app, item.menu_path, item.title, item.weight, active_when=active_when, item=item)(endpoint)


def make_static_endpoint(item):
    path = os.path.join(app.config['BASE_DIR'], item.fs_path)

    @app.route(item.url_path, endpoint='static' + item.url_path.replace('/', '_'))
    def endpoint():
        return send_file(path, cache_timeout=600)


class ContentStructureItem:
    @staticmethod
    def parse_weight_title(p):
        try:
            weight, title = p.split(maxsplit=1)
            return int(weight), os.path.splitext(title)[0]
        except ValueError:
            weight = reduce(lambda a, x: a * 100 + (ord(x) - 32), p.ljust(8)[:8], 0)
            return weight, os.path.splitext(p)[0]

    @staticmethod
    def fs_path_to_url(fs_path):
        p = '/'.join([ContentStructureItem.parse_weight_title(x)[1]
                      for x in fs_path.split(os.path.sep)]).replace(' ', '_').lower()
        p = re.sub(r'[^a-z0-9_\-/]', '', p)
        return '/' + p

    def __init__(self, item_type, fs_path):
        self.fs_path = fs_path
        self.type = item_type
        assert self.type in ('node', 'leaf', 'static')

        raw_url_path = ContentStructureItem.fs_path_to_url(fs_path)
        if self.type == 'static':
            raw_url_path = raw_url_path.rsplit('/', 1)[0] + '/' + os.path.split(fs_path)[-1]
        else:
            self.menu_path = raw_url_path.replace('/', '.')
            self.weight, self.title = ContentStructureItem.parse_weight_title(os.path.basename(fs_path))
            self.category = ContentStructureItem.parse_weight_title(fs_path.split(os.path.sep)[0])[1]

        self.url_path = re.sub(r'^/[^/]+', '', raw_url_path)

        if self.main_page and '/' not in self.parent_url.strip('/'):
            fs_root = os.path.dirname(fs_path)
            url_root = self.parent_url
            prod_weight, prod_title = ContentStructureItem.parse_weight_title(os.path.split(fs_root)[-1])
            if self.category == 'Products':
                PRODUCTS.append(ProductInfo(prod_title, fs_root, url_root, prod_weight, self.fs_path))

        if self.type == 'node' and self.category == 'Products' and self.url_path.endswith('/tutorials'):
            find_product(self).tutorials_url = self.url_path

        if self.type == 'leaf' and self.category == 'Products' and '/tutorials/' in self.url_path:
            find_product(self).tutorial_items.append(self)
            find_product(self).tutorial_items = list(sorted(find_product(self).tutorial_items, key=lambda x: x.weight))

    @property
    def void(self):
        return self.url_path.strip() == ''

    @property
    def main_page(self):
        return self.type == 'leaf' and self.weight == 0 and not self.void

    @property
    def parent_url(self):
        return self.url_path.rsplit('/', 1)[0]


def index_content():
    base_dir = os.path.abspath(app.config['BASE_DIR'])
    ignore_prefix = os.path.join(base_dir, 'app')

    def is_valid_path(p):
        if root.startswith(ignore_prefix):
            return False
        if root == base_dir:
            return False
        if (os.path.sep + '.') in root:
            return False
        if (os.path.sep + '_') in root:
            return False
        return True

    for root, dirs, files in os.walk(base_dir):
        root = os.path.abspath(root)
        if not is_valid_path(root):
            continue
        if not files and not dirs:
            continue
        root = root[len(base_dir):].strip(os.path.sep)
        for f in files:
            ext = os.path.splitext(f)[1]
            if ext == '.md':
                make_content_page_endpoint(ContentStructureItem('leaf', os.path.join(root, f)))
            elif ext != '.yaml':
                make_static_endpoint(ContentStructureItem('static', os.path.join(root, f)))

        make_content_page_endpoint(ContentStructureItem('node', root))

index_content()
