#import flask app
from functools import cache
from typing import Mapping
from flask_wtf import Form
from app import app, mail
#import dos metodos do flask
from flask import Flask, request, render_template, url_for, redirect, flash
#import do objeto do banco de dados
from app import database
#import das coleções do banco de dados
from app.models.learning_object import LearningObject
from app.models.site import Site
from app.models.user import User
#import dos formulários
from app.models.forms import LoginForm, RegisterForm, ProfileForm, ForgotPasswordForm, VerifyCodeForgotPasswordForm, ChangePasswordForm
#import do contralador de seção do usuário e verificação de senha
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash
#import do controller da api do stackexchange
from app.controllers.api_stackexchange import StackExchange
#outros imports
import datetime
import time
import pytz
import random
from flask_mail import Message
import secrets

#### Cache do sistema ####

#lista para gestão do cache antes do login do usuário
cache_app_before_login = []

#lista para gestão do cache depois do login do usuário
cache_app_after_login = []

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
                        #site_update = {**site_database, **site_json}
                        site_update = site_json
                        database.update("sites", site_database, site_update)       
                        break
                if site_update == None or "":
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
    #global list_sites
    list_sites = []
    for site in sites:
        list_sites.append(site["site"])
    return render_template("search_api.html", sites=list_sites)

@app.route("/results_search_api/", methods=['POST'])
@login_required
def results_search_api():   
    global cache_app_after_login
    stackexchange = StackExchange(30, 1)
    sites = database.list("sites")
    list_sites_api = []
    list_results = []
    
    #pegar as datas
    date_start = datetime.datetime.strptime(request.form.get('date_start')[:10], "%d/%m/%Y").replace(tzinfo=pytz.utc).timestamp() #para pegar somente a data
    date_end = datetime.datetime.strptime(request.form.get('date_end')[:10], "%d/%m/%Y").replace(tzinfo=pytz.utc).timestamp() #para pegar somente a data
    #pegar as ordenações
    selected_sort = request.form.get('selected-sort')
    selected_order = request.form.get('selected-order')
    #pegar as tags e não tags
    selected_tagged = request.form.get('selected-tagged')
    selected_nottagged = request.form.get('selected-nottagged')
    #pegar os sites
    selected_sites = request.form.getlist('selected-sites')
    #pegar seleção de somente perguntas aceitas
    accepted = request.form.get('accepted')
    #pegar o tipo da busca
    selected_type_search = request.form.getlist('selected-type-search') 
    #pegar a busca
    search = request.form.get('search')
    #date_format = ciso8601.parse_datetime(str(date_start))
    # to get time in seconds:
    #print(time.mktime(date_format.timetuple()))
    """print(date_start)
    print(date_end)
    print(selected_sort)
    print(selected_order)
    print(selected_tagged)
    print(selected_nottagged)
    print(selected_type_search[0])
    print(accepted)"""
    
    if selected_sites:
        for option in selected_sites:
            option = option.split("-")[1]
            for site in sites:
                if option == site["site"]["api_parameter"]:
                    list_sites_api.append(site["site"])
                    break
    for site in list_sites_api:
        #list_result_items = stackexchange.search_advanced(str(search), str(site["api_parameter"]))
        list_result_items = stackexchange.search_advanced(str(search), str(site["api_parameter"]), date_start, date_end, str(selected_sort), str(selected_order), accepted, selected_tagged, selected_nottagged, str(selected_type_search[0]))
        list_results.append(list_result_items)
    
    update_results = []
    update = []
    for results, site in zip(list_results, list_sites_api):
        for result in results:
            item_db = database.filter_by('learning_objects', {"general.identifier": result["question_id"]})
            if item_db:
                update.append(1)
            else:
                update.append(0)
        update_results.append(update)
        update = []
    
    cache_user = []
    for x in range(len(cache_app_after_login)):
        if current_user.email == cache_app_after_login[x][0]:              
            cache_user = cache_app_after_login[x]
            break        
    if cache_user:
        cache_user[1] = list_results
        cache_user[2] = list_sites_api
        cache_user[3] = update_results
    else:
        cache_user.append(current_user.email)
        cache_user.append(list_results)
        cache_user.append(list_sites_api)
        cache_user.append(update_results)
        cache_app_after_login.append(cache_user)
    
    return render_template("results_search_api.html", list_results=cache_user[1], list_sites_api=cache_user[2], update_results=cache_user[3])

@app.route("/save_search/<int:index_list_results>/<int:index_result>/<string:name_site>/<string:api_site>")
@login_required
def save_search(index_list_results, index_result, name_site, api_site):
    list_results = []
    list_sites_api = []
    update_results = []
    cache_user = []
    global cache_app_after_login
    user = None
    for x in range(len(cache_app_after_login)):
        if current_user.email == cache_app_after_login[x][0]:              
            cache_user = cache_app_after_login[x]
            user = x
            break  
    if cache_user:                                
        list_results = cache_user[1]
        list_sites_api = cache_user[2]
        update_results = cache_user[3]       
    save_item = list_results[index_list_results][index_result]
    #verificar se já esta no banco de dados e impedir de incluir novamente
    learning_object = LearningObject(save_item, name_site, api_site)
    learning_object_json = learning_object.get_as_json()
    item_db = database.filter_by('learning_objects', {"general.identifier": learning_object_json['general']['identifier'][1]})
    if not item_db:
        print("create")
        database.create("learning_objects", learning_object)
        update_results[index_list_results][index_result] = 1
        cache_user[3] = update_results
        cache_app_after_login[user] = cache_user
        return render_template("results_search_api.html", list_results=list_results, list_sites_api=list_sites_api, update_results=update_results)
    else:
        print("update")
        database.update("learning_objects", item_db[0])
        return render_template("results_search_api.html", list_results=list_results, list_sites_api=list_sites_api, update_results=update_results)

@app.route("/search_database/")
def search_database():
    sites = database.list("sites")
    list_sites = []
    for site in sites:
        list_sites.append(site["site"])
    return render_template("search_database.html", sites=list_sites)

@app.route("/results_search_database/")
def results_search_database():
    date_start = datetime.datetime.strptime(request.form.get('date_start')[:10], "%d/%m/%Y").replace(tzinfo=pytz.utc).timestamp() #para pegar somente a data
    date_end = datetime.datetime.strptime(request.form.get('date_end')[:10], "%d/%m/%Y").replace(tzinfo=pytz.utc).timestamp() #para pegar somente a data
    #pegar as ordenações
    selected_sort = request.form.get('selected-sort')
    selected_order = request.form.get('selected-order')
    #pegar as tags e não tags
    selected_tagged = request.form.get('selected-tagged')
    selected_nottagged = request.form.get('selected-nottagged')
    #pegar os sites
    selected_sites = request.form.getlist('selected-sites')
    #pegar seleção de somente perguntas aceitas
    accepted = request.form.get('accepted')
    #pegar o tipo da busca
    selected_type_search = request.form.getlist('selected-type-search') 
    #pegar a busca
    search = request.form.get('search')
    pass

@login_required
@app.route("/view_learning_objects/")
def view_learning_objects():
    learning_objects = database.list("learning_objects")
    list_learning_objects = []
    for learning_object in learning_objects:
        list_learning_objects.append(learning_object)
    return render_template("view_learning_objects.html", learning_objects=list_learning_objects)

@login_required
@app.route("/view_learning_object/<string:id_learning_object_0>/<int:id_learning_object_1>", methods=['GET', 'POST'])
def view_learning_object(id_learning_object_0, id_learning_object_1):
    learning_object = database.filter_by('learning_objects', {"general.identifier": id_learning_object_0,"general.identifier": id_learning_object_1})
    return render_template("view_learning_object.html", learning_object=learning_object[0])

@login_required
@app.route("/edit_learning_object/<string:id_learning_object_0>/<int:id_learning_object_1>", methods=['GET', 'POST'])
def edit_learning_object(id_learning_object_0, id_learning_object_1):
    learning_object = database.filter_by('learning_objects', {"general.identifier": id_learning_object_0,"general.identifier": id_learning_object_1})
    return render_template("edit_learning_object.html", learning_object=learning_object[0])

@login_required
@app.route("/save_edit/<string:id_learning_object_0>/<int:id_learning_object_1>", methods=['GET', 'POST'])
def save_edit(id_learning_object_0, id_learning_object_1):
    save_edit_learning_object = request.get_json()
    if save_edit_learning_object:
        learning_object_db = database.filter_by('learning_objects', {"general.identifier": id_learning_object_0,"general.identifier": id_learning_object_1})
        database.update("learning_objects", learning_object_db[0], save_edit_learning_object)
        #print('\n',json.dumps(save_edit_learning_object, indent=2),'\n')
    return redirect(url_for("view_learning_objects"))

@login_required
@app.route("/delete_learning_object/<string:id_learning_object_0>/<int:id_learning_object_1>")
def delete_learning_object(id_learning_object_0, id_learning_object_1):
    learning_object_db = database.filter_by('learning_objects', {"general.identifier": id_learning_object_0,"general.identifier": id_learning_object_1})
    database.delete("learning_objects", learning_object_db[0])
    return redirect(url_for("view_learning_objects"))

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
        return redirect(url_for("index"))

#Logout
@app.route("/logout/", methods=['GET', 'POST'])
@login_required
def logout():
    global cache_app_after_login
    for x in range(len(cache_app_after_login)):
        if current_user.email == cache_app_after_login[x][0]:              
            cache_app_after_login.pop(x)
            break
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
    
    return render_template('profile.html', form=form, error=error)

#ForgotPassword
@app.route("/forgot_password/", methods=['GET', 'POST'])
def forgot_password():
    if not current_user.is_authenticated:
        form = ForgotPasswordForm()
        if form.validate_on_submit():
            
            return redirect(url_for("send_code_mail", email=form.email.data))
        else:
            return render_template('forgot_password.html', form=form)
    else:
        return redirect(url_for("login"))
    

        
#### Envio de email ####
@app.route("/send_code_mail/<string:email>", methods=['GET', 'POST'])
def send_code_mail(email):
    if not current_user.is_authenticated:
        global cache_app_before_login
        query = database.filter_by('users', {"email": email})
        if query:
            user_bd = query[0] 
            
            #gera codigo temporário para recuperar a senha
            number = range(0, 9)
            code_temp = ''
            for i in range(6):
                code_temp += str(random.choice(number))
            
            #gerando hash de segurança do link de recuperação
            token_temp = secrets.token_hex(64)
                        
            #gestão do cache
            cache_user_temp = [] 
            for x in range(len(cache_app_before_login)):
                if user_bd['email'] == cache_app_before_login[x][0]:              
                    cache_user_temp = cache_app_before_login[x]
                    break        
            if cache_user_temp:
                cache_user_temp[0] = user_bd
                cache_user_temp[1] = int(code_temp)
                cache_user_temp[2] = str(token_temp)
            else:
                cache_user_temp.append(user_bd)
                cache_user_temp.append(int(code_temp))
                cache_user_temp.append(str(token_temp))
                cache_app_before_login.append(cache_user_temp)
            
            msg = Message(
                'Código para recuperação de senha!',
                recipients=['jefersonpks@gmail.com'],
            )
            msg.html = f"""  
                <div class="text-align:center">
                    <p>
                        <h2>Para resuperar a sua senha use o código:<h2>
                    </p>
                    <table style="border:1px solid #4400ff;margin-top:10px" border="0" width="200" cellspacing="0" cellpadding="0" align="center">
                        <tbody>
                            <tr>
                                <td height="60">
                                    <p style="font-family:'Lato',Calibri,Arial,sans-serif;font-size:22px;color:#4400ff;text-align:center">
                                        <strong>
                                            {code_temp}
                                        </strong>
                                    </p>
                                </td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            """
            mail.send(msg)
            return redirect(url_for("verify_code_forgot_password", email=email, token=token_temp))
        else:
            return redirect(url_for("register"))
    else:
        return redirect(url_for("index"))


@app.route("/verify_code_forgot_password/<string:email>/<string:token>/", methods=['GET', 'POST'])
def verify_code_forgot_password(email, token):#verificar se codigo esta no cache e se esta dentro do tempo permitido, se não estiver lançar uma mensagem de errr dizendo que o codigo não existe ou expirou
    global cache_app_before_login
    if not current_user.is_authenticated:
        verified = False
        form = VerifyCodeForgotPasswordForm()
        if form.validate_on_submit():
            for x in range(len(cache_app_before_login)):
                print(email==cache_app_before_login[x][0]['email'])
                print(type(form.code.data))
                print(type(cache_app_before_login[x][1]))
                print(token==cache_app_before_login[x][2])
                if email == cache_app_before_login[x][0]['email'] and form.code.data == cache_app_before_login[x][1] and token == cache_app_before_login[x][2]: #verifica se o tken passado no link é o mesmo que foi gerado pelo sistema        
                    verified = True
                    break
            if verified:
                return redirect(url_for("change_password", email=email, token=token))
            else:
                return render_template('verify_code_forgot_password.html', form=form, email=email)
        else:
            return render_template('verify_code_forgot_password.html', form=form, email=email)
    else:
        return redirect(url_for("index"))


@app.route("/change_password/<string:email>/<string:token>/", methods=['GET', 'POST'])
def change_password(email, token):
    global cache_app_before_login
    if not current_user.is_authenticated:
        form = ChangePasswordForm()
        if form.validate_on_submit():
            for x in range(len(cache_app_before_login)):
                if email == cache_app_before_login[x][0]['email'] and token == cache_app_before_login[x][2]: #verifica se o token passado no link é o mesmo que foi gerado pelo sistema                    
                    new_password = form.new_password.data
                    user_recovery_password = User(cache_app_before_login[x][0]['name'], cache_app_before_login[x][0]['email'], new_password)
                    new_password = form.new_password.data
                    database.update('users', cache_app_before_login[x][0], user_recovery_password.get_as_json())
                    cache_app_before_login.pop(x)
                    break
            if True:
                return redirect(url_for("change_password", token=token))
            else:
                return render_template('verify_code_forgot_password.html', form=form, email=email)
        else:
            return render_template('change_password.html', form=form)
    else:
        return redirect(url_for("index"))

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

@app.route("/test/", methods=['GET', 'POST'])
def test():
    return render_template("advanced.html")
global aux
aux=1
@app.route("/test2/", methods=['GET', 'POST'])
def test2():
    res = request.form.getlist("form")
    print(res)
    return redirect(url_for("index"))
