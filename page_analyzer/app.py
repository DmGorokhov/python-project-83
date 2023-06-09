from flask import (Flask, request, render_template,
                   redirect, url_for, flash, abort)
from page_analyzer.services.database import DBUrlsModel, DBSession
from page_analyzer.services.validator import is_valid_url, get_parsed_url
from page_analyzer.services.parser import make_urlcheck
from page_analyzer.settings import Configs


app = Flask(__name__)
configs = Configs()

app.config["SECRET_KEY"] = configs.secret_key
DATABASE_URL = configs.db_url


@app.route("/")
def index():
    return render_template('index.html')


@app.route('/urls')
def get_urls():
    db_connection = DBSession(DATABASE_URL)
    repo_urls = DBUrlsModel(db_connection)
    urls = repo_urls.get_urls_list()
    db_connection.close()

    return render_template('urls_index.html', urls=urls)


@app.route('/urls/<int:id>')
def get_url(id):
    db_connection = DBSession(DATABASE_URL)
    repo_urls = DBUrlsModel(db_connection)
    url = repo_urls.get_url(id)
    if url:
        checks_list = repo_urls.get_url_checks(id)
        db_connection.close()
        return render_template('show_url.html', url=url,
                               checks_list=checks_list)
    abort(404)


@app.post("/urls")
def urls_post():
    url = request.form.get('url')

    if is_valid_url(url):
        parsed_url = get_parsed_url(url)
        db_connection = DBSession(DATABASE_URL)
        repo_urls = DBUrlsModel(db_connection)
        url_id = repo_urls.find_url(parsed_url)
        if url_id:
            message = ('Страница уже существует', 'info')
        else:
            url_id = repo_urls.add_url(parsed_url)
            message = ('Страница успешно добавлена', 'success')
        db_connection.close()
        flash(*message)
        return redirect(url_for('get_url', id=url_id), code=302)

    flash('Некорректный URL', 'danger')
    return render_template('index.html', uncorrect_url=url), 422


@app.post('/urls/<id>/checks')
def check_url(id):
    db_connection = DBSession(DATABASE_URL)
    repo_urls = DBUrlsModel(db_connection)
    url = repo_urls.get_url(id)
    url_check = make_urlcheck(url.get('id'), url.get('name'))
    if url_check:
        repo_urls.add_check(url_check)
        db_connection.close()
        message = ('Страница успешно проверена', 'success')
    else:
        message = ('Произошла ошибка при проверке', 'danger')
    flash(*message)
    return redirect(url_for('get_url', id=url['id']))


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500
