#import flask app
from app import app, mail
#import dos metodos do flask
from flask import Flask, request, render_template, url_for, redirect, flash, abort
#import do objeto do banco de dados
from app import database
#import das coleções do banco de dados
from app.models.collections.learning_object import LearningObject
from app.models.collections.site import Site
from app.models.collections.user import User
#import dos formulários
from app.models.forms import LoginForm, RegisterForm, ProfileForm, ForgotPasswordForm, VerifyCodeForgotPasswordForm, ChangePasswordForm
#import do contralador de seção do usuário e verificação de senha
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash
#import do controller da api do stackexchange
from app.controllers.api_stackexchange import StackExchange
#import message para envio do email
from flask_mail import Message
#import do gerador de hash base64
import secrets
#outros imports
import datetime
import pytz
import random

#### Limite diário de busca padrão na API para novos usuários ####
SEARCH_LIMIT = 20

#### limites de busca da API por request ####
PAGE_SIZE = 30
MAX_PAGES = 1

#### CACHE DA APLICAÇÃO ####

#Lista para gestão do cache antes do login do usuário
cache_app_before_login = []

#Lista para gestão do cache depois do login do usuário
cache_app_after_login = []

#### ROTAS DA APLICAÇÃO ####

#### Tela principal do sistema ####

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
    
    sites = database.list("sites")
    list_sites = []
    for site in sites:
        list_sites.append(site["site"])
        
    days_before = datetime.datetime.today()-datetime.timedelta(days=30)
    date_start = days_before.strftime("%d/%m/%Y")
    date_end = datetime.datetime.today().strftime("%d/%m/%Y")
        
    learning_objects = database.sort("learning_objects", -1, 10)
    list_learning_objects = []
    for learning_object in learning_objects:
        list_learning_objects.append(learning_object)
    return render_template("index.html", number_sites=number_sites, number_learning_objects=number_learning_objects, sites=list_sites, learning_objects=list_learning_objects, date_start=date_start, date_end=date_end)

#### Pesquisa e Atulização dos sites disponiveis para a busca na api ####

#Pesquisa/atualização de sites disponiveis para busca na api
@app.route("/search_sites/", methods=['GET'])
@login_required
def search_sites():
    if current_user.role != "administrator":
        flash('Acesso não permitido a rota especificada!', 'danger')
        return redirect(url_for("index"))
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

#Visualização dos sites
@app.route("/view_sites/", methods=['GET'])
@login_required
def view_sites():
    sites = database.list("sites")
    list_sites = []
    for site in sites:
        list_sites.append(site["site"])
    return render_template("view_sites.html", sites=list_sites)


#### Pesquisa e CRUD de objetos de aprendizagens ####

#Pesquisa de objetos de aprendizagens na api
@app.route("/search_api/", methods=['GET'])
@login_required
def search_api():
    sites = database.list("sites")
    list_sites = []
    for site in sites:
        list_sites.append(site["site"])
        
    days_before = datetime.datetime.today()-datetime.timedelta(days=30)
    date_start = days_before.strftime("%d/%m/%Y")
    date_end = datetime.datetime.today().strftime("%d/%m/%Y")
    
    return render_template("search_api.html", sites=list_sites, date_start=date_start, date_end=date_end)

#Apresenta os resultados da pesquisa na api
@app.route("/results_search_api/", methods=['POST'])
@login_required
def results_search_api():   
    global cache_app_after_login
    if current_user.search_limit <= 0 and current_user.role != "administrator":
        flash('Limite diário de buscas na API atingido! Novas buscas na API somente a partir de amanhã!', 'danger')
        return redirect(url_for("index")) 
    stackexchange = StackExchange(PAGE_SIZE, MAX_PAGES)
    sites = database.list("sites")
    list_sites_api = []
    list_results = []
    
    #pegar as datas
    try:
        date_start = datetime.datetime.strptime(request.form.get('date_start')[:10], "%d/%m/%Y").replace(tzinfo=pytz.utc).timestamp() #para pegar somente a data
        date_end = datetime.datetime.strptime(request.form.get('date_end')[:10], "%d/%m/%Y").replace(tzinfo=pytz.utc).timestamp() #para pegar somente a data
    except:
        date_start = datetime.datetime.strptime(request.form.get('date_start')[:10], "%m/%d/%Y").replace(tzinfo=pytz.utc).timestamp() #para pegar somente a data
        date_end = datetime.datetime.strptime(request.form.get('date_end')[:10], "%m/%d/%Y").replace(tzinfo=pytz.utc).timestamp() #para pegar somente a data
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
    
    if selected_sites:
        for option in selected_sites:
            option = option.split("-")[1]
            for site in sites:
                if option == site["site"]["api_parameter"]:
                    list_sites_api.append(site["site"])
                    break
    else:
        for site in sites:
            list_sites_api.append(site["site"])
        
    for site in list_sites_api:
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
            cache_user[1] = list_results
            cache_user[2] = list_sites_api
            cache_user[3] = update_results
            cache_app_after_login[x] = cache_user
            break        
    if not cache_user:        
        cache_user.append(current_user.email)
        cache_user.append(list_results)
        cache_user.append(list_sites_api)
        cache_user.append(update_results)
        cache_app_after_login.append(cache_user)
     
    #controle do limite de pesquisas diárias na API
    if(current_user.role == "standard"):
        current_user.search_limit -= 1
        database.update("users", database.filter_by('users', {"email": current_user.email})[0], current_user.get_as_json())
    
    
    return render_template("results_search_api.html", list_results=cache_user[1], list_sites_api=cache_user[2], update_results=cache_user[3])

#Cria um novo objeto de aprendizagem a partir da pesquisa retornada na api
@app.route("/create_learning_object/<int:index_list_results>/<int:index_result>/<string:name_site>/<string:api_site>")
@login_required
def create_learning_object(index_list_results, index_result, name_site, api_site):
    list_results = []
    list_sites_api = []
    update_results = []
    cache_user = []
    global cache_app_after_login
    index_user = None
    for x in range(len(cache_app_after_login)):
        if current_user.email == cache_app_after_login[x][0]:              
            cache_user = cache_app_after_login[x]
            index_user = x
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
        database.create("learning_objects", learning_object)
        update_results[index_list_results][index_result] = 1
        cache_user[3] = update_results
        cache_app_after_login[index_user] = cache_user
        return render_template("results_search_api.html", list_results=list_results, list_sites_api=list_sites_api, update_results=update_results)
    else:
        database.update("learning_objects", item_db[0])
        return render_template("results_search_api.html", list_results=list_results, list_sites_api=list_sites_api, update_results=update_results)

#Pesquisa de objetos de aprendizagens no banco de dados
@app.route("/search_database/")
@login_required
def search_database():
    sites = database.list("sites")
    list_sites = []
    for site in sites:
        list_sites.append(site["site"])
    return render_template("search_database.html", sites=list_sites)

#Apresenta os resultados da pesquisa no banco de dados
@app.route("/results_search_database/", methods=['POST'])
@login_required
def results_search_database():
    global cache_app_after_login
    sites = database.list("sites")
    list_foruns = []
    list_results = []
    
    #pegar as datas
    try:
        date_start = datetime.datetime.strptime(request.form.get('date_start')[:10], "%d/%m/%Y").replace(tzinfo=pytz.utc).timestamp() #para pegar somente a data
        date_end = datetime.datetime.strptime(request.form.get('date_end')[:10], "%d/%m/%Y").replace(tzinfo=pytz.utc).timestamp() #para pegar somente a data
    except:
        date_start = datetime.datetime.strptime(request.form.get('date_start')[:10], "%m/%d/%Y").replace(tzinfo=pytz.utc).timestamp() #para pegar somente a data
        date_end = datetime.datetime.strptime(request.form.get('date_end')[:10], "%m/%d/%Y").replace(tzinfo=pytz.utc).timestamp() #para pegar somente a data
    #pegar o tipo ordenação
    selected_order = request.form.get('selected-order')
    #pegar os sites
    selected_sites = request.form.getlist('selected-sites')
    #pegar o tipo da busca
    selected_type_search = request.form.getlist('selected-type-search') 
    #pegar a busca
    search = request.form.get('search')
    
    if selected_sites:
        for option in selected_sites:
            option = option.split("-")[1]
            for site in sites:
                if option == site["site"]["api_parameter"]:
                    list_foruns.append(site["site"])
                    break
    else:
        for site in sites:
            list_foruns.append(site["site"])
        
    for site in list_foruns:
        list_result_items = database.search_advanced("learning_objects", str(search), str(site["api_parameter"]), date_start, date_end, selected_order, selected_type_search[0])
        list_results.append(list_result_items)
    
    cache_user = []
    for x in range(len(cache_app_after_login)):
        if current_user.email == cache_app_after_login[x][0]:              
            cache_user = cache_app_after_login[x]
            break        
    if cache_user:
        cache_user[4] = list_results
        cache_user[5] = list_foruns
    else:
        cache_user.append(current_user.email)
        cache_user.append(None)
        cache_user.append(None)
        cache_user.append(None)
        cache_user.append(list_results)
        cache_user.append(list_foruns)
        cache_app_after_login.append(cache_user)

    return render_template("results_search_database.html", list_results=cache_user[4], list_foruns=cache_user[5])


#Visualiza os objetos de aprendizagens que estão no banco de dados
@app.route("/view_learning_objects/")
@login_required
def view_learning_objects():
    learning_objects = database.list("learning_objects")
    list_learning_objects = []
    for learning_object in learning_objects:
        list_learning_objects.append(learning_object)
    return render_template("view_learning_objects.html", learning_objects=list_learning_objects)

#Visualiza o objeto de aprendizagem
@app.route("/view_learning_object/<string:id_learning_object_0>/<int:id_learning_object_1>", methods=['GET', 'POST'])
@login_required
def view_learning_object(id_learning_object_0, id_learning_object_1):
    learning_object = database.filter_by('learning_objects', {"general.identifier": id_learning_object_0,"general.identifier": id_learning_object_1})
    return render_template("view_learning_object.html", learning_object=learning_object[0])

#Edita o objeto de aprendizagem
@app.route("/edit_learning_object/<string:id_learning_object_0>/<int:id_learning_object_1>", methods=['GET', 'POST'])
@login_required
def edit_learning_object(id_learning_object_0, id_learning_object_1):
    learning_object = database.filter_by('learning_objects', {"general.identifier": id_learning_object_0,"general.identifier": id_learning_object_1})
    return render_template("edit_learning_object.html", learning_object=learning_object[0])

#Atualiza o objeto de aprendizagem que foi editado
@app.route("/update_learning_object/<string:id_learning_object_0>/<int:id_learning_object_1>", methods=['GET', 'POST'])
@login_required
def update_learning_object(id_learning_object_0, id_learning_object_1):
    save_edit_learning_object = request.get_json()
    if save_edit_learning_object:
        learning_object_db = database.filter_by('learning_objects', {"general.identifier": id_learning_object_0,"general.identifier": id_learning_object_1})
        database.update("learning_objects", learning_object_db[0], save_edit_learning_object)
        #print('\n',json.dumps(save_edit_learning_object, indent=2),'\n')
    return redirect(url_for("view_learning_objects"))

#Deleta o objeto de aprendizagem
@app.route("/delete_learning_object/<string:id_learning_object_0>/<int:id_learning_object_1>")
@login_required
def delete_learning_object(id_learning_object_0, id_learning_object_1):
    learning_object_db = database.filter_by('learning_objects', {"general.identifier": id_learning_object_0,"general.identifier": id_learning_object_1})
    database.delete("learning_objects", learning_object_db[0])
    return redirect(url_for("view_learning_objects"))


#### Login, Registro, Perfil, Logout e Recuperação de senha ####

#Visualiza todos os usuários cadastrados
@app.route("/view_users/")
@login_required
def view_users():
    if current_user.role != "administrator":
        flash('Acesso negado!', 'danger')
        return redirect(url_for("index"))
     
    users = database.list("users")
    return render_template("view_users.html", users=users)

#Visualiza todos os usuários cadastrados
@app.route("/request_admin_access/")
@login_required
def request_admin_access():
    msg = Message('Solicitação de acesso como administrador!')
    msg.html = f"""  
            <div width="100%" style="margin:0;padding:0!important">
                <center style="width:100%;>
                    <div style="max-width:600px;margin:0 auto" class="m_-2585479850499807075email-container">
                        <table width="100%" cellspacing="0" cellpadding="0" border="0" align="center">
                            <tbody>
                                <tr>
                                    <td height="20"></td>
                                </tr>
                                <tr>
                                    <td align="center">
                                        <p style="line-height:1.5;font-family:'Lato',Calibri,Arial,sans-serif;font-size:18px;color:#000000;text-align:center;text-decoration:none"> 
                                            O usuário abaixo solicitou acesso como administrador:
                                        </p>
                                    </td>
                                </tr>
                            </tbody>
                        </table>
                        <table style="border:1px solid #9400D3;margin-top:10px" border="0" width="200" cellspacing="0" cellpadding="0" align="center">
                            <tbody>
                                <tr>
                                    <td height="60">
                                        <p style="font-family:'Lato',Calibri,Arial,sans-serif;font-size:22px;color:#9400D3;text-align:center">
                                            <strong>
                                                {current_user.email}
                                            </strong>
                                        </p>
                                    </td>
                                </tr>
                            </tbody>
                        </table>
                        <table width="100%" cellspacing="0" cellpadding="0" border="0" align="center">
                            <tbody>
                                <tr>
                                    <td height="20"></td>
                                </tr>
                            </tbody>
                        </table>
                    </div>
                </center>
                <div class="yj6qo"></div>
                <div class="adL"></div>
            </div>
        """        
    
    error = 0
    success = 0
    
    users = database.filter_by("users", {"role": "administrator"})
    for user in users:    
        print(user)
        #envio do email com o código
        msg.recipients = [user['email']]        
        try:                    
            mail.send(msg)
            success += 1
        except:
            error += 1
    
    if error > 0:
        flash(f"Ocorreu um problema ao tentar enviar a solicitação para os administradores! {success} emails foram enviados e {error} não foram enviados", 'info')
    else:
        flash('Solicitação enviada para todos os administradores!', 'primary')
                                
    return redirect(url_for("profile"))

#Libera o acesso de administrator
@app.route("/release_admin_access/<string:email>/")
@login_required
def release_admin_access(email):
    if current_user.role != "administrator":
        flash('Acesso negado!', 'danger')
        return redirect(url_for("index"))
     
    user_bd = database.filter_by("users", {"email": email})
    if user_bd:
        user_aux = user_bd[0]
        user_aux['role'] = "administrator"
        user_aux['search_limit'] = 99999
        
        database.update("users", user_bd[0], user_aux)
        
        flash('Usuário liberado para acesso como administrador!', 'success')
    
    flash('Ocorrreu um problema ao tentar liberar o usuário para acesso como administrador!', 'danger')
    
    users = database.list("users")
    return render_template("view_users.html", users=users)

#Remove o acesso de administrator
@app.route("/remove_admin_access/<string:email>/")
@login_required
def remove_admin_access(email):
    if current_user.role != "administrator":
        flash('Acesso negado!', 'danger')
        return redirect(url_for("index"))

    user_bd = database.filter_by("users", {"email": email})
    if user_bd:
        user_aux = user_bd[0]
        user_aux['role'] = "standard"
        user_aux['search_limit'] = 20
        
        database.update("users", user_bd[0], user_aux)
        
        flash('Acesso como administrador removido do usuário!', 'success')
    
    flash('Ocorrreu um problema ao tentar remover o acesso como administrador do usuário !', 'danger')
    
    users = database.list("users")
    return render_template("view_users.html", users=users)

#Deleta o usuário
@app.route("/delete_user/<string:email>/")
@login_required
def delete_user(email):
    if current_user.role != "administrator":
        flash('Acesso negado!', 'danger')
        return redirect(url_for("index"))
    
    user_bd = database.filter_by("users", {"email": email})
    if user_bd:
        database.delete("users", user_bd[0])
        
    users = database.list("users")
    
    flash('Usuário deletado com sucesso!', 'success')
    
    return render_template("view_users.html", users=users)

#Registro de conta
@app.route("/register/", methods=['GET', 'POST'])
def register():
    if not current_user.is_authenticated:
        form = RegisterForm()
        if form.validate_on_submit():
            name = form.name.data
            email = form.email.data
            password = form.password.data
            confirm_password = form.confirm_password.data
            query = database.filter_by('users', {"email": email})
            if not query:
                if password == confirm_password:
                    user = User(name, email, password, "standard", SEARCH_LIMIT)
                    database.create("users", user)
                    flash('Conta registrada com sucesso!', 'success')
                    return redirect(url_for("login"))
                else:
                    flash('A senha de confirmação está incorreta!', 'danger')
                    return render_template('register.html', form=form)
            else:
                flash('Email já cadastrado!', 'danger')
                return render_template('register.html', form=form)
        return render_template('register.html', form=form)
    else:
        flash('Você já está logado no sistema!', 'info')
        return redirect(url_for("index"))

#Login - Entrar no sistema
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
                    user = User(user_bd['name'], user_bd['email'], user_bd['password'], user_bd['role'], user_bd['search_limit'])
                    login_user(user, remember=remember)
                    return redirect(url_for("index"))
                else:
                    flash('Ocorreu um erro ao tentar fazer login. Por favor verifique sua senha!', 'danger')
                    return redirect(url_for("login"))  
            else:
                flash('Ocorreu um erro ao tentar fazer login. Email não registrado!', 'danger')
                return redirect(url_for("login")) 
        else:                
            return render_template('login.html', form=form)
    else:
        flash('Você já está logado no sistema!', 'info')
        return redirect(url_for("index"))

#Logout - Sair do sistema
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

#Perfil do usuário
@app.route("/profile/", methods=['GET', 'POST'])
@login_required
def profile():
    form = ProfileForm()
    if form.validate_on_submit():
        name = form.name.data
        current_password = form.current_password.data
        new_password = form.new_password.data
        confirm_new_password = form.confirm_new_password.data
        #busca dados do usuário no banco
        query = database.filter_by('users', {"email": current_user.email})
        if query:
            user_bd = query[0]
            #verificar se a senha atual é igual a sanha no banco de dados
            if check_password_hash(user_bd['password'], current_password):       
                if new_password == confirm_new_password:
                    user_temp = User(name, current_user.email, new_password, current_user.role, current_user.search_limit)
                    database.update("users", user_bd, user_temp.get_as_json())
                    form.name.data = name
                    flash('Dados do perfil alterados com sucesso!', 'success')
                    return render_template('profile.html', form=form)
                else:
                    flash('A confirmação de senha está incorreta!', 'danger')                    
                    return render_template('profile.html', form=form)
            else:
                flash('A senha atual informada está incorreta!', 'danger')                        
                return render_template('profile.html', form=form)
        else:
            abort(500)
    else:
        form.name.data = current_user.name
        return render_template('profile.html', form=form)

#Recuperação de senha
@app.route("/forgot_password/", methods=['GET', 'POST'])
def forgot_password():
    if not current_user.is_authenticated:
        global cache_app_before_login
        form = ForgotPasswordForm()
        if form.validate_on_submit():
            query = database.filter_by('users', {"email": form.email.data})
            if query:
                user_bd = query[0] 
                
                #gera codigo temporário para recuperar a senha
                number = range(0, 9)
                code_temp = ''
                for i in range(6):
                    code_temp += str(random.choice(number))
                
                #gerando hash de segurança do link de recuperação
                token_temp = secrets.token_hex(64)
                
                #gera validade do codigo e do token
                validate_temp = int(datetime.datetime.now().replace(tzinfo=pytz.utc).timestamp()+3600) #soma 3600 segundos ao tempo de validade para ser valido por 1 hora
                        
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
                    cache_user_temp[3] = int(validate_temp)
                else:
                    cache_user_temp.append(user_bd)
                    cache_user_temp.append(int(code_temp))
                    cache_user_temp.append(str(token_temp))
                    cache_user_temp.append(int(validate_temp))
                    cache_app_before_login.append(cache_user_temp)
                
                #envio do email com o código
                msg = Message(
                    'Código para recuperação de senha!',
                    recipients=[form.email.data],
                )
                msg.html = f"""  
                    <div width="100%" style="margin:0;padding:0!important">
                        <center style="width:100%;>
                            <div style="max-width:600px;margin:0 auto" class="m_-2585479850499807075email-container">
                                <table width="100%" cellspacing="0" cellpadding="0" border="0" align="center">
                                    <tbody>
                                        <tr>
                                            <td height="20"></td>
                                        </tr>
                                        <tr>
                                            <td align="center">
                                                <p style="line-height:1.5;font-family:'Lato',Calibri,Arial,sans-serif;font-size:18px;color:#000000;text-align:center;text-decoration:none"> 
                                                    Para recuperar a seu acesso use o código abaixo:
                                                </p>
                                            </td>
                                        </tr>
                                    </tbody>
                                </table>
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
                                <table width="100%" cellspacing="0" cellpadding="0" border="0" align="center">
                                    <tbody>
                                        <tr>
                                            <td height="20"></td>
                                        </tr>
                                        <tr>
                                            <td align="center">
                                                <p style="line-height:1.5;font-family:'Lato',Calibri,Arial,sans-serif;font-size:12px;color:#000000;text-align:center;text-decoration:none"> 
                                                    Este código é válido por 1 hora.
                                                </p>
                                            </td>
                                        </tr>
                                    </tbody>
                                </table>
                            </div>
                        </center>
                        <div class="yj6qo"></div>
                        <div class="adL"></div>
                    </div>
                """
                try:                    
                    mail.send(msg)
                    flash('Código enviado no email informado!', 'primary')            
                    return redirect(url_for("verify_code_forgot_password", token=token_temp))
                except:
                    flash('Ocorreu um problema ao tentar enviar o código, por favor tente novamente!', 'danger')                                
                    return redirect(url_for("forgot_password"))                    
            else:
                flash('Resgistro não encontrado, por favor realize seu registro no sistema!', 'warning')
                return redirect(url_for("register"))
        else:
            return render_template('forgot_password.html', form=form)
    else:
        flash('Você já está logado no sistema!', 'info')
        return redirect(url_for("index"))
    
#Verifica código enviado da recuperação de senha
@app.route("/verify_code_forgot_password/<string:token>/", methods=['GET', 'POST'])
def verify_code_forgot_password(token):#verificar se codigo esta no cache e se esta dentro do tempo permitido, se não estiver lançar uma mensagem de errr dizendo que o codigo não existe ou expirou
    if not current_user.is_authenticated:
        global cache_app_before_login
        #verificando token e validade dele
        date_now = int(datetime.datetime.now().replace(tzinfo=pytz.utc).timestamp())
        for x in range(len(cache_app_before_login)):
            if token == cache_app_before_login[x][2]:
                if date_now < cache_app_before_login[x][3]: #verifica se o token passado no link é o mesmo que foi gerado pelo sistema e ainda está válido  
                    form = VerifyCodeForgotPasswordForm()
                    if form.validate_on_submit():
                        if form.code.data == cache_app_before_login[x][1]: #verifica se o codigo digitado é válido                                     
                            token_verification_code = f"{token[:50]}{form.code.data}{token[50:]}" #concatena o token com o codigo enviado
                            flash('Código verificado com sucesso!', 'success')
                            return redirect(url_for("change_password", token_verification_code=token_verification_code))
                        else:
                            flash('O código informado está incorreto!', 'danger')                    
                            return render_template('verify_code_forgot_password.html', form=form)
                    else:
                        return render_template('verify_code_forgot_password.html', form=form)                    
                else:
                    flash('Token expirou! Reenvie outro código para recuperar sua senha!', 'warning')
                    abort(404)
        #caso não encontre o token no cache                    
        flash('Token inválido! Reenvie outro código para recuperar sua senha!', 'danger')                                    
        abort(404)
    else:
        flash('Você já está logado no sistema!', 'info')
        return redirect(url_for("index"))

#Alteração de senha após as validações anteriores da recuperação de senha
@app.route("/change_password/<string:token_verification_code>/", methods=['GET', 'POST'])
def change_password(token_verification_code):
    if not current_user.is_authenticated:
        global cache_app_before_logi       
        verification_code = int(token_verification_code[50:56])
        token = f"{token_verification_code[:50]}{token_verification_code[56:]}"
        date_now = int(datetime.datetime.now().replace(tzinfo=pytz.utc).timestamp())
        for x in range(len(cache_app_before_login)):
            if verification_code == cache_app_before_login[x][1] and token == cache_app_before_login[x][2]:
                if date_now < cache_app_before_login[x][3]: #verifica se o token passado no link é o mesmo que foi gerado pelo sistema e ainda está válido  
                    form = ChangePasswordForm()
                    if form.validate_on_submit():    
                        new_password = form.new_password.data
                        confirm_new_password = form.confirm_new_password.data   
                        if new_password == confirm_new_password: #verifica se a senha está realmente correta                   
                            user_recovery_password = User(cache_app_before_login[x][0]['name'], cache_app_before_login[x][0]['email'], new_password, cache_app_before_login[x][0]['role'], cache_app_before_login[x][0]['search_limit']) #gera um novo objeto de usuario para atualizar no banco
                            database.update('users', cache_app_before_login[x][0], user_recovery_password.get_as_json())
                            cache_app_before_login.pop(x) #limpa o cache_app_before_login                            
                            flash('Senha alterar com sucesso!', 'success')                                                        
                            return redirect(url_for("login"))
                        else:
                            flash('A confirmação de senha está incorreta!', 'danger')                                                                            
                            return render_template('change_password.html', form=form)
                    else:
                        return render_template('change_password.html', form=form)
                else:
                    flash('Token expirou! Reenvie outro código para recuperar sua senha!', 'warning')
                    abort(404)
        #caso não encontre o token no cache
        flash('Token inválido! Reenvie outro código para recuperar sua senha!', 'danger')
        abort(404)
    else:
        flash('Você já está logado no sistema!', 'info')        
        return redirect(url_for("index"))


#### Tratamento de exceções das rotas ####

@app.errorhandler(404)
def errorPage(e):
    return render_template('404.html', e=e)
    
#Erro para quando tentar acessar uma rota que necessita de login
@app.errorhandler(401)
def page_not_found(e):
    flash('Faça login primeiro!', 'danger')
    return redirect(url_for("login"))

@app.errorhandler(500)
def errorPage(e):
    return render_template('500.html', e=e)


#### Rotas de teste ####

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
