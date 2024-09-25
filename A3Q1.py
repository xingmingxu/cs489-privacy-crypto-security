import os
import hashlib
import json

LEADING_ZEROES = 5
HASH_LENGTH = LEADING_ZEROES + 1
# TODO: Enter your WatIAM ID here
WatIAM_ID = "********"
ADMIN_ID = "admin"
# Dict keys
PREVIOUS_HASH_KEY = 'previous_hash'
PROOF_KEY = 'proof'
ID_KEY = 'ID'

class Blockchain:
    """
    This object stores a simple blockchain.
    """
    def __init__(self):
        """
        Initializes the blockchain with a genesis block.
        """
        self.chain = []
        self.chain.append(self.create_block(proof=1, previous_hash='0', id='satoshi'))
    
    def hash_block(self, block: dict) -> str:
        """
        Computes the SHA-256 hash of a given block.

        Args:
        - block (dict): The block to be hashed.

        Returns:
        - str: The SHA-256 hash of the block.
        """
        encoded_block = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(encoded_block).hexdigest()[:HASH_LENGTH]
    
    def add_block(self, block: dict) -> None:
        """
        Adds a new block to the blockchain if it meets validity conditions.

        Args:
        - block (dict): The block to be added.

        Returns:
        - None
        """
        condition_1 = block[PREVIOUS_HASH_KEY] == self.hash_block(self.get_last_block())
        condition_2 = self.hash_block(block)[:LEADING_ZEROES] == LEADING_ZEROES*'0'
        if condition_1 and condition_2:
            self.chain.append(block)
        else:
            print(f"ERROR: proposed block at index {len(self.chain)} is not valid")
            exit()

    def create_block(self, proof: int, previous_hash: str, id: str) -> dict:
        """
        Creates a new block for the blockchain.

        Args:
        - proof (int): The proof number of the block.
        - previous_hash (str): The hash of the previous block.
        - id (str): Your WatIAM ID.

        Returns:
        - dict: The newly created block.
        """
        block = {PREVIOUS_HASH_KEY: previous_hash,
                PROOF_KEY: proof,
                ID_KEY: id}
        return block

    def get_last_block(self) -> dict:
        """
        Retrieves the last block from the blockchain.

        Returns:
        - dict: The last block in the blockchain.
        """
        return self.chain[-1]

    def dump_proofs(self, save_file="blockchain.txt") -> None:
        """
        Dumps the proof numbers of blocks in the blockchain to a file.

        Args:
        - save_file (str): The filename to save the proofs. Default is 'blockchain.txt'.

        Returns:
        - None
        """
        with open(save_file, 'w+') as dump_file:
            dump_file.write(f'{WatIAM_ID}\n')
            for block in self.chain[1:]:
                dump_file.write(f'{block[PROOF_KEY]}\n')
    
    def dump_collision(self, collision_block, save_file="collision.txt") -> None:
        """
        Dumps the proof number of the found collision block into a file.

        Args:
        - save_file (str): The filename to save the collision proof. Default is 'collision.txt'.

        Returns:
        - None
        """
        with open(save_file, 'w+') as dump_file:
            dump_file.write(f'{ADMIN_ID}\n')
            dump_file.write(f'{collision_block[PROOF_KEY]}\n')
    
    def load_from_dump_file(self, save_file="blockchain.txt", collision_file="collision.txt") -> None:
        """
        Loads the blockchain from a dump file containing proof numbers.

        Args:
        - save_file (str): The filename from which to load the proofs. Default is 'blockchain.txt'.
        - collision_file (str): The filename from which to load the collision proof. Default is 'collision.txt'.

        Returns:
        - None
        """
        with open(save_file, 'r') as dump_file:
            lines = list(map(str.strip, dump_file.readlines()))
        id = lines[0]
        for proof in lines[1:]:
            block = self.create_block(int(proof), self.hash_block(self.get_last_block()), id)
            self.add_block(block)
        print('SUCCESS: loaded successfully!')
        if os.path.exists(collision_file):
            with open(collision_file, 'r') as dump_file:
                collision_lines = list(map(str.strip, dump_file.readlines()))
            admin_id = collision_lines[0]
            if admin_id != ADMIN_ID:
                print('Error: collision file was faulty. Exiting!')
                exit()
            collision_proof = int(collision_lines[1])
            collision_block = self.create_block(collision_proof, self.hash_block(self.chain[-2]), admin_id)
            if self.hash_block(collision_block) == self.hash_block(self.get_last_block()):
                print('SUCCESS: collision is correct! Good job!')
            else:
                print(self.hash_block(collision_block), self.hash_block(self.get_last_block())) # added
                print('ERROR: collision is faulty. Try again.')
        else:
            print('ERROR: no collision file found')

    def mine_new_block(self, previous_hash: str, id: str) -> dict:
        """
        Mines and returns a new valid block for the blockchain.

        Args:
        - previous_hash (str): The hash of the previous block.
        - id (str): Your WatIAM ID.

        Returns:
        - dict: The newly mined block.
        """
        # TODO: Implement the mining process to create a valid block
        nonce = 0
        while True:
            block = self.create_block(nonce, previous_hash, id)
            if self.hash_block(block)[:LEADING_ZEROES] == LEADING_ZEROES*'0':
                return block
            nonce += 1

    def mine_chain(self, id: str, chain_length=5) -> None:
        """
        Mines a specified number of blocks and saves proofs to a file.

        Args:
        - id (str): Your WatIAM ID.
        - chain_length (int): Number of blocks to mine. Default is 5.

        Returns:
        - None
        """
        # TODO: Implement mining of the entire chain
        # This line dumps your proofs to a file. You must submit the dump file
        for i in range(chain_length):
            self.add_block(self.mine_new_block(self.hash_block(self.get_last_block()), id))
        self.dump_proofs()
    
    def find_collision(self, id=ADMIN_ID) -> dict:
        """
        Mines and returns a collision block for the last block with a new id.

        Args:
        - id (str): The new ID which is set to the ADMIN_ID.

        Returns:
        - dict: The newly mined collision block.
        """
        # TODO: Implement the process of finding a collision for the last block.
        # The collision must share the previous hash value with the last block, but have a different proof and ID.
        # The collision block's hash must be equal to the hash value of the last block.

        # self.create_block(collision_proof, self.hash_block(self.chain[-2]), admin_id)
        prev_hash = self.hash_block(self.chain[-2])
        old_proof = self.get_last_block()[PROOF_KEY]
        old_hash = self.hash_block(self.get_last_block())[:HASH_LENGTH]

        new_proof = 0 # collision_proof
        while True:
            if new_proof != old_proof:
                collision_block = self.create_block(new_proof, prev_hash, id) # id=ADMIN_ID
                #print(self.hash_block(collision_block[:HASH_LENGTH]), old_hash)
                if self.hash_block(collision_block)[:HASH_LENGTH] == old_hash:
                    self.dump_collision(collision_block)
                    break
            new_proof += 1

        print(f'original proof: {self.get_last_block()[PROOF_KEY]}')
        print(f'collision proof: {new_proof}')
        self.dump_collision(collision_block)
        return collision_block

import time
if __name__ == "__main__":
    blockchain = Blockchain()
    #start = time.time()
    blockchain.mine_chain(WatIAM_ID)
    ##end = time.time()
    #print("Mine chain complete", end - start)
    blockchain.find_collision(ADMIN_ID)
    #end = time.time()
    #print("Collision found", end - start)   
    # NOTE: This function is what will be used to evaluate your answer
    testing_blockchain = Blockchain()
    testing_blockchain.load_from_dump_file()
