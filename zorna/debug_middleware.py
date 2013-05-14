# Originally based on: http://djangosnippets.org/snippets/1872/
# Requires sqlparse: http://pypi.python.org/pypi/sqlparse
import time
from django.test.signals import template_rendered
from django.conf import settings
from django.db import connection
from django.utils.encoding import force_unicode
from django.utils.safestring import mark_safe

TEMPLATE = """
<div id="debug" style="clear:both;">
<a href="#debugbox"
    onclick="this.style.display = 'none';
        document.getElementById('debugbox').style.display = 'block';
        return false;"
    style="font-size: small; color: red; text-decoration: none; display: block; margin: 12px;"
>+</a>

<div style="display: none;clear: both; border: 1px solid red; padding: 12px; margin: 12px; overflow: scroll; white-space: wrap;" id="debugbox">

<p>Server-time taken: {{ server_time|floatformat:"5" }} seconds</p>
<p>View: <strong>{{view}}</strong></p>
<p>Templates used:</p>
{% if templates %}
<ol>
    {% for template in templates %}
        <li><strong>{{ template.0 }}</strong> loaded from <samp>{{ template.1 }}</samp></li>
    {% endfor %}
</ol>
{% else %}
    None
{% endif %}
<p>Template path:</p>
{% if template_dirs %}
    <ol>
    {% for template in template_dirs %}
        <li>{{ template }}</li>
    {% endfor %}
    </ol>
{% else %}
    <ul><li>None</li></ul>
{% endif %}
<p>SQL executed:</p>
{% if sql %}
<pre style="margin-left: 2em;">{% for query in sql %}{{ query.sql }}
<strong>took {{ query.time|floatformat:"3" }} seconds</p>{{ query.count }}</strong>
{% endfor %}</pre>
<p>Total SQL time: {{ sql_total }} in {{num_queries}} queries</p>
{% else %}
    {% if not debug %}
    <ol><li>Showing full queries is disabled when settings.DEBUG = False.</li></ol>
    {% else %}
    None
    {% endif %}
{% endif %}
</div>
</div>
</body>
"""

# Monkeypatch instrumented test renderer from django.test.utils - we could use
# django.test.utils.setup_test_environment for this but that would also set up
# e-mail interception, which we don't want
from django.test.utils import instrumented_test_render
from django.template import Template, Context
if Template.render != instrumented_test_render:
    Template.original_render = Template.render
    Template.render = instrumented_test_render
# MONSTER monkey-patch
old_template_init = Template.__init__
def new_template_init(self, template_string, origin=None, name='<Unknown Template>'):
    old_template_init(self, template_string, origin, name)
    self.origin = origin
Template.__init__ = new_template_init

class DebugFooter:
    def process_request(self, request):
        self.time_started = time.time()
        self.templates_used = []
        self.contexts_used = []
        self.sql_offset_start = len(connection.queries)
        template_rendered.connect(self._storeRenderedTemplates)

    def process_response(self, request, response):

        # Don't bother if the url doesn't have the "debug"  query  string
        # Added by Jeff Schroeder for dynamically enabling/disabling this
        if not request.GET.has_key("debug"):
            return response

        # Only include debug info for text/html pages not accessed via Ajax
        if 'text/html' not in response['Content-Type']:
            return response
        if request.is_ajax():
            return response
        if response.status_code != 200:
            return response

        templates = []
        for t in self.templates_used:
            if t.origin and t.origin.name:
                templates.append( (t.name, t.origin.name) )
            else:
                templates.append( (t.name, "no origin") )

        sql_queries = connection.queries[self.sql_offset_start:]
        # Reformat sql queries a bit
        sql_total = 0.0
        sql_counts = {}
        for query in sql_queries:
            raw_sql = query['sql']
            query['sql'] = reformat_sql(query['sql'])
            sql_total += float(query['time'])
            count = sql_counts.get(raw_sql,0) + 1
            sql_counts[raw_sql] = count
            if count > 1:
                query['count'] = mark_safe('<p>duplicate query count=%s</p>' % count)
            else:
                query['count'] = ''

        from django.core.urlresolvers import resolve
        view_func = resolve(request.META['PATH_INFO'])[0]

        view =  '%s.%s' % (view_func.__module__, view_func.__name__)

        vf = view_func
        breaker = 10
        while not hasattr(vf,'func_code'):
            if hasattr(vf,'view_func'):
                vf = vf.view_func
            else:
                break # somethings wrong about the assumptions of the decorator
            breaker = breaker - 1
            if breaker < 0:
                break
        if hasattr(vf,'func_code'):
            co = vf.func_code
            filename = co.co_filename
            lineno = co.co_firstlineno
            view = '- '.join([view, ':'.join([co.co_filename, str(co.co_firstlineno)])])

        debug_content = Template(TEMPLATE).render(Context({
            'debug': settings.DEBUG,
            'server_time': time.time() - self.time_started,
            'templates': templates,
            'sql': sql_queries,
            'sql_total': sql_total,
            'num_queries' : len(sql_queries),
            'template_dirs': settings.TEMPLATE_DIRS,
            'view': view
        }))

        content = response.content
        response.content = force_unicode(content).replace('</body>', debug_content)

        return response

    def _storeRenderedTemplates(self, **kwargs):
        template = kwargs.get('template')
        if(template):
            self.templates_used.append(template)
        context = kwargs.get('context')
        if(context):
            self.contexts_used.append(context)

def reformat_sql(sql):
    if sql:
        import sqlparse
        sql = sqlparse.format(sql, reindent=True, keyword_case='upper')
    return sql