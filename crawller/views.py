from django.shortcuts import render

import urllib
import requests
from bs4 import BeautifulSoup
from idlelib import browser
from urllib.request import urlopen
import mechanicalsoup
from threading import Thread
import  time
import itertools
from django.contrib.auth.models import User, Group
from rest_framework import viewsets
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.views.generic import TemplateView
# Create your views here.
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.utils import json
from rest_framework import serializers
from rest_framework import viewsets

#from selenium.webdriver.chrome.service import Service

exploreLink=[]
links = []
formats=['jpg','exe','pdf','apk','mp4','mp3','jpeg','png','rar','aspx','sitemap','.Net']


def readRobots(url):

    try:
        data = urlopen(url+'/robots.txt')
    except Exception as e:
        print("Exepte to open robots",e)
        data=None
        pass

    robotLink =set()
    if data:
        for line in data:
            line=line.decode("utf-8")
            str_list=str(line).split(":")
            if str_list[0].lower() == "disallow":
                robotLink.add(url+str_list[1].strip().rstrip('/'))
    return robotLink

def siteMapCrawl(url,link):
    browser = mechanicalsoup.StatefulBrowser()
    browser.open(link)
    exploreLink.append(link)
    aTags=browser.links()
    for tag in aTags:
        href=tag['href']
        if href.startswith(url):
            if href[-1] == "/":
                href = href[:-1]
            if href not in exploreLink:
                exploreLink.append(href)
        if href.startswith('/'):
            href=str(url)+str(href)
            if href not in exploreLink:
                exploreLink.append(href)

def str_to_bool(s):
    if s == 'True' or s=='true':
         return True
    elif s == 'False' or s=='false':
         return False
    else:
         raise ValueError

def readFromSiteMap(url):
    r = requests.get(url + "/sitemap.xml")
    xml = r.text
    soup = BeautifulSoup(xml)
    sitemapTags = soup.find_all("sitemap")
    print(sitemapTags)
    if sitemapTags:
        t = True
        for sitemap in sitemapTags:
            loc = sitemap.findNext("loc").text
            loc = loc.replace('/sitemap', '')
            links.append(loc)
    else:
        t = False
    return t
@api_view(["POST"])
def crawl(request):
    data = request.data
    url = data["url"]
    robotLink = readRobots(url)
    t=False
    # t = readFromSiteMap(url)
    if not t:
        links.append(url)
    index = 0
    if robotLink and url in robotLink:
        robotLink.remove(url)

    if t:
        for link in links:
            siteMapCrawl(url, link)
    else:
        while links:
            link = links[0]
            index = index+1
            print("kodom linko daram expelore mikonm", link)
            try:
                if index % 100 == 0:
                    time.sleep(1)
                if link not in exploreLink and link not in robotLink:
                    getLinks(url, link)
                    links.remove(link)
            except Exception as e:
                links.remove(link)
                print("link", link)
                print("exeptions", e)
                continue
#        return render(request, 'crawl.html', {'links':exploreLink})
    return  Response(exploreLink)
def readRobotFromHtml(link):
    webpage = urlopen(str(link)).read()
    soup = BeautifulSoup(webpage, "lxml")
    robots = soup.find_all("meta")
    for robot in robots:
        if robot.get("name", None) == "robots":
            content = str(robot.get("content", None)).lower()
            if 'nofollow' in content:
                return False
        else:
            return True
    return True
def getLinks(url, link):
    browser = mechanicalsoup.StatefulBrowser()
    browser.open(link)
    allowToCrawl=readRobotFromHtml(link)
    exploreLink.append(link)
    if allowToCrawl:
        aTags = browser.links()
        if aTags:
            for tag in aTags:
                href = tag['href']
                href_part = str(href).split('.')
                if href_part[-1].lower() not in formats:
                    admision = True
                else:
                    admision = False
                if admision:
                    if href.startswith(url):
                        if href[-1] == "/":
                            href = href[:-1]
                        if href not in links:
                            if href not in exploreLink:
                                links.append(href)
                    if href.startswith('/'):
                        href = str(url)+str(href)
                        if href[-1] == "/":
                            href = href[:-1]
                        if href not in links:
                            if href not in exploreLink:
                                links.append(href)
    print("links should visit count", len(links))
    print("expelored count", len(exploreLink))

# @api_view(["POST"])
def form(request):
    url='http://lms.ui.ac.ir'
    webpage = urlopen(str(url)).read()
    soup = BeautifulSoup(webpage, "lxml")
    form = soup.find('form')

    browser = mechanicalsoup.StatefulBrowser()
    browser.open(url)
    fields = extract_form_fields(form)
    for key in fields:
        if key=='username':
            fields[key]='953611133039'
        if key=='password':
            fields[key]='1272508171'
    form = browser.select_form()
    form.set_input(fields)
    # form.choose_submit('submit')
    resp = browser.submit_selected()
    print(resp)
    url=browser.get_url()
    print(url)
    browser.launch_browser()
    print(browser.links())
    # fields = form.findAll('input')
    # formdata = dict((field.get('name'), field.get('value')) for field in fields)
    print(fields)
    return render(request,'form.html',{})
def extract_form_fields(soup):
    "Turn a BeautifulSoup form in to a dict of fields and default values"
    fields = {}
    for input in soup.findAll('input'):
        # ignore submit/image with no name attribute
        if input['type'] in ('submit', 'image') and not 'name' in input:
            continue

        # single element nome/value fields
        if input['type'] in ('text', 'hidden', 'password', 'submit', 'image'):
            value = ''
            if 'value' in input:
                value = input['value']
            fields[input['name']] = value
            continue

        # checkboxes and radios
        # if input['type'] in ('checkbox', 'radio'):
        #     value = ''
        #     if input.has_attr("checked"):
        #         if input.has_attr('value'):
        #             value = input['value']
        #         else:
        #             value = 'on'
        #     if 'name' in input and value:
        #         fields[input['name']] = value
        #
        #     if not 'name' in input:
        #         fields[input['name']] = value
        #
        #     continue
        #
        # assert False, 'input type %s not supported' % input['type']

    # # textareas
    # for textarea in soup.findAll('textarea'):
    #     fields[textarea['name']] = textarea.string or ''
    #
    # # select fields
    # for select in soup.findAll('select'):
    #     value = ''
    #     options = select.findAll('option')
    #     is_multiple = select.has_key('multiple')
    #     selected_options = [
    #         option for option in options
    #         if option.has_key('selected')
    #     ]
    #
    #     # If no select options, go with the first one
    #     if not selected_options and options:
    #         selected_options = [options[0]]
    #
    #     if not is_multiple:
    #         assert(len(selected_options) < 2)
    #         if len(selected_options) == 1:
    #             value = selected_options[0]['value']
    #     else:
    #         value = [option['value'] for option in selected_options]
    #
    #     fields[select['name']] = value

    return fields