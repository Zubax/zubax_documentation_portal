#
# Copyright (C) 2015 Zubax Robotics <info@zubax.com>.
# Author: Pavel Kirienko <pavel.kirienko@zubax.com>
#

import os, time, logging, re
from functools import wraps
from flask import Flask, render_template, send_from_directory, request, Markup, g, redirect
from flask_menu import Menu
from flask.ext.assets import Environment
from flask.ext.misaka import Misaka
from werkzeug.contrib.cache import SimpleCache
from bs4 import BeautifulSoup
import pygments, pygments.lexers, pygments.formatters
import misaka

app = Flask(__name__.split('.')[0])

app.config.from_object('config')

assets = Environment(app)

menu = Menu(app)

misaka_instance = Misaka(app)

cache = SimpleCache()

logger = logging.getLogger('app')


class MarkdownRenderer(misaka.HtmlRenderer):
    def block_code(self, text, lang):
        if not lang:
            return '\n<pre><code>%s</code></pre>\n' % Markup.escape(text)
        lexer = pygments.lexers.get_lexer_by_name(lang, stripall=True)
        formatter = pygments.formatters.HtmlFormatter()
        rendered = pygments.highlight(text, lexer, formatter)
        return rendered


def resolve_relative_path(p):
    if not os.path.isabs(p):
        p = os.path.join(app.config['BASE_DIR'], p)
    return p


def render_markdown(source, relative_url):
    # Rendering the hard way because we need pygments
    renderer = MarkdownRenderer()
    md = misaka.Markdown(renderer, extensions=misaka.EXT_TABLES | misaka.EXT_FENCED_CODE | misaka.EXT_AUTOLINK |
                         misaka.EXT_STRIKETHROUGH)
    pre_rendered = md(source)
    rendered = misaka.smartypants(pre_rendered)

    # Yay slowest markdown renderer ever
    hygiene = BeautifulSoup(rendered, 'html5lib')

    # Styling tables
    for tag in hygiene.find_all('table'):
        tag.attrs['class'] = 'table table-striped table-condensed table-bordered'

    # Fixing local path entries
    def fix_path(path):
        path = path.strip()
        if path.startswith('/') or path.startswith('#') or ':/' in path:
            return path
        return '/'.join([relative_url, path])

    for tag_name in ['a', 'img']:
        for x in hygiene.find_all(tag_name):
            for attr_name in ['src', 'href']:
                if attr_name in x.attrs:
                    x.attrs[attr_name] = fix_path(x.attrs[attr_name])

    # Every image must be wrapped into a link tag
    for img in hygiene.find_all('img'):
        if img.parent.name != 'a':
            a = hygiene.new_tag('a', href=img.attrs['src'])
            img.insert_after(a)
            img.extract()
            a.append(img)

    # Enabling Lightbox on images
    image_id = 0
    for a in hygiene.find_all('a'):
        if a.img:
            a.attrs['data-lightbox'] = 'image-%d' % image_id
            image_id += 1
            if a.img.attrs.get('title') or a.img.attrs.get('alt'):
                a.attrs['data-title'] = a.img.attrs.get('title') or a.img.attrs.get('alt')

    # Rendering alert boxes
    for alert_name in ['info', 'warning', 'danger']:
        for x in hygiene.find_all(alert_name):
            alert_name = x.name
            x.name = 'div'
            x.attrs['class'] = 'alert alert-' + alert_name

    # Generating table of contents anchors.
    # JS-based solution doesn't quite work because if anchors are not set at page load time the browser won't scroll.
    for header in ['h2', 'h3', 'h4', 'h5']:
        for h in hygiene.find_all(header):
            anchor = ''.join(h.strings).strip()
            anchor = re.sub(r'\s', '_', anchor)
            anchor = re.sub(r'[^A-Za-z0-9\-_:\.]', '', anchor)
            h.attrs['id'] = anchor

    # Oi moroz moroz ne moroz mena
    return Markup(str(hygiene))  # Ne moroz mena moigo kona


def render_markdown_from_file(path, relative_url):
    with open(resolve_relative_path(path), encoding='utf8') as f:
        return render_markdown(f.read(), relative_url)


def cached(timeout=None, key=None):
    timeout = timeout or 99999999999
    key = key or 'view/%s'

    if app.config.get('DEBUG', False):
        timeout = min(timeout, 3)

    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            cache_key = key % request.path
            rv = cache.get(cache_key)
            if rv is not None:
                return rv
            rv = f(*args, **kwargs)
            cache.set(cache_key, rv, timeout=timeout)
            return rv
        return decorated_function

    return decorator


from app import main


@app.before_request
def before_request():
    g.request_timestamp = time.time()
    g.get_request_rel_time_ms = lambda: int((time.time() - g.request_timestamp) * 1000 + 1)


@app.after_request
def after_request(response_class):
    processing_time_ms = g.get_request_rel_time_ms()
    log_method = logger.debug if processing_time_ms < 100 else logger.warning
    log_method('Request %r processed in %d ms', request.path, processing_time_ms)
    return response_class


def try_desperate_redirect(path):
    # Compatibility with the old website
    redirects = {
        '/Main_Page': '/',
        '/Zubax_GNSS': '/zubax_gnss',
        '/DroneCode_Probe': '/dronecode_probe',
        '/UAVCAN_Interface': '/uavcan'
    }

    if path in redirects:
        target = redirects[path]
        logger.info('Compat redirect %r --> %r', path, target)
        return redirect(target)

    if path.lower().startswith('/zubax_gnss_tutorial'):
        return redirect('/zubax_gnss/tutorials')


@app.errorhandler(404)
def not_found(_error):
    red = try_desperate_redirect(request.path)
    if red:
        return red

    return render_template('http_error.html', error_description='File not found (404)'), 404


@app.errorhandler(500)
def not_found(_error):
    return render_template('http_error.html', error_description='Internal server error (500)'), 500


@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'), 'favicon.ico', mimetype='image/x-icon')


@app.route('/favicon-152.png')
def favicon_152():
    return send_from_directory(os.path.join(app.root_path, 'static'), 'favicon-152.png', mimetype='image/png')
