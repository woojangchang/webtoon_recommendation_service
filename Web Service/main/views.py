from django.shortcuts import render
import pandas as pd
from .models import *
from .search import *
import json
from django.http.response import HttpResponseRedirect
from django.urls import reverse
from django.http.response import HttpResponse
from django.core.paginator import Paginator

cs = pd.read_csv('data/cosine_similarity.csv', index_col=0)
illustrators = list(cs.columns.sort_values())
j_ill = json.dumps(illustrators)

# thumb = pd.read_csv('data/naverurl.csv')
# webtoons = pd.read_csv('data/webtoon.csv', encoding='cp949', index_col=0)
# thumb = pd.merge(thumb, webtoons, on='title', how='outer')
thumb = pd.read_csv('data/all.csv', encoding='cp949')

tls = list(thumb['title'].values + ';' + thumb['writer'].values)
# tls = list(thumb['title'].values + ';' + thumb['writer'].values)
j_tls = json.dumps(tls)

# Create your views here.
def index(req):
    context = {

    }
    
    return render(req, 'index.html', context=context)


def input(req):
    page = req.GET.get('page', '1')
    try:
        img = req.FILES['fileInput']
        img = img.file
        cs_df = get_similar_image_wbt(img)

        top10value = list(cs_df.values * 100)
        top10illustrator = list(cs_df.index.to_numpy())

        infos = []
        for ill in top10illustrator:
            df2 = thumb[thumb['illustrator']==ill]
            link = list(df2['url'].values)
            thumbnail = list(df2['thumb'].values)
            title = list(df2['title'].values)

            info = [(l, th, ti) for l, th, ti in zip(link, thumbnail, title)]
            infos.append(info)


        top10 = list(zip(top10value, top10illustrator, infos))
        paginator = Paginator(top10, 10)
        page_obj = paginator.get_page(page)
        context = {
            'top10': top10,
        }

        
    except:
        context={'response':''}
        pass
    
    return render(req, 'input.html', context=context)

# import random

def search_main(req):
    context = {'response':'그림 작가를 검색하세요.', 'illustrators':j_ill}
    
    return render(req, 'search.html', context=context)

def search_searching(req):
    illustrator = req.POST.get('searchInput', False)
    return HttpResponseRedirect(reverse('search', kwargs={'illustrator':illustrator}))

def search(req, illustrator):
    # 입력 파라미터
    page = req.GET.get('page', '1')  # 페이지

    if illustrator in illustrators:
        df = cs.copy()
        
        df = df[illustrator].sort_values(ascending=False)[1:]

        df2 = thumb[thumb['illustrator']==illustrator]
        link0 = list(df2['url'].values)
        thumbnail0 = list(df2['thumb'].values)
        title0 = list(df2['title'].values)
        platform0 = list(df2['platform'].values)
        info0 = zip(link0, thumbnail0, title0, platform0)

        top10value = list(df.values * 100)
        top10illustrator = list(df.index.to_numpy())

        infos = []
        for ill in top10illustrator:
            df2 = thumb[thumb['illustrator']==ill]
            link = list(df2['url'].values)
            thumbnail = list(df2['thumb'].values)
            title = list(df2['title'].values)
            platform = list(df2['platform'].values)

            info = [(l, th, ti, pf) for l, th, ti, pf in zip(link, thumbnail, title, platform)]
            infos.append(info)

        top10 = list(zip(top10value, top10illustrator, infos))
        paginator = Paginator(top10, 10)
        page_obj = paginator.get_page(page)

        context = {
            'info':info0,
            'illustrator':illustrator,
            # 'top10': top10,
            'top10':page_obj,
            'illustrators':j_ill,
        }

    else:
        context = {'response':'없는 작가 명입니다.', 'illustrators':j_ill}
    
    return render(req, 'search.html', context=context)

def story_main(req):
    context = {'response':'작품을 검색하세요.', 'titles':j_tls}
    
    return render(req, 'story.html', context=context)

def story_searching(req):
    try:
        title = req.POST.get('searchInput', False)
        w_genre = req.POST.get('wgenre', False)
        w_author = req.POST.get('wauthor', False)
        if isinstance(w_genre, int):
            w_genre = float(w_genre)
        
        if isinstance(w_author, int):
            w_author = float(w_author)

        return HttpResponseRedirect(reverse('story', kwargs={'title':title, 'wgenre':w_genre, 'wauthor':w_author}))
    except:
        return HttpResponseRedirect(reverse('story_main'))


def story(req, title, wgenre, wauthor):
    # tw = req.POST.get('searchInput')
    page = req.GET.get('page', '1')  # 페이지
    
    # if not tw:
    #     tw = random.choice(tls)
    tw = title
    try:
        writer = title.split(';')[1]
        title = title.split(';')[0]
    except:
        context = {'response':'없는 작품 명입니다.', 'titles':j_tls}
        return render(req, 'story.html', context=context)
    
    
    if tw in tls:
        df = get_recomm(title, writer, rank=len(thumb)-1, w_genre=wgenre, w_author=wauthor)
        df = df.drop_duplicates(subset=['title', 'writer'])
        df = df[(df['title']!=title)&df['writer']!=writer]
        df2 = thumb[(thumb['title']==title) & (thumb['writer']==writer)]
        link0 = list(df2['url'].values)[:1]
        thumbnail0 = list(df2['thumb'].values)[:1]
        writer0 = list(df2['writer'].values)[:1]
        story0 = list(df2['story'].values)[:1]
        platform0 = list(df2['platform'].values)[:1]
        info0 = zip(link0, thumbnail0, writer0, story0, platform0)
        

        top10value = list(df['similarity'].values * 100)
        top10title = list(df.title.to_numpy())
        top10author = list(df.writer.to_numpy())

        infos = []
        for tl, ta in zip(top10title, top10author):
            df2 = thumb[(thumb['title']==tl) & (thumb['writer']==ta)]
            link = list(df2['url'].values)[:1]
            thumbnail = list(df2['thumb'].values)[:1]
            writer = list(df2['writer'].values)[:1]
            story = list(df2['story'].values)[:1]
            platform = list(df2['platform'].values)[:1]

            info = [(l, th, wr, st, pl) for l, th, wr, st, pl in zip(link, thumbnail, writer, story, platform)]
            infos.append(info)

        top10 = list(zip(top10value, top10title, infos))
        paginator = Paginator(top10, 10)
        page_obj = paginator.get_page(page)

        context = {
            'info':info0,
            'title':title,
            'story':story,
            # 'top10': top10,
            'top10' : page_obj,
            'titles':j_tls,
            'wgenre':wgenre,
            'wauthor':wauthor
        }
    else:
        context = {'response':'없는 작품 명입니다.', 'titles':j_tls}
    
    return render(req, 'story.html', context=context)
    
import os

def download(req):
    file_path = 'data/models/encoder.h5'

    binary_file = open(file_path, 'rb')
    response = HttpResponse(binary_file.read(), content_type="application/liquid; charset=utf-8")
    response['Content-Disposition'] = 'attachment; filename=' + os.path.basename(file_path)
    return response

def help(req):
    context = {

    }
    return render(req, 'help.html', context=context)