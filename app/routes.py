#import flask app
from app import app 
#import dos metodos do flask
from flask import Flask, request, render_template, url_for, redirect, flash
#import do objeto do banco de dados
from app import database
#import das coleções do banco de dados
from app.models.learning_object import LearningObject
from app.models.site import Site
from app.models.user import User
#import dos formulários
from app.models.forms import LoginForm, RegisterForm, ProfileForm
#import do contralador de seção do usuário e verificação de senha
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash
#import do controller da api do stackexchange
from app.controllers.api_stackexchange import StackExchange
#outros imports
import json


list_sites = []
list_results = []

#### ROTAS DA APLICAÇÃO ####

#### home ####

@app.route("/")
@app.route("/index/")
@login_required
def index():
    try:
        number_sites = len(database.list("sites"))
    except:
        number_sites = 0
        
    try:
        number_learning_objects = len(database.list("learning_objects"))
    except:
        number_learning_objects = 0
    return render_template("index.html", number_sites=number_sites, number_learning_objects=number_learning_objects)

#### sites ####

@app.route("/search_sites/", methods=['GET'])
@login_required
def search_sites():
    sites_database = database.list("sites")
    stackexchange = StackExchange(100, None)
    pages_sites = stackexchange.sites()
    if sites_database:
        for page in pages_sites:
            for site in page["items"]:
                site_object = Site(site)
                site_json = site_object.get_as_json()
                for site_database in sites_database:
                    if site_json["site"]["api_parameter"] == site_database["site"]["api_parameter"]:
                        site_update = {**site_database, **site_json}
                        break
                if site_update != None or "":
                    database.update("sites", site_update)
                    break
                else:
                    database.create("sites", site_object)
                    break
    else:
        for page in pages_sites:
            for site in page["items"]:
                try:
                    site_object = Site(site)
                    database.create("sites", site_object)
                except:
                    continue
    return redirect(url_for('view_sites'))

@app.route("/view_sites/", methods=['GET'])
@login_required
def view_sites():
    sites = database.list("sites")
    list_sites = []
    for site in sites:
        list_sites.append(site["site"])
    return render_template("view_sites.html", sites=list_sites)


#### learning_object ####

@app.route("/search_api/", methods=['GET'])
@login_required
def search_api():
    sites = database.list("sites")
    global list_sites
    list_sites = []
    for site in sites:
        list_sites.append(site["site"])
    return render_template("search_api.html", sites=list_sites)

@app.route("/results_search_api/", methods=['POST'])
@login_required
def results_search_api():
    search = request.form.get('search')
    stackexchange = StackExchange(2, 1)
    
    sites = database.list("sites")
    list_sites_api = []
    global list_results
    list_results = []
    select = request.form.getlist('multi-select')
    if select:
        for option in select:                                       ### criar ium objeto learning object, passar ele para uma variavel e em seguida colocar na lista para mandar para o html
            option = option.split("-")[1]
            print(option)
            for site in sites:
                if option == site["site"]["api_parameter"]:
                    list_sites_api.append(site["site"]["api_parameter"])
                    break
    for api_parameter in list_sites_api:
        list_result_items = stackexchange.search_advanced(str(search), str(api_parameter))
        list_results.append(list_result_items)
    
    return render_template("results_search_api.html", list_results=list_results)

@app.route("/save_search/<int:index_list_results>/<int:index_result>/")
@login_required
def save_search(index_list_results, index_result):
    global list_sites
    global list_results
    name_site = list_sites[int(index_list_results)]["name"]
    api_site = list_sites[index_list_results]["api_parameter"]
    save_item = list_results[index_list_results][index_result]
    learning_object = (LearningObject(save_item, name_site, api_site))
    database.create("learning_objects", learning_object)
    return render_template("results_search_api.html", list_results=list_results)

@app.route("/search_database/")
def search_database():
    sites = database.list("sites")
    global list_sites
    for site in sites:
        list_sites.append(site["site"])
    return render_template("search_database.html", sites=list_sites)

@app.route("/results_search_database/")
def results_search_database():
    
    pass

@app.route("/view_learning_objects/")
def view_learning_objects():
    
    pass

#### Login, Registro, Perfil e Logout ####

#Criar Conta
@app.route("/register/", methods=['GET', 'POST'])
def register():
    if not current_user.is_authenticated:
        form = RegisterForm()
        if form.validate_on_submit():
            name = form.name.data
            email = form.email.data
            password = form.password.data
            query = database.filter_by('users', {"email": email})
            if not query:
                user = User(name, email, password)
                database.create("users", user)
                flash('Conta registrada com sucesso!', 'success')
                return redirect(url_for("login"))
            else:
                flash('Email já cadastrado', 'danger')
        return render_template('register.html', form=form)
    else:
        return redirect(url_for("index"))

#Login
@app.route("/login/", methods=['GET', 'POST'])
def login():
    if not current_user.is_authenticated:
        form = LoginForm()
        if form.validate_on_submit():
            email = form.email.data
            password = form.password.data
            remember = form.remember.data
            print(remember)
            query = database.filter_by('users', {"email": email})
            if query:
                user_bd = query[0]
                if check_password_hash(user_bd['password'], password):
                    user = User(user_bd['name'], user_bd['email'], user_bd['password'])
                    login_user(user, remember=remember)
                    flash('Login realizado com sucesso!', 'success')
                    return redirect(url_for("index"))
                else:
                    flash('Problema com o login. Por favor verifique seu email e senha.', 'danger')
        return render_template('login.html', form=form)
    else:
        return redirect(url_for("login"))

#Logout
@app.route("/logout/", methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))

#Profile
@app.route("/profile/", methods=['GET', 'POST'])
@login_required
def profile():
    form = ProfileForm()
    error = None
    if form.validate_on_submit():
        name = form.name.data
        email = form.email.data
        current_password = form.current_password.data
        new_password = form.new_password.data
        repeat_new_password = form.repeat_new_password.data
        # Saber se email é o mesmo
        query = database.filter_by('users', {"email": email})
        if query:
            user_bd = query[0]
            is_email_used = True
            is_email_same = (user_bd['email'] == current_user.email)
        else:
            is_email_used = False
            is_email_same = False
        if not is_email_used or is_email_same:
            #verificar se a senha atual é igual
            user_bd = database.filter_by('users', {"email": current_user.email})
            user_bd = user_bd[0]
            is_pass_ok = check_password_hash(user_bd['password'], current_password)
            if is_pass_ok:
                if new_password == repeat_new_password:
                    user_bd['name'] = name
                    user_bd['password'] = new_password
                    user_bd['email'] = email

                    
                    database.update("users", user_bd)
                    return redirect(url_for("index"))
                else:
                    error = 3 # Nova Senha Não coincide
            else:
                error = 2 #Senha atual está errada
        else:
            error = 1 #Email está em uso e não é o mesmo
    else:
        form.name.data = current_user.name
        form.email.data = current_user.email
        print(form.errors)
    
    return render_template('profile.html', form=form, error=error)
    
#### tratamento de exceções nas rotas ####

@app.errorhandler(404)
def errorPage(e):
    return render_template('404.html')
    
@app.errorhandler(401)
def page_not_found(e):
    return redirect(url_for("login"))

@app.errorhandler(500)
def errorPage(e):
    return render_template('500.html')


#### test ####

@app.route("/test/", methods=['GET'])
def test():
    return render_template("profile.html")
