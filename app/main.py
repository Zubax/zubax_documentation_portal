#
# Copyright (C) 2015 Zubax Robotics <info@zubax.com>.
# Author: Pavel Kirienko <pavel.kirienko@zubax.com>
#

import os, re
from functools import reduce
from . import app, cached, render_markdown
from flask import request, render_template, redirect, send_file, Markup
from flask_menu import register_menu, current_menu


class ProductInfo:
    def __init__(self, title, fs_root, url_root, weight, main_page_path):
        self.title = title
        self.fs_root = fs_root
        self.url_root = url_root
        self.weight = weight
        self.forum_url = 'https://productforums.zubax.com/'  # TODO: link the right sub-forum somehow

        with open(main_page_path) as f:
            main_page = render_markdown(f.read(), url_root)
        paragraphs = re.findall(r'<p[^>]*>.+?</p>', main_page, re.DOTALL)
        if paragraphs:
            self.short_description_html = Markup(paragraphs[0])
        else:
            self.short_description_html = Markup(self.title)

    @property
    def image_url(self):
        return self.url_root + '/image.jpg'


PRODUCTS = []


@app.route('/')
@register_menu(app, '.', 'Home', order=0)
@cached()
def index():
    products = sorted(PRODUCTS.copy(), key=lambda x: x.weight)
    return render_template('index.html', **locals())


@app.route('/search')
def search():
    return redirect('https://duckduckgo.com/?q=site:docs.zubax.com ' + request.args['q'])


@app.errorhandler(404)
def not_found(_error):
    return render_template('404.html'), 404


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
                with open(item.fs_path) as f:
                    markdown_source = f.read()
                    url_path = item.parent_url if item.main_page else item.url_path
                    content = render_markdown(markdown_source, url_path)
                    try:
                        page_title = re.findall(r'<h(\d)>([^<]+)</h\1>', content)[0][1]
                    except IndexError:
                        page_title = item.title
                    return render_template('content_page.html', content=content, title=page_title)
            except IsADirectoryError:
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

    for root, dirs, files in os.walk(base_dir):
        root = os.path.abspath(root)
        if root.startswith(ignore_prefix) or root == base_dir or (os.path.sep + '.') in root:
            continue
        if not files and not dirs:
            continue
        root = root[len(base_dir):].strip(os.path.sep)
        for f in files:
            if os.path.splitext(f)[1] == '.md':
                make_content_page_endpoint(ContentStructureItem('leaf', os.path.join(root, f)))
            else:
                make_static_endpoint(ContentStructureItem('static', os.path.join(root, f)))

        make_content_page_endpoint(ContentStructureItem('node', root))

index_content()
