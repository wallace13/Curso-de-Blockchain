import datetime
import hashlib
import json
from flask import Flask, jsonify, request
import requests
from uuid import uuid4
from urllib.parse import urlparse

class Blockchain:

    ##Metodo de inicialização
    def __init__(self):
        self.chain = []
        ##cria uma lista vazia,pra posteriormente receber as transações
        self.transactions = []
        self.create_block(proof = 1, previous_hash = '0')
        ##Objeto que tem todos os nós da rede
        self.nodes = set()
        
    ##Cria um Block 
    def create_block(self, proof, previous_hash):
        block = {'index': len(self.chain) + 1,
                 'timestamp': str(datetime.datetime.now()),
                 'proof': proof,
                 'previous_hash': previous_hash,
                 'transactions': self.transactions}
        ##Zera a lista de transações
        self.transactions = []
        self.chain.append(block)
        return block

    def get_previous_block(self):
        return self.chain[-1]

    def proof_of_work(self, previous_proof):
        new_proof = 1
        check_proof = False
        while check_proof is False:
            hash_operation = hashlib.sha256(str(new_proof**2 - previous_proof**2).encode()).hexdigest()
            if hash_operation[:4] == '0000':
                check_proof = True
            else:
                new_proof += 1
        return new_proof
    
    def hash(self, block):
        encoded_block = json.dumps(block, sort_keys = True).encode()
        return hashlib.sha256(encoded_block).hexdigest()
    
    def is_chain_valid(self, chain):
        previous_block = chain[0]
        block_index = 1
        while block_index < len(chain):
            block = chain[block_index]
            if block['previous_hash'] != self.hash(previous_block):
                return False
            previous_proof = previous_block['proof']
            proof = block['proof']
            hash_operation = hashlib.sha256(str(proof**2 - previous_proof**2).encode()).hexdigest()
            if hash_operation[:4] != '0000':
                return False
            previous_block = block
            block_index += 1
        return True

    ##Uma transação só
    def add_transaction(self, sender, receiver, amount):
        ##sender = remetente da função
        self.transactions.append({'sender': sender,
                                    ##recebido da função
                                  'receiver': receiver,
                                  'amount': amount})
        ##previos_block retorna o indice
        previous_block = self.get_previous_block()
        ##retorna a variavel que criamos mais 1
        return previous_block['index'] + 1
    
    ##Metodo de adicionar nós
    def add_node(self, address):
        ##endereço 
        parsed_url = urlparse(address)
        ##Extrai do endereço apenas o endereço do nó
        self.nodes.add(parsed_url.netloc)
    
    ##Faz a subtituição da cadeia do blockchain se ele encontrar um block maior
    def replace_chain(self):
        ##Copia dos nós
        network = self.nodes
        ##encontra a cadeia mais longa
        longest_chain = None
        ##acha a cadeia mais longa
        max_length = len(self.chain)
        ##percorre todos os nós da rede pra achar o blockchain maior
        for node in network:
            ##pega o comprimento do nó da rede
            response = requests.get(f'http://{node}/get_chain')
            ##verifica se a reposta do response veio correta
            if response.status_code == 200:
                ##comprimento da resposta
                length = response.json()['length']
                ##pega o blockchain, a cadeia de blocos
                chain = response.json()['chain']
                ##Verifica se ele é maior que o tamanho maximo
                if length > max_length and self.is_chain_valid(chain):
                    ##atualiza a variavel max_length
                    max_length = length
                    ##atualiza a variavel longest_chain
                    longest_chain = chain
        ##Verifica se a variavel não esta vazia
        ##se não está vazia, foi encontrado um bloco maior
        if longest_chain:
            self.chain = longest_chain
            return True
        ##se não encontrar retorna falso
        return False

app = Flask(__name__)

##Variavel  que substitui os traços do nó
node_address = str(uuid4()).replace('-', '')

blockchain = Blockchain()

@app.route('/mine_block', methods = ['GET'])
def mine_block():
    previous_block = blockchain.get_previous_block()
    previous_proof = previous_block['proof']
    proof = blockchain.proof_of_work(previous_proof)
    previous_hash = blockchain.hash(previous_block)
    ##Inclui as transações / amount é quanto a transação esta mandando
    blockchain.add_transaction(sender = node_address, receiver = 'Fernando', amount = 1)
    block = blockchain.create_block(proof, previous_hash)
    response = {'message': 'Parabens voce acabou de minerar um bloco!',
                'index': block['index'],
                'timestamp': block['timestamp'],
                'proof': block['proof'],
                'previous_hash': block['previous_hash'],
                ##elemento transação
                'transactions': block['transactions']}
    ##Resposta da mineiração do bloco
    return jsonify(response), 200

@app.route('/get_chain', methods = ['GET'])
def get_chain():
    response = {'chain': blockchain.chain,
                'length': len(blockchain.chain)}
    return jsonify(response), 200

@app.route('/is_valid', methods = ['GET'])
def is_valid():
    is_valid = blockchain.is_chain_valid(blockchain.chain)
    if is_valid:
        response = {'message': 'Tudo certo, o blockchain e valido.'}
    else:
        response = {'message': 'o blockchain nao e valido.'}
    return jsonify(response), 200

##metodo para adicionar transações ao bloco
@app.route('/add_transaction', methods = ['POST'])
def add_transaction():
    ##pegar o arquivo json que o post vai enviar
    json = request.get_json()
    ##lista as chaves
    ##verifica se existe as chaves  
    transaction_keys = ['sender','receiver','amount']
     ##verifica se não existiu todas as chaves  que estão na transação
    if not all(key in json for key in transaction_keys):
        ##codigo 400 é um codigo de erro
        return 'Alguns elementos estao faltando',400
    ##se transação está ok, nós a adicionamos ao bloco
    index = blockchain.add_transaction(json['sender'],json['receiver'],json['amount'])
    response = {'message': f'Esta tramsacao sera adicionada ao bloco {index}'}
    ##codigo 201 usado quando nós temos um post, é um codigo pra informar que a transação foi bem sucedida
    return jsonify(response),201

##conecta nós
@app.route('/connect_node', methods = ['POST'])
def connect_node():
    ##todos os nos da rede
    json = request.get_json()
    ##armazena a chave node
    nodes = json.get('nodes')
    ##verifica se a requisição não esta vazia
    if nodes is None:
        return "Vazio", 400
    ##for para adicionar os nós
    for node in nodes:
        blockchain.add_node(node)
    ##mensagem e todos os nós conectados, total_nodes exibe a lista de todos os nós
    response = {'message': 'Todos nos conectados, blockchain contem os seguintes nos:',
                'total_nodes': list(blockchain.nodes)}
    return jsonify(response),201

##metodo para substituir a cadeia, subtituir o blockchain se necessario
@app.route('/replace_chain',methods= ['GET'])
def replace_chain():
    is_chain_replaced = blockchain.replace_chain()
    if is_chain_replaced:
        response = {'message': 'Os nos tinham cadeias diferentes então foi substituida ',
                    'new_chain' : blockchain.chain}
    else:
        response = {'message': 'Tudo certo, nao houve substituicao ', 
                   'actual_chain' : blockchain.chain}
    return jsonify(response), 201 

app.run(host = '0.0.0.0', port = 5000)

