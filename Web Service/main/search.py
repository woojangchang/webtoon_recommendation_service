import numpy as np
import pandas as pd
from scipy.sparse import hstack
from sklearn.metrics.pairwise import cosine_similarity
from tensorflow.keras.models import load_model
from PIL import Image as pil

encoder = load_model('data/models/encoder.h5')
latent_vector = pd.read_csv('data/latent_vector.csv', index_col=0)

web = pd.read_csv('data/all.csv', encoding='cp949')

okt_matrices = np.load('data/matrices/okt.npy',allow_pickle=True)
kkma_matrices = np.load('data/matrices/kkma.npy',allow_pickle=True)
hannanum_matrices = np.load('data/matrices/hannanum.npy',allow_pickle=True)
komoran_matrices = np.load('data/matrices/komoran.npy',allow_pickle=True)

def hstack_matrices(matrices, noauthor, w_author, w_genre):
    cnt_genre_matrix, lb_writer_matrix, lb_illustrator_matrix, tfidf_story_matrix = matrices

    sparse_matrix_list = [cnt_genre_matrix * w_genre, tfidf_story_matrix]
    if not noauthor:
        sparse_matrix_list.append(lb_writer_matrix * w_author)
        sparse_matrix_list.append(lb_illustrator_matrix * w_author)

    sparse_matrix_list = tuple(sparse_matrix_list)

    X_features_sparse = hstack(sparse_matrix_list).tocsr()
    return X_features_sparse

indices = web[['title', 'writer']]

tokenizer_matrices = [okt_matrices, kkma_matrices, hannanum_matrices, komoran_matrices]

def get_recomm(title, writer, rank=10, same_genre=False, noauthor=False,  w_author=0.7, w_genre=1.3, tokenizer_matrices=tokenizer_matrices):

    cosine_sim = np.zeros((len(web), len(web)))
    
    for matrices in tokenizer_matrices:
        X_features_sparse = hstack_matrices(matrices, noauthor=noauthor,  w_author=w_author, w_genre=w_genre)
        cosine_sim += cosine_similarity(X_features_sparse, X_features_sparse)
    cosine_sim /= len(tokenizer_matrices)
    
    print_copy = web.copy()
    idx = indices[(indices['title']==title)&(indices['writer']==writer)].index[0]
    
    genre = print_copy.loc[idx, 'genre']
    print_copy['similarity'] = cosine_sim[idx]
    
    if same_genre:
        return print_copy[print_copy['genre'] == genre].sort_values(by='similarity', ascending=False).iloc[1:1+rank, :]
        
    else:
        return print_copy.sort_values(by='similarity', ascending=False).iloc[1:1+rank, :]

def imageToNpArray(img, w=40, h=40, img_mode="RGB"):     

    img_resize = pil.open(img).resize((w,h), pil.ANTIALIAS).convert(mode=img_mode)
    img_unit8 = np.asarray(img_resize, dtype='uint8')
 
    X_raw = np.asarray(img_unit8)
    X_raw = X_raw.reshape((1, X_raw.shape[0], X_raw.shape[1], X_raw.shape[2]))
    X_raw = X_raw.astype('float32')/255.0     
    
    return  X_raw

def get_similar_image_wbt(img, latent_vector=latent_vector):
    X = imageToNpArray(img)
    pred = encoder.predict(X)
    
    latent_vector.loc['User'] = pred[0]
    cs = cosine_similarity(latent_vector.values)

    idx = list(latent_vector.index)

    cs_df = pd.DataFrame(cs, index=idx, columns=idx)

    user = cs_df['User'].sort_values(ascending=False)[1:11]
    
    return user

    