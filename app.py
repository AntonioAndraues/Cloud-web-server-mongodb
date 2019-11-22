from flask import Flask
from flask_restful import reqparse, abort, Api, Resource
import functools
from pymongo import MongoClient
import sys

    
app = Flask(__name__)
api = Api(app)

client = MongoClient(sys.argv[1], int(sys.argv[2]))
db = client.tarefas
db = client['tarefas']
posts = db.posts
Tarefas={ 
}

def tarefa_nao_existe(tarefa_id):
    if tarefa_id not in Tarefas:
        if("tarefa"+tarefa_id in Tarefas):
            return "tarefa"+tarefa_id 
        abort(404, message="Tarefa {} não existe".format(tarefa_id))
def atualiza_tarefas():
    for x in posts.find():
        try:
            Tarefas[x['_id']]=  {'tarefa': x['tarefa'], 'ativo': x['ativo']}
        except Excepition as e:
            print(str(e))
        

class Tarefa(Resource):
    def get(self, tarefa_id):
        atualiza_tarefas()
        tarefa_id=tarefa_nao_existe(tarefa_id)
        if(Tarefas[tarefa_id]["ativo"]=="1"):
            return {"tarefa":Tarefas[tarefa_id]["tarefa"]}
        else:
            abort(404, message="{} está inativa".format(tarefa_id))

    def delete(self, tarefa_id):
        atualiza_tarefas()
        tarefa_id=tarefa_nao_existe(tarefa_id)
        try:
            myquery = { "_id": tarefa_id, "ativo": "1" }
            newvalues = { "$set": { "_id": tarefa_id, "ativo": "0" } }
            posts.update_one(myquery, newvalues)
            Tarefas[tarefa_id]={"tarefa":Tarefas[tarefa_id]["tarefa"],"ativo":'0'}
            return 'tarefa deletada', 204
        except Exception as e:
            return f'ERRO: {str(e)}', 400 
        
        

    def put(self, tarefa_id):
        atualiza_tarefas()
        tarefa_id=tarefa_nao_existe(tarefa_id)
        args = parser.parse_args()
        tarefa = {'tarefa': args['tarefa'], 'ativo': '1'}
        try:
            myquery = { "_id": tarefa_id}
            newvalues = { "$set": { "tarefa":args['tarefa'],"ativo": "1" } }
            posts.update_one(myquery, newvalues)
            Tarefas[tarefa_id] = tarefa
            return tarefa, 201
        except Exception as e:
           return f'ERRO: {str(e)}', 400
        



class ListaTarefas(Resource):
    def get(self, tarefa=None):
        atualiza_tarefas()
        Tarefas_ativas=[Tarefas[tarefa_ativa] for tarefa_ativa in Tarefas if Tarefas[tarefa_ativa]["ativo"]!="0"]
        return Tarefas_ativas

    def post(self,tarefa):
        atualiza_tarefas()
        if(len(Tarefas)==0):
            tarefa_id='tarefa1'
        else:
            tarefa_id = int(max(Tarefas.keys()).lstrip('tarefa')) + 1
            tarefa_id = 'tarefa%i' % tarefa_id
        try:
            post_data ={'_id': tarefa_id, 'tarefa': tarefa, 'ativo' : '1' }
            result = posts.insert_one(post_data)
            Tarefas[tarefa_id] = {'tarefa': tarefa, 'ativo': "1"}
            return Tarefas[tarefa_id], 201
        except Exception as e:
            return f'Erro: {str(e)}', 400


class HealthCheck(Resource):
    def get(self):
        return 200

api.add_resource(Tarefa, '/Tarefa/<tarefa_id>')
api.add_resource(ListaTarefas, '/Tarefas/<tarefa>', '/Tarefas/')
api.add_resource(HealthCheck, '/healthcheck','/')


if __name__ == '__main__':
    app.run(host='0.0.0.0',debug=True)
    
