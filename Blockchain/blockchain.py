# Module 1 - Create a Blockchain

# Importing the libraries
import datetime
import hashlib
import json
from flask import Flask, jsonify


# Part 1 - Building a Blockchain

class Blockchain:

    def __init__(self):
        self.chain = []
        # initiate the genesis block while creating the object
        self.create_block(proof=1, previous_hash='0')

    def create_block(self, proof, previous_hash):
        block = {
            'index': len(self.chain) + 1,
            'timestamp': str(datetime.datetime.now()),
            'proof': proof,
            'previous_hash': previous_hash
        }
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


# Part 2 - Mining our Blockchain (API endpoints to work with the blockchain)

# Creating a Web App
app = Flask(__name__)

# Create a Blockchain
blockchain = Blockchain()


# Mining a new block
@app.route('/mine_block', methods=['GET'])
def mine_block():
    previous_block = blockchain.get_previous_block()
    previous_proof = previous_block['proof']

    proof = blockchain.proof_of_work(previous_proof)
    previous_hash = blockchain.hash(previous_block)

    block = blockchain.create_block(proof, previous_hash)

    response = {
        'message': 'Congratulations, you just mined a block!',
        'index': block['index'],
        'timestamp': block['timestamp'],
        'proof': block['proof'],
        'previous_hash': block['previous_hash']
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


# Running the app
app.run(host='0.0.0.0', port=5000)
