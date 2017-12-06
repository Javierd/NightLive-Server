from flask import Blueprint, render_template
from jinja2 import TemplateNotFound

web_page = Blueprint('web_page', __name__,
                        template_folder='templates')

@web_page.route('/')
def index():
	return render_template('index.html')

@web_page.route('/about')
def about():
	return render_template('about.html')

@web_page.route('/businessWeb')
def business():
	return render_template('business_web.html')

@web_page.route('/contact')
def contact():
	return render_template('contact.html')

@web_page.errorhandler(404)
def page_not_found(e):
    return render_template('404.html')