from flask import request
from flask_jwt_extended import get_jwt_identity, jwt_required
from flask_restful import Resource
from mysql_connection import get_connection
from mysql.connector import Error

class ReviewResource(Resource):
    
    @jwt_required()
    def post(self):

        data = request.get_json()
        user_id = get_jwt_identity()

        print(user_id)

        try : 
            connection = get_connection()

        # 2-2 쿼리문 만들기 - insert 쿼리 만들기
            query = '''

            insert into review
            (movieId,userId,rating,content)
            values(%s,%s,%s,%s);'''

        # 2-3 위의 쿼리에 매칭되는 변수를 처리해 준다.
        # 단, 라이브러리 특성상, 튜플로 만들어야 한다. 
            print(data)
            record = (data['movieID'], user_id,
                      data['rating'],data['content'] ) 

        # 2-4 커서를 가져온다.

            cursor = connection.cursor()
        
        # 2-5 위의 쿼리문을,커서로 실행한다.
            cursor.execute(query,record)  # 1. 쿼리, 2. 맵핑되는데이터

        # 2-6 커밋을 해주어야, db에 완전히 반영된다.

            connection.commit()

        # 2-7 자원을 반납한다. 
            cursor.close()
            connection.close()

        except Error as e:

            print(e)
            cursor.close()
            connection.close()
            # 유저에게 알려줘야 한다. -> respone해준다.
            return {"result" : "fail", "error" : str(e)},500  

        return {"result" : "success"},200
    
    # 특정 영화에 대한 리뷰 
    @jwt_required(optional= True)
    def get(self) :
        
        movieId = request.args.get('movieId')
        offset = request.args.get('offset')
        limit = request.args.get('limit')
        user_id = get_jwt_identity()

        try :
            connection = get_connection()

            query = '''select u.nickname, r.rating,r.content
                        from review r
                        join user u
                        on u.id = r.userId
                        where r.movieId = %s
                        order by r.updatedAt desc
                        limit '''+ str(offset) +''', '''+ str(limit) +'''    ;'''
            
            record = (movieId ,    )

            cursor = connection.cursor(dictionary=True)
            cursor.execute(query, record)

            result_list = cursor.fetchall()
            print(result_list)

            cursor.close()
            connection.close()

        except Error as e :
            print(e)
            cursor.close()
            connection.close()
            return {'error' : str(e)}, 500
        
        return {'result' : 'success',
                'items' : result_list,
                'count' : len(result_list)}