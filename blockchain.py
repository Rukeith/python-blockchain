import hashlib
import json
from time import time
from uuid import uuid4
from flask import Flask

class Blockchain(object):
  def __init__(self):
    self.current_transactions = []
    self.chain = []
    # Create the genesis block
    self.new_block(previous_hash = 1, proof = 100)
  def new_block(self, proof, previous_hash = None):
    """
    Create a new block
    :param proof: <int> The proof given by the Proof of Work algorithm
    :param previous_hash: (Optional) <str> Hash of previous Block
    :return: <dict> New Block
    """
    block = {
      'index': len(self.chain) + 1,
      'timestamp': time(),
      'transactions': self.current_transactions,
      'proof': proof,
      'previous_hash': previous_hash or self.hash(self.chain[-1]),
    }
    # Reset the current list of transactions
    self.current_transactions = []
    self.chain.append(block)
    return block
  def new_transaction(self, sender, recipient, amount):
    """
    Create a new trade information, put it to next block
    :param sender: <str> Address of the Sender
    :param recipient: <str> Address of the Recipient
    :param amount: <int> Amount
    :return: <int> The index of the Block that will hold this transaction
    """
    self.current_transactions.append({
      'sender': sender,
      'recipient': recipient,
      'amount': amount,
    })
    return self.last_block['index'] + 1
  @staticmethod
  def hash(block):
    """
    Generate block's SHA-256 hash
    :param block: <dict> Block
    :return: <str>
    """
    # We must make sure that the Dictionary is Ordered, or we'll have inconsistent hashes
    block_string = json.dumps(block, sort_keys = True).encode()
    return hashlib.sha256(block_string).hexdigest()
  @property
  def last_block(self):
    return self.chain[-1]
  def proof_of_work(self, last_proof):
    """
    Simple work proof
      - Find a p' to make hash(pp') start from 0000
      - p is proof of previous work, p' is current proof
    :param last_proof: <int>
    :return: <int>
    """
    proof = 0
    while self.valid_proof(last_proof, proof) is False:
      proof += 1
    return proof
  @staticmethod
  def valid_proof(last_proof, proof):
    """
    Find hash(last_proof, proof) is start by 0000
    :param last_proof: <int> Previous Proof
    :param proof: <int> Current Proof
    :return: <bool> True if correct, False if not.
    """
    guess = '{last_proof}{proof}'.encode()
    guess_hash = hashlib.sha256(guess).hexdigest()
    return guess_hash[:4] == "0000"

# Instantiate our Node
app = Flask(__name__)
# Generate a globally unique address for this node
node_identifier = str(uuid4()).replace('-', '')
# Instantiate the Blockchain
blockchain = Blockchain()
@app.route('/mine', methods=['GET'])
def mine():
  return "We'll mine a new Block"

@app.route('/transactions/new', methods=['POST'])
def new_transaction():
  values = request.get_json()
  # Check that the required fields are in the POST'ed data
  required = ['sender', 'recipient', 'amount']
  if not all(k in values for k in required):
    return 'Missing values', 400
  # Create a new Transaction
  index = blockchain.new_transaction(values['sender'], values['recipient'], values['amount'])
  response = { 'message': 'Transaction will be added to Block {index}' }
  return jsonify(response), 201

@app.route('/chain', methods=['GET'])
def full_chain():
  response = {
      'chain': blockchain.chain,
      'length': len(blockchain.chain),
  }
  return jsonify(response), 200
if __name__ == '__main__':
  app.run(host='0.0.0.0', port=5000)