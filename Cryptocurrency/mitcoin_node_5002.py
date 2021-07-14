# Module 2 - Create a Cryptocurrency

# Importing the libraries
import datetime
import hashlib
import json
from flask import Flask, jsonify, request
import requests
from uuid import uuid4
from urllib.parse import urlparse


# Part 1 - Building a Blockchain

class Blockchain:

    # Declare all the class variables in the __init__ method
    def __init__(self):
        # Initiate the blockchain object to store the chain
        self.chain = []
        # Initialize the transaction object to be stored in each block
        self.transactions = []
        # Initiate the genesis block while creating the object
        self.create_block(proof=1, previous_hash='0')
        # Initiate nodes object to store the distributed nodes like http://127.0.0.1:5000/, http://127.0.0.1:5001/
        self.nodes = set()

    def create_block(self, proof, previous_hash):
        block = {
            'index': len(self.chain) + 1,
            'timestamp': str(datetime.datetime.now()),
            'proof': proof,
            'previous_hash': previous_hash,
            'transactions': self.transactions
        }
        # empty the transactions after adding to the block
        self.transactions = []
        self.chain.append(block)
        return block

    def get_previous_block(self):
        return self.chain[-1];

    def proof_of_work(self, previous_proof):
        new_proof = 1
        check_proof = False
        while check_proof is False:
            hash_operation = hashlib.sha256(str(new_proof ** 2 - previous_proof ** 2).encode()).hexdigest()
            if hash_operation[:4] == '0000':
                check_proof = True
            else:
                new_proof += 1
        return new_proof

    def hash(self, block):
        encoded_block = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(encoded_block).hexdigest()

    # Method to check if the chain is valid
    def is_chain_valid(self, chain):
        # initializing the first block (genesis block)
        previous_block = chain[0]

        # Iterate through each block and do the checks
        block_index = 1
        while block_index < len(chain):
            block = chain[block_index]

            # Check if the block hash is correct (equal to hash of previous block)
            if block['previous_hash'] != self.hash(previous_block):
                return False

            # Check if the proof of current block is correct (proof_of_work() return four leading zeros)
            previous_proof = previous_block['proof']
            proof = block['proof']
            hash_operation = hashlib.sha256(str(proof ** 2 - previous_proof ** 2).encode()).hexdigest()
            if hash_operation[:4] != '0000':
                return False

            # set the current block as the previous_block for the next iteration
            previous_block = block
            # increment the block index
            block_index += 1

        return True

    # method to add the transactions to the transaction object
    def add_transactions(self, sender, receiver, amount):
        self.transactions.append({
            'sender': sender,
            'receiver': receiver,
            'amount': amount
        })

        # return the index of the block added
        previous_block = self.get_previous_block()
        return previous_block['index'] + 1

    # Method to add distributed online node to our list of nodes
    def add_node(self, address):
        parsed_url = urlparse(address)
        self.nodes.add(parsed_url.netloc)

    # Method to replace our chain with the longest chain in all the nodes (network)
    def replace_chain(self):
        network = self.nodes
        longest_chain = None
        max_length = len(self.chain)
        for nodes in network:
            # get the length of chain in each nodes by calling the GET - /get_chain endpoints
            response = requests.get(f'http://{nodes}/get_chain')
            if response.status_code == 200:
                length = response.json()['length']
                chain = response.json()['chain']
                if length > max_length and self.is_chain_valid(chain):
                    max_length = length
                    longest_chain = chain
            # if the longest_chain is not null, then a longest chain has been found in other node
            if longest_chain:
                self.chain = longest_chain
                return True

            # else return false
            return False


# Part 2 - Mining our Blockchain (API endpoints to work with the blockchain)

# Creating a Web App
app = Flask(__name__)

# Creating an address for the node on Port 5000
node_address = str(uuid4()).replace('-', '')  # generate an unique id and remove the dashes

# Create a Blockchain
blockchain = Blockchain()


# Mining a new block
@app.route('/mine_block', methods=['GET'])
def mine_block():
    previous_block = blockchain.get_previous_block()
    previous_proof = previous_block['proof']

    proof = blockchain.proof_of_work(previous_proof)
    previous_hash = blockchain.hash(previous_block)
    blockchain.add_transactions(sender=node_address, receiver='Soumya', amount=1)

    block = blockchain.create_block(proof, previous_hash)

    response = {
        'message': 'Congratulations, you just mined a block!',
        'index': block['index'],
        'timestamp': block['timestamp'],
        'proof': block['proof'],
        'previous_hash': block['previous_hash'],
        'transactions': block['transactions']
    }

    return jsonify(response), 200


# Get the full blockchain
@app.route('/get_chain', methods=['GET'])
def get_chain():
    response = {
        'chain': blockchain.chain,
        'length': len(blockchain.chain)
    }

    return jsonify(response), 200


# Check if the chain is valid
@app.route('/is_valid', methods=['GET'])
def is_valid():
    result = blockchain.is_chain_valid(blockchain.chain)
    if result:
        response = {
            'message': 'All good. The blockchain is valid'
        }
    else:
        response = {
            'message': 'We have a problem. The blockchain is not valid'
        }
    return jsonify(response), 200


# endpoint to add a transaction to our list of transactions
@app.route('/add_transaction', methods=['POST'])
def add_transaction():
    # get the json request payload from POST request
    json = request.get_json()
    transaction_keys = ['sender', 'receiver', 'amount']
    # if any of the transaction keys are missing, return negative response
    if not all(key in json for key in transaction_keys):
        return 'Some elements of the transaction are missing', 400
    # else add the transaction to our list of transactions
    index = blockchain.add_transactions(json['sender'], json['receiver'], json['amount'])
    response = {
        'message': f'This transaction will be added to block {index}'
    }
    return jsonify(response), 201


# Part 3 - Decentralizing our Blockchain


# Connecting new nodes
@app.route('/connect_node', methods=['POST'])
def connect_node():
    # get the json request payload from POST request
    json = request.get_json()
    nodes = json.get('nodes')  # example payload json = {"nodes": ['http://127.0.0.1:5000','http://127.0.0.1:5001']}
    if nodes is None:
        return "No node", 400
    for node in nodes:
        blockchain.add_node(node)
    response = {
        'message': 'All the nodes are now connected. The Mitcoin blockchain now contains the following nodes',
        'total_nodes': list(blockchain.nodes)
    }
    return jsonify(response), 201


# Replacing the chain by the longest chain if needed
@app.route('/replace_chain', methods=['GET'])
def replace_chain():
    is_chain_replaced = blockchain.replace_chain()
    if is_chain_replaced:
        response = {
            'message': 'The nodes had different chains, so the chain was replaced by the longest ones',
            'new_chain': blockchain.chain
        }
    else:
        response = {
            'message': 'All good. The chain is the largest one.',
            'actual_chain': blockchain.chain
        }
    return jsonify(response), 200


# Running the app
app.run(host='0.0.0.0', port=5002)
