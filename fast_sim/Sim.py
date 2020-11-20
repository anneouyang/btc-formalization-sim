import random
import matplotlib.pyplot as plt
import time

from Block import Block
from Node import Node

class Sim():

	def __init__(self, N, P, R, tb="z"):

		# experiment parameters
		self.N = N
		self.P = P
		self.R = R
		self.tb = tb

		# index is id -> (height, prev_block_id, miner_id, nxt_blocks_ids)
		# blocks are 0-indexed
		# genesis block starts at height 1
		# -1 is the default value for N/A
		# initialize the list of blocks with the genesis block
		self.blocks = [Block(1, -1, -1, [])]
		# initialize all nodes to point to the genesis block
		# nodes are 0-indexed
		self.nodes = [Node() for i in range(self.N)]

		self.max_convergence_height = 1
		self.cur_lca = 0
		self.cur_assigned_id = 0
		self.consensus_height_by_round = [1 for i in range(self.R + 1)]

		self.num_blocks_mined = 1
		self.blocks_mined_in_cur_round = []


	def get_longest_chains(self):
		"""
		Get all candidates for longest chains
		"""
		longest_chains_height = 0
		for i in range(self.N):
			longest_chains_height = max(longest_chains_height, self.nodes[i].max_height)
		ret = set()
		for i in range(self.N):
			if self.nodes[i].max_height == longest_chains_height:
				# print(self.nodes[i].max_height, self.nodes[i].head, self.blocks[self.nodes[i].head].height)
				ret.add(self.nodes[i].head)
		return list(ret)


	def tie_break_by_random(self, longest_chains, node_id):
		return random.choice(longest_chains)


	def tie_break_by_first_seen(self, longest_chains, node_id):
		for i in range(len(longest_chains)):
			if self.blocks[longest_chains[i]].miner_id == node_id:
				return longest_chains[i]
		return self.tie_break_by_random(longest_chains, node_id)


	def update_longest_chain(self, longest_chains, node_id, tie_breaking_function):
		block_to_mine_on = tie_breaking_function(longest_chains, node_id)
		self.nodes[node_id].max_height = self.blocks[block_to_mine_on].height
		self.nodes[node_id].head = block_to_mine_on


	def mine_block(self, node_id):
		_ = random.uniform(0, 1)
		if _ > self.P:
			return

		# get new block index
		block_to_mine_on = self.nodes[node_id].head
		new_block_id = self.num_blocks_mined
		self.num_blocks_mined += 1

		# assign an index 
		assigned_id = -1
		if (block_to_mine_on == self.cur_lca):
			assigned_id = self.cur_assigned_id
			self.cur_assigned_id += 1
		else:
			assigned_id = self.blocks[block_to_mine_on].assigned_id

		# make new block
		self.blocks.append(Block(self.blocks[block_to_mine_on].height + 1, block_to_mine_on, node_id, [], assigned_id))

		# update children list of old block
		self.blocks[block_to_mine_on].nxt_blocks_id.append(new_block_id)

		# update record of nodes
		self.nodes[node_id].max_height = self.blocks[new_block_id].height
		self.nodes[node_id].head = new_block_id

		self.blocks_mined_in_cur_round.append(new_block_id)


	def reassign_ids(self):
		q = [self.cur_lca]
		q_ind = 0
		self.cur_assigned_id = 0
		while q_ind < len(q):
			if self.blocks[q[q_ind]].prev_block_id == self.cur_assigned_id:
				self.blocks[q[q_ind]].assigned_id = self.cur_assigned_id
				self.cur_assigned_id += 1
			else:
				self.blocks[q[q_ind]].assigned_id = self.blocks[self.blocks[q[q_ind]].prev_block_id].assigned_id
			for child_id in self.blocks[q[q_ind]].nxt_blocks_id:
				q.append(child_id)
			q_ind += 1


	def check_for_convergence(self):
		# if the assigned ids are not the same, do not find LCA yet
		if len(self.blocks_mined_in_cur_round) > 0:
			prev = self.blocks[self.blocks_mined_in_cur_round[0]].assigned_id
			for i in range(1, len(self.blocks_mined_in_cur_round)):
				if self.blocks[self.blocks_mined_in_cur_round[i]].assigned_id != prev:
					return
				prev = self.blocks[self.blocks_mined_in_cur_round[i]].assigned_id
		# find LCA
		cur_conv_height = self.nodes[0].max_height
		# get nodes at height cur_conv_height
		blocks_at_node_height = [-1 for i in range(self.N)]
		# print([self.nodes[i].max_height for i in range(self.N)])
		for i in range(self.N):
			assert(self.nodes[i].max_height == cur_conv_height)
			blocks_at_node_height[i] = self.nodes[i].head
		while True:
			assert(cur_conv_height >= 0)
			# print(blocks_at_node_height)
			conv_block_id = -1
			flag = True
			for i in range(self.N):
				if conv_block_id == -1:
					conv_block_id = blocks_at_node_height[i]
				if conv_block_id != blocks_at_node_height[i]:
					flag = False
					break
			assert(conv_block_id != -1)
			if flag:
				self.max_convergence_height = cur_conv_height
				self.cur_lca = conv_block_id
				self.reassign_ids()
				break
			cur_conv_height -= 1
			for i in range(self.N):
				blocks_at_node_height[i] = self.blocks[blocks_at_node_height[i]].prev_block_id


	def print_info(self):
		print("total number of blocks mined: ", self.num_blocks_mined)
		print("number of blocks in consensus: ", self.max_convergence_height)
		print("percentage discarded: ", 1 - self.max_convergence_height / self.num_blocks_mined)

	def plot_time_consensus_height(self):
		plt.plot(range(1, self.R + 1), self.consensus_height_by_round[1:])
		plt.show()


	def run(self):
		"""
		Main function of the simulation
		"""
		random.seed(time.time())
		# rounds are 0 indexed, genesis block is mined in round 0
		for r in range(1, self.R + 1):
			# # DEBUG PRINT: blocks list
			# print([(self.blocks[i].height, self.blocks[i].prev_block_id, self.blocks[i].miner_id, self.blocks[i].assigned_id) for i in range(len(self.blocks))])
			# update longest chains
			longest_chains = self.get_longest_chains()
			# if (r % 100 == 0):
			# 	print("round ", r, "/", self.R)
			# # DEBUG PRINT: longest chains
			# print("longest chains: ", longest_chains)
			# print([self.blocks[i].height for i in longest_chains])
			for i in range(self.N):
				if (self.tb[0] == "f"):
					self.update_longest_chain(longest_chains, i, self.tie_break_by_first_seen)
				else:
					self.update_longest_chain(longest_chains, i, self.tie_break_by_random)
			# check for convergence
			self.check_for_convergence()
			self.consensus_height_by_round[r] = self.max_convergence_height
			self.blocks_mined_in_cur_round = []
			# mine new blocks
			for i in range(self.N):
				self.mine_block(i)
			# print("")
		return self.max_convergence_height
		# self.print_info()
		# self.plot_time_consensus_height()



