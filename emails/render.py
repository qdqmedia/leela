import logging
from copy import deepcopy
from functools import partial

from django.forms.models import model_to_dict
from django.conf import settings
from django.core.mail import make_msgid

import htmlmin
from jinja2 import Environment, Markup

from custom import import_from_module


logger = logging.getLogger('emails')


def render_html(torender, context, test=False, ignore_minify=False):
    """
    Renders the HTML template of an emailkind or fragment with the
    overrides contained in context. The rendered html returned is
    minified if `MINIFY_HTML` is set to True in settings.

    @type torender: EmailKind or EmailKindFragment
    @type context: dict
    @type test: bool
    @type ignore_minify: bool
    @param ignore_minify: if set to True, the value of `MINIFY_HTML`
        in settings is ignored, and the html is not minified.
    """
    try:
        fullcontext = _get_full_context(torender, context)
        if _should_include_fragments(torender):
            fullcontext['fragments'] = _fragments_context(torender, fullcontext,
                                                          test=test, for_plain=False)
        template_string = _render(torender.template, fullcontext, Environment(autoescape=True))
        html = _embed_images(template_string, torender.images.all(), test)
        if (settings.MINIFY_HTML and not ignore_minify):
            html = _minify_html(html)
        return html
    except Exception as e:
        logger.exception(
            'Error rendering the html template of {name} with {ctx}'
            .format(name=torender, ctx=context)
        )
        raise e


def render_plain(torender, context):
    """
    Renders the plain template of an emailkind or fragment with the
    overrides contained in context.
    @type emailkind: EmailKind or EmailKindfragment
    @type context: dict
    """
    fullcontext = _get_full_context(torender, context)
    if _should_include_fragments(torender):
        fullcontext['fragments'] = _fragments_context(torender, fullcontext, for_plain=True)
    return _render(torender.plain_template, fullcontext,
                   Environment(autoescape=False))


def _minify_html(html):
    return htmlmin.minify(
        html,
        remove_comments=True,
        reduce_empty_attributes=False,
        reduce_boolean_attributes=False,
        remove_optional_attribute_quotes=False).strip()


def _should_include_fragments(torender):
    return hasattr(torender, 'fragments')


def _fragments_context(emailkind, context, test=False, for_plain=False):
    """
    Returns a dict containing all the rendered fragments for a given
    email kind and its context. The dict keys will be the fragment name
    and the value a jinja2 html-safe string containing the rendered fragment
    content.
    @type emailkind: EmailKind

    @param context: the emailkind full context
    @type context dict

    @param test: tells if the rendering is for testing
    @type test: bool

    @param for_plain: tells if the context is for plain text rendering.
    @type for_play: bool
    """
    render_fn = render_plain if for_plain else partial(render_html, test=test, ignore_minify=True)
    return {fragment.name: Markup(render_fn(fragment, context))
            for fragment in emailkind.fragments.filter(is_plain=for_plain)}


def _get_full_context(emailkind, additional):
    default = emailkind.default_context
    fullcontext = deepcopy(default)
    fullcontext['meta'] = model_to_dict(emailkind)
    fullcontext.update(additional)
    return fullcontext


def _render(template_string, fullcontext, env):
    for filt in settings.FILTERS:
        env.filters[filt[0]] = import_from_module(filt[1])
    template = env.from_string(template_string)
    return template.render(fullcontext)


def _embed_images(template, images, test=False):
    for image in images:
        src_attr = 'src="cid:{}"'.format(image.placeholder_name)
        if test:
            replace_src = 'src="{}"'.format(image.image.url)
        else:
            if not len(image.content_id):
                image.content_id = make_msgid(image.placeholder_name)
                image.save()
            replace_src = 'src="cid:{}"'.format(image.content_id[1:-1])
        template = template.replace(src_attr, replace_src)
    return template
