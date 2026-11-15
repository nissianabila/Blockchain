from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
import hashlib
import json
import time

app = Flask(__name__)
app.secret_key = "blockchain-demo-secret-key"


class Block:
    def __init__(self, index, data="", previous_hash="0" * 64, nonce=0):
        self.index = index
        self.timestamp = time.time()
        self.data = data
        self.previous_hash = previous_hash
        self.nonce = nonce
        self.hash = self.calculate_hash()

    def calculate_hash(self):
        block_data = {
            "index": self.index,
            "timestamp": self.timestamp,
            "data": self.data,
            "previous_hash": self.previous_hash,
            "nonce": self.nonce
        }
        block_string = json.dumps(block_data, sort_keys=True)
        return hashlib.sha256(block_string.encode()).hexdigest()

    def to_dict(self, is_valid=True):
        return {
            "index": self.index,
            "timestamp": self.timestamp,
            "data": self.data,
            "previous_hash": self.previous_hash,
            "nonce": self.nonce,
            "hash": self.hash,
            "is_valid": is_valid
        }


class Blockchain:
    difficulty = 2  # Hash harus diawali dua angka nol.

    def __init__(self):
        self.chain = []
        self.create_genesis_block()

    def create_genesis_block(self):
        genesis = Block(0, "", "0" * 64)
        genesis.hash = self.proof_of_work(genesis)
        self.chain.append(genesis)

    def reset(self):
        self.chain = []
        self.create_genesis_block()

    def proof_of_work(self, block):
        block.nonce = 0
        computed_hash = block.calculate_hash()

        while not computed_hash.startswith("0" * self.difficulty):
            block.nonce += 1
            computed_hash = block.calculate_hash()

        return computed_hash

    def add_block(self):
        last_block = self.chain[-1]
        new_block = Block(
            index=last_block.index + 1,
            data="",
            previous_hash=last_block.hash
        )
        new_block.hash = self.proof_of_work(new_block)
        self.chain.append(new_block)
        return new_block

    def cascade_hash_from(self, start_index):
        self.chain[start_index].hash = self.chain[start_index].calculate_hash()
        for i in range(start_index + 1, len(self.chain)):
            self.chain[i].previous_hash = self.chain[i - 1].hash
            self.chain[i].hash = self.chain[i].calculate_hash()

    def add_transaction_to_block(self, block_index, sender, receiver, amount_value):
        if block_index < 0 or block_index >= len(self.chain):
            return False

        target_block = self.chain[block_index]
        formatted_amount = int(amount_value) if amount_value == int(amount_value) else amount_value
        existing_lines = [line for line in target_block.data.splitlines() if line.strip()]
        line_number = len(existing_lines) + 1
        new_line = f"{line_number}. {sender} -> {receiver} : {formatted_amount}"

        if target_block.data.strip():
            target_block.data = target_block.data.rstrip() + "\n" + new_line
        else:
            target_block.data = new_line

        self.cascade_hash_from(block_index)
        return True

    def update_block_data(self, block_index, new_data):
        if block_index < 0 or block_index >= len(self.chain):
            return False

        self.chain[block_index].data = new_data
        self.cascade_hash_from(block_index)
        return True

    def mine_block(self, block_index):
        if block_index < 0 or block_index >= len(self.chain):
            return None, None

        target_block = self.chain[block_index]
        target_block.hash = self.proof_of_work(target_block)

        for i in range(block_index + 1, len(self.chain)):
            self.chain[i].previous_hash = self.chain[i - 1].hash
            self.chain[i].hash = self.chain[i].calculate_hash()

        new_block = None
        if block_index == len(self.chain) - 1:
            new_block = self.add_block()

        return target_block, new_block

    def is_block_valid(self, index):
        block = self.chain[index]
        if block.hash != block.calculate_hash():
            return False
        if not block.hash.startswith("0" * self.difficulty):
            return False
        if index > 0 and block.previous_hash != self.chain[index - 1].hash:
            return False
        return True

    def is_chain_valid(self):
        return all(self.is_block_valid(i) for i in range(len(self.chain)))

    def get_blocks_state(self):
        return [
            block.to_dict(is_valid=self.is_block_valid(i))
            for i, block in enumerate(self.chain)
        ]


blockchain = Blockchain()


@app.route("/")
def index():
    return render_template(
        "index.html",
        blocks=blockchain.get_blocks_state(),
        is_valid=blockchain.is_chain_valid()
    )


@app.route("/add_transaction", methods=["POST"])
def add_transaction():
    block_index = request.form.get("block_index", type=int)
    sender = request.form.get("sender", "").strip()
    receiver = request.form.get("receiver", "").strip()
    amount = request.form.get("amount", "").strip()

    if block_index is None or not sender or not receiver or not amount:
        flash("Semua kolom transaksi harus diisi.", "error")
        return redirect(url_for("index"))

    try:
        amount_value = float(amount)
        if amount_value <= 0:
            raise ValueError
    except ValueError:
        flash("Jumlah transaksi harus berupa angka lebih dari 0.", "error")
        return redirect(url_for("index"))

    success = blockchain.add_transaction_to_block(block_index, sender, receiver, amount_value)

    if success:
        flash(f"Transaksi ditambahkan ke Data Block {block_index}. Klik Mine untuk memvalidasi.", "success")
    else:
        flash("Blok tidak ditemukan.", "error")

    return redirect(url_for("index"))


@app.route("/tamper", methods=["POST"])
def tamper():
    payload = request.get_json(silent=True) or {}
    block_index = payload.get("block_index")
    new_data = payload.get("data", "")

    if not isinstance(block_index, int) or not blockchain.update_block_data(block_index, new_data):
        return jsonify({"error": "Blok tidak ditemukan"}), 400

    return jsonify({
        "is_valid": blockchain.is_chain_valid(),
        "blocks": blockchain.get_blocks_state()
    })


@app.route("/mine", methods=["POST"])
def mine():
    block_index = request.form.get("block_index", type=int)
    mined_block, new_block = blockchain.mine_block(block_index)

    if mined_block is None:
        flash("Blok tidak ditemukan.", "error")
    elif new_block is not None:
        flash(f"Block {mined_block.index} berhasil di-mine dan Block {new_block.index} dibuat!", "success")
    else:
        flash(f"Block {mined_block.index} berhasil di-mine!", "success")

    return redirect(url_for("index"))


@app.route("/reset", methods=["POST"])
def reset():
    blockchain.reset()
    flash("Blockchain berhasil di-reset ke Block 0.", "success")
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(debug=True)