from flask import request
from flask_jwt_extended import get_jwt_identity, jwt_required
from flask_restful import Resource
from mysql_connection import get_connection
from mysql.connector import Error

import pandas as pd


class MovieRecommendResource(Resource):
    
    @jwt_required()
    def get(self):
        
        user_id = get_jwt_identity()
        print(user_id)

        # 1. 영화별 상관 계수를 뽑아야 한다.
        # 1-1. DB에서 movie 테이블과 review 테이블의
        # 데이터를 가져와서, 데이터 프레임으로 만든다.


        try:
            connection = get_connection()
            query = ''' select m.id as movieId , m.title, r.userId, r.rating
                        from movie m
                        left join review r
                        on m.id = r.movieId;'''
            
            cursor = connection.cursor(dictionary=True)
            cursor.execute(query)
            
            result_list = cursor.fetchall()

            # 1-2. 데이터의 모양을, 상관계수를 계산할 수 있도록
            # pivot_table 해야한다.
            df = pd.DataFrame(result_list)
            
            print(df)
            df.pivot_table(index = 'userId', columns= 'title', values= 'rating', aggfunc='mean')

            # 1-3. corr() 함수를 이용해서 상관계수를 뽑는다.
            # corr_movie = df.corr(min_periods=50)
            corr_movie = df.corr(numeric_only=True,min_periods=50) #상관계수 만듬  (50개 이상인 데이터만 가지고)

            # 2. 이 유저의 별점 정보를 DB에서 가져온다.

            query = ''' select m.title,r.rating
                        from review r
                        join movie m
                        on r.movieId = m.id
                        where r.userId = %s;  '''
            
            record = (user_id , )
            cursor = connection.cursor(dictionary=True)
            cursor.execute(query,record)
            result_list = cursor.fetchall()
            print()
            print(result_list)
            print()

            cursor.close()
            connection.close()

        except Error as e:
            print(e)
            cursor.close()
            connection.close()
            return {'error' : str(e)},500

        # 3. 가중치로 계산하여 응답한다.
        #    이미 본 영화 및 중복 영화를 제거한다.

        my_rating = pd.DataFrame(result_list)
        movie_list = pd.DataFrame()
        for i in range(my_rating.shape[0]):
            title = my_rating['title'][i] 
            print(title)
            recom_movie = corr_movie[title].dropna().sort_values(ascending=False).to_frame()
            recom_movie.columns = ['corr']
            recom_movie['weight'] = recom_movie['corr']*my_rating['rating'][i]

            movie_list = pd.concat( [movie_list, recom_movie ]  )

        for title in my_rating['title']:
            if title in movie_list.index:
                movie_list.drop(title,axis = 0, inplace = True)
        
        movie_list.groupby('title')['weight'].max().sort_values(ascending=False).head(10)

        print()
        print(movie_list)
        print()


        return