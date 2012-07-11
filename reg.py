import os
import urlparse
import time
import hmac
import hashlib
import base64
from werkzeug.wrappers import Request, Response
from werkzeug.routing import Map, Rule
from werkzeug.exceptions import HTTPException, NotFound
from werkzeug.wsgi import SharedDataMiddleware
from werkzeug.utils import redirect
from jinja2 import Environment, FileSystemLoader

try:
	URL_STEM = os.environ['PHOTOREG_URL_STEM']
	HMAC_KEY = os.environ['PHOTOREG_HMAC_KEY']
	LISTEN_HOST = os.environ['PHOTOREG_LISTEN_HOST']
	LISTEN_PORT = int(os.environ['PHOTOREG_LISTEN_PORT'])
except:
	print "PHOTOREG_URL_STEM, PHOTOREG_HMAC_KEY, LISTEN_HOST, LISTEN_PORT must be set in the environment before running this"
	raise


class Reg(object):
	def __init__(self):
		template_path = os.path.join(os.path.dirname(__file__), 'templates')
		self.jinja_env = Environment(loader=FileSystemLoader(template_path), autoescape=True)

		self.url_map = Map([
			Rule('/',             endpoint='rego_form'),
			Rule('/process_rego', endpoint='process_rego'),
			Rule('/view_all',     endpoint='view_all'),
		])

	def dispatch_request(self, request):
		adapter = self.url_map.bind_to_environ(request.environ)
		try:
			endpoint, values = adapter.match()
			return getattr(self, 'on_' + endpoint)(request, **values)
		except HTTPException, e:
			return e

	def wsgi_app(self, environ, start_response):
		request = Request(environ)
		response = self.dispatch_request(request)
		return response(environ, start_response)

	def __call__(self, environ, start_response):
		return self.wsgi_app(environ, start_response)

	def render_template(self, template_name, **context):
		t = self.jinja_env.get_template(template_name)
		return Response(t.render(context), mimetype='text/html')

	def on_rego_form(self, request):
		error = None
		url = ''
		return self.render_template('rego_form.html', error=error, url=url)

	def on_process_rego(self, request):
		error = None
		url = ''
		if request.method != 'POST':
			return self.render_template('process_rego_bad_GET.html', error=error, url=url)

		name = request.form['name']
		email = request.form['email']
		mobile = request.form['mobile']
		series = request.form['series']
		character_details = request.form['character_details']
		gave_consent = request.form['gave_consent']

		# XXX: Should perform sanity-checking here

		# Generate the tag. It could just be a hash of their name,
		# but that's not meaningful anyway, and isn't necessarily unique.
		# Fuck it, a random number is good enough, just hash
		# the current time and use the first 8 characters in base32 representation.
		# HMAC it with a server secret to discourage guessing. >_>
		timestamp = str(time.strftime('%Y%m%d-%H%M%S'))
		photoset_tag = base64.b32encode( hmac.new(HMAC_KEY, timestamp, hashlib.sha1).digest() )[:8]

		# Make it easier to read
		photoset_tag_pretty = photoset_tag[:4] + '-' + photoset_tag[4:]

		# Generate the URL
		photoset_url = "%s%s" % (URL_STEM, photoset_tag)

		# XXX: Actually put the data somewhere

		# XXX: Print the label

		return self.render_template('process_rego_POST.html', error=error, url=url,
			name=name,
			email=email,
			mobile=mobile,
			series=series,
			character_details=character_details,
			gave_consent=gave_consent,
			photoset_url=photoset_url,
			photoset_tag_pretty=photoset_tag_pretty,
		)

	def on_view_all(self, request):
		error = None
		url = ''
		return self.render_template('view_all.html', error=error, url=url)


def create_app(with_static=True):
	app = Reg()
	if with_static:
		app.wsgi_app = SharedDataMiddleware(app.wsgi_app, {
			'/static':  os.path.join(os.path.dirname(__file__), 'static')
		})
	return app


if __name__ == '__main__':
	from werkzeug.serving import run_simple
	app = create_app()
	run_simple(LISTEN_HOST, LISTEN_PORT, app, use_debugger=True, use_reloader=True)

