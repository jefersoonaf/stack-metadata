#import flask app
from app import app 
#import dos metodos do flask
from flask import Flask, request, render_template, url_for, redirect
#import do objeto do banco de dados
from app import database
#import das coleções do banco de dados
from app.models.learning_object import LearningObject
from app.models.site import Site
#import do controller da api do stackexchange
from app.controllers.api_stackexchange import StackExchange
#outros imports
import json



descriptions = [
    {
        "is_answered": True,
        "view_count": 2490067,
        "accepted_answer_id": 231855,
        "answer_count": 38,
        "score": 11066,
        "creation_date": 1224800471,
        "question_id": 231767,
        "body_markdown": "What is the use of the `yield` keyword in Python, and what does it do?\r\n\r\nFor example, I&#39;m trying to understand this code&lt;sup&gt;**1**&lt;/sup&gt;:\r\n\r\n    def _get_child_candidates(self, distance, min_dist, max_dist):\r\n        if self._leftchild and distance - max_dist &lt; self._median:\r\n            yield self._leftchild\r\n        if self._rightchild and distance + max_dist &gt;= self._median:\r\n            yield self._rightchild\t\r\n\r\nAnd this is the caller:\r\n\r\n    result, candidates = [], [self]\r\n    while candidates:\r\n        node = candidates.pop()\r\n        distance = node._get_dist(obj)\r\n        if distance &lt;= max_dist and distance &gt;= min_dist:\r\n            result.extend(node._values)\r\n        candidates.extend(node._get_child_candidates(distance, min_dist, max_dist))\r\n    return result\r\n\r\nWhat happens when the method `_get_child_candidates` is called?\r\nIs a list returned? A single element? Is it called again? When will subsequent calls stop?\r\n\r\n\r\n----------\r\n\r\n\r\n&lt;sub&gt;\r\n1. This piece of code was written by Jochen Schulz (jrschulz), who made a great Python library for metric spaces. This is the link to the complete source: [Module mspace][1].&lt;/sub&gt;\r\n\r\n\r\n  [1]: http://well-adjusted.de/~jrschulz/mspace/",
        "link": "https://stackoverflow.com/questions/231767/what-does-the-yield-keyword-do",
        "title": "What does the &quot;yield&quot; keyword do?",
        "body": "<p>What is the use of the <code>yield</code> keyword in Python, and what does it do?</p>\n\n<p>For example, I'm trying to understand this code<sup><strong>1</strong></sup>:</p>\n\n<pre><code>def _get_child_candidates(self, distance, min_dist, max_dist):\n    if self._leftchild and distance - max_dist &lt; self._median:\n        yield self._leftchild\n    if self._rightchild and distance + max_dist &gt;= self._median:\n        yield self._rightchild  \n</code></pre>\n\n<p>And this is the caller:</p>\n\n<pre><code>result, candidates = [], [self]\nwhile candidates:\n    node = candidates.pop()\n    distance = node._get_dist(obj)\n    if distance &lt;= max_dist and distance &gt;= min_dist:\n        result.extend(node._values)\n    candidates.extend(node._get_child_candidates(distance, min_dist, max_dist))\nreturn result\n</code></pre>\n\n<p>What happens when the method <code>_get_child_candidates</code> is called?\nIs a list returned? A single element? Is it called again? When will subsequent calls stop?</p>\n\n<hr>\n\n<p><sub>\n1. This piece of code was written by Jochen Schulz (jrschulz), who made a great Python library for metric spaces. This is the link to the complete source: <a href=\"http://well-adjusted.de/~jrschulz/mspace/\" rel=\"noreferrer\">Module mspace</a>.</sub></p>\n"
    },
    {
        "is_answered": True,
        "view_count": 2490067,
        "accepted_answer_id": 231855,
        "answer_count": 38,
        "score": 11066,
        "creation_date": 1224800471,
        "question_id": 231767,
        "body_markdown": "What is the use of the `yield` keyword in Python, and what does it do?\r\n\r\nFor example, I&#39;m trying to understand this code&lt;sup&gt;**1**&lt;/sup&gt;:\r\n\r\n    def _get_child_candidates(self, distance, min_dist, max_dist):\r\n        if self._leftchild and distance - max_dist &lt; self._median:\r\n            yield self._leftchild\r\n        if self._rightchild and distance + max_dist &gt;= self._median:\r\n            yield self._rightchild\t\r\n\r\nAnd this is the caller:\r\n\r\n    result, candidates = [], [self]\r\n    while candidates:\r\n        node = candidates.pop()\r\n        distance = node._get_dist(obj)\r\n        if distance &lt;= max_dist and distance &gt;= min_dist:\r\n            result.extend(node._values)\r\n        candidates.extend(node._get_child_candidates(distance, min_dist, max_dist))\r\n    return result\r\n\r\nWhat happens when the method `_get_child_candidates` is called?\r\nIs a list returned? A single element? Is it called again? When will subsequent calls stop?\r\n\r\n\r\n----------\r\n\r\n\r\n&lt;sub&gt;\r\n1. This piece of code was written by Jochen Schulz (jrschulz), who made a great Python library for metric spaces. This is the link to the complete source: [Module mspace][1].&lt;/sub&gt;\r\n\r\n\r\n  [1]: http://well-adjusted.de/~jrschulz/mspace/",
        "link": "https://stackoverflow.com/questions/231767/what-does-the-yield-keyword-do",
        "title": "What does the &quot;yield&quot; keyword do?",
        "body": "<p>What is the use of the <code>yield</code> keyword in Python, and what does it do?</p>\n\n<p>For example, I'm trying to understand this code<sup><strong>1</strong></sup>:</p>\n\n<pre><code>def _get_child_candidates(self, distance, min_dist, max_dist):\n    if self._leftchild and distance - max_dist &lt; self._median:\n        yield self._leftchild\n    if self._rightchild and distance + max_dist &gt;= self._median:\n        yield self._rightchild  \n</code></pre>\n\n<p>And this is the caller:</p>\n\n<pre><code>result, candidates = [], [self]\nwhile candidates:\n    node = candidates.pop()\n    distance = node._get_dist(obj)\n    if distance &lt;= max_dist and distance &gt;= min_dist:\n        result.extend(node._values)\n    candidates.extend(node._get_child_candidates(distance, min_dist, max_dist))\nreturn result\n</code></pre>\n\n<p>What happens when the method <code>_get_child_candidates</code> is called?\nIs a list returned? A single element? Is it called again? When will subsequent calls stop?</p>\n\n<hr>\n\n<p><sub>\n1. This piece of code was written by Jochen Schulz (jrschulz), who made a great Python library for metric spaces. This is the link to the complete source: <a href=\"http://well-adjusted.de/~jrschulz/mspace/\" rel=\"noreferrer\">Module mspace</a>.</sub></p>\n"
    }
]

@app.route("/")
@app.route("/home/")
def home(): 
    return render_template("home.html", descriptions=descriptions)

@app.route("/index/")
def index():
    number_sites = len(database.list("sites"))
    return render_template("index.html", number_sites=number_sites)


#### sites ####

@app.route("/search_sites/", methods=['GET'])
def search_sites():
    sites_database = database.list("sites")
    """list_sites_database = []
    for site in sites_database:
        list_sites_database.append(site["site"]["api_parameter"])"""
    stackexchange = StackExchange()
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
def view_sites():
    sites = database.list("sites")
    list_sites = []
    for site in sites:
        list_sites.append(site["site"])
    return render_template("view_sites.html", sites=list_sites)


#### learning_object ####

@app.route("/search_api/")
def search_api():
    return render_template("search_api.html")


#### test ####

@app.route("/test/", methods=['GET'])
def test():
    return render_template("enhanced.html")

