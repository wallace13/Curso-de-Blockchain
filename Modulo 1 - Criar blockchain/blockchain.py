import datetime
import hashlib
import json
from flask import Flask, jsonify

class Blockchain:

    def __init__(self):
        self.chain = []
        self.create_block(proof = 1, previous_hash = '0')

    ##cria um bloco
    def create_block(self, proof, previous_hash):
        block = {'index': len(self.chain) + 1,
                 'timestamp': str(datetime.datetime.now()),
                 'proof': proof,
                 'previous_hash': previous_hash}
        self.chain.append(block)
        return block

    ##retorna o bloco anterior
    def get_previous_block(self):
        return self.chain[-1]

    ##SELF = OBJETO / PREVIOIS_PROOF É O ELEMENTO DO PROBLEMA
    ##PRA ACHAR A NOVA PROVA 
    def proof_of_work(self, previous_proof):
        new_proof = 1
        check_proof = False
        ##CHECA SE É FALSO E CONTINUA NO WHILE ENQUANTO FOR FALSO
        while check_proof is False:
            ##PRODUZ HASH, VERIFICA O NIVEL DE DIFICULDADE COM 4 ZEROS A ESQUERDA
            ##DEPOIS CONVERTE PRA HEXADECIMAL EM HEXDIGEST
            hash_operation = hashlib.sha256(str(new_proof**2 - previous_proof**2).encode()).hexdigest()
            ##VERIFICA SE ELE ATENDE O NIVEL DE DIFICULDADE 
            ##VERIFICA SE ELE RESOLVEU O PROBLEMA
            if hash_operation[:4] == '0000':
                check_proof = True
            else:
                ##SE NÃO ATENDEU INCREMENTA
                new_proof += 1
        ##QUANDO O PROBLEMA É RESOLVIDO, RETORNA A SOLUÇÃO
        return new_proof

    ##FUNÇÃO DE HASH ESTRUTURADA
    def hash(self, block):
        ##GERA UM JSON E APARTIR DESSE JSON GERA UM BLOCO
        encoded_block = json.dumps(block, sort_keys = True).encode()
       ##RETORNA O HASH 256 DESSE JSON E CONVERTE PARA HEXADECIMAL
        return hashlib.sha256(encoded_block).hexdigest()
    
    ##VERIFICA SE OS BLOCOS SÃO VALIDOS
    def is_chain_valid(self, chain):
        ##INICIALIZA O BLOCO ANTERIOR DO OBJETO CHAIN
        ##CHAIN SÃO TODOS OS BLOCOS
        previous_block = chain[0]
        ##INICIALIZA O BLOCO ATUAL
        block_index = 1
        ##PASSA POR TODOS OS BLOCOS
        while block_index < len(chain):
            block = chain[block_index]
            ##VERIFICA SE HASH DO BLOCO ATUAL CONDIZ COM O ANTERIOR
            ##SE FOR SIGNIFICA QUE JA HOUVE FALHA E QUE O HASH ATUAL NÃO É VALIDO
            if block['previous_hash'] != self.hash(previous_block):
                return False
            previous_proof = previous_block['proof']
            proof = block['proof']
            hash_operation = hashlib.sha256(str(proof**2 - previous_proof**2).encode()).hexdigest()
            ##VERIFICA SE O HASH COMEÇA COM 4 ZEROS
            ##SE NÃO É VALIDO RETORNA FALSO
            if hash_operation[:4] != '0000':
                return False
            previous_block = block
            ##INCREMENTA O INDICE DO LAÇO
            block_index += 1
        ##SE NENHUMA CHECAGEM ENTRAR DENTRO DE UM IF O BLOCO É VALIDO
        return True

##FUNÇÃO PARA INTERAGIR COM O BLOCKCHAIN
app = Flask(__name__)

##CRIA A INSTANCIA DA CLASSE BLOCKCHAIN
blockchain = Blockchain()

##FUNÇÃO QUE MINERA O BLOCO A PARTIR DA INSTANCIA QUE A GENTE CRIOU
##/MINE É O NOSSO ENDEREÇO, A NOSSA URL, ESSE É O NOME DA PAGINA E O METODO USADO PARA ACCESAR A PAGINA É O GET
##O GET É USADO PRA PEGAR ALGO DA PAGINA
@app.route('/mine_block', methods = ['GET'])
##FUNÇÃO DE MINERAÇÃO
def mine_block():
    ##BLOCO ANTERIOR
    previous_block = blockchain.get_previous_block()
    ##PEGA O PROOF DO BLOCO ANTERIOR
    previous_proof = previous_block['proof']
    ##PEGA O PROOF OF WORK DO BLOCO ANTERIOR
    proof = blockchain.proof_of_work(previous_proof)
    ##PEGA O HASH ANTEROR
    previous_hash = blockchain.hash(previous_block)
    ##CRIAR O BLOCO
    block = blockchain.create_block(proof, previous_hash)
    ##RESULTADO DA NOSSA MINERAÇÃO
    ##A GENTE USA REPONSE PRA EXIBIR NA PAGINA
    response = {'message': 'Parabens voce acabou de minerar um bloco!',
                #INDICE DO BLOCO
                'index': block['index'],
                #HORARIO DA MINERAÇÃO
                'timestamp': block['timestamp'],
                #PROVA DA MINERAÇÃO
                'proof': block['proof'],
                #HASH ANTERIOR
                'previous_hash': block['previous_hash']}
    ##RETORNA OS ELEMENTOS A SEREM EXIBIDOS
    ##200 SIGINIFICA QUE TUDO FOI BEM RECEBIDO
    return jsonify(response), 200

##FUNÇÃO QUE RETORNA TODO O BLOCKCHAIN
##RETORNA TODOS OS BLOCOS
@app.route('/get_chain', methods = ['GET'])
def get_chain():
    response = {'chain': blockchain.chain,
                ##TAMANHO DO BLOCKCHAIN
                'length': len(blockchain.chain)}
    return jsonify(response), 200

##VERIFICA SE O BLOCKCHAIN É VALIDO
@app.route('/is_valid', methods = ['GET'])
def is_valid():
    is_valid = blockchain.is_chain_valid(blockchain.chain)
    if is_valid:
        response = {'message' : ' Tudo certo, o blockchain e valido '}
    else:
        response = {'message' : ' O blockchain nao e valido '}
    return jsonify(response), 200

##RODA O HOST, RODA A APLICAÇÃO
app.run(host = '0.0.0.0', port = 5000)
