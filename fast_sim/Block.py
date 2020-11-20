
class Block():
	
	def __init__(self, height, prev_block_id, miner_id, nxt_blocks_id = [], assigned_id = -1):
		self.height = height
		self.prev_block_id = prev_block_id
		self.miner_id = miner_id
		self.nxt_blocks_id = nxt_blocks_id
		self.assigned_id = assigned_id