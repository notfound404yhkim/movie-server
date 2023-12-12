from flask import request
from flask_jwt_extended import get_jwt_identity, jwt_required
from flask_restful import Resource
from mysql_connection import get_connection
from mysql.connector import Error

class MovieListResource(Resource):
    
    def get(self):
        #1 . 클라이언트로부터 데이터를 받아온다.
        # 없음.

        #2. db에 저장된 데이터를 가져온다.
        offset = request.args.get('offset')
        limit = request.args.get('limit')
        try:
            connection = get_connection()
            
            query = '''select m.title, avg(r.rating) as 'rating_avg',count(r.rating) as 'review_count'
                        from movie m
                        left join review r
                        on m.id = r.movieId
                        group by m.title
                        order by rating_avg desc, review_count desc
                        limit '''+ str(offset) +''', '''+ str(limit) +'''    ;'''

            cursor = connection.cursor(dictionary=True)
            cursor.execute(query)

            result_list = cursor.fetchall()  

            print(result_list)


            i = 0
            for row in result_list:
                result_list[i]['rating_avg'] = str(row['rating_avg'])
                i = i+1

            print()
            print(result_list)
            print()
                
            cursor.close()
            connection.close()

        except Error as e:
            print(e)
            cursor.close()
            connection.close()
            #클라이언트에게 에러를 보내줘야한다.
            return {"result" : "fail", "error" : str(e)},500
        


        return {"result " : "success",
                "itmems" : result_list,
                "count " : len(result_list)},200
    
class Movieinfo(Resource) :
    
    def get(self,movie_id) :
        
        try :
            connection = get_connection()

            query = '''select m.*,avg(r.rating) as 'rating_avg',count(r.rating) as 'review_count'
                        from movie m
                        left join review r
                        on m.id = r.movieId
                        where m.id = %s
                        group by m.title;'''
            record = (movie_id , )

            cursor = connection.cursor(dictionary=True)
            cursor.execute(query, record)

            result_list = cursor.fetchall()

            cursor.close()
            connection.close()

        except Error as e :
            print(e)
            cursor.close()
            connection.close()
            return {'error' : str(e)}, 500
        
        i = 0
        for row in result_list:
            result_list[i]['rating_avg'] = str(row['rating_avg'])
            result_list[i]['createdAt'] = row['createdAt'].isoformat()
            result_list[i]['year'] = row['year'].isoformat()
            i = i+1


        return {'result' : 'success',
                'items' : result_list,
                'count' : len(result_list)}