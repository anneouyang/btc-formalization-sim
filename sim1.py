import random
import matplotlib.pyplot as plt
import time
import secrets

WINDOW_LEN = 1000
MAX_ROUNDS = 1000
p = .1
n = 1000
# nodes indexed from 0 to n-1 inclusive

num_blocks_mined_total = 1
new_blocks_produced = 0
# num_blocks_agreed_by_all_nodes = 0

# contains all the mined blocks
# id -> (height, prev_id, miner_id, round_num)
blocks = {0: (1, -1, -1, 0)} 

# contains the latest WINDOW_LEN nodes of its chain and height of its most recent block
nodes = [{'height':1, 'blocks':{1:0}} for i in range(n)] 

max_convergence_height = 1
consensus_blocks = [-1 for i in range(MAX_ROUNDS + 1)]
consensus_height_by_round = [0 for i in range(MAX_ROUNDS + 1)]

rounds_interval_only_one_node_mine = []


def get_longest_chains():
	longest_chain_height = 0
	for i in range(n):
		longest_chain_height = max(longest_chain_height, nodes[i]['height'])
	ret = set()
	for i in range(n):
		if nodes[i]['height'] == longest_chain_height and nodes[i]['blocks'][longest_chain_height] not in ret:
			ret.add(nodes[i]['blocks'][longest_chain_height])
	return list(ret)

def tie_break_by_first_seen(longest_chains, node_id):
	for i in range(len(longest_chains)):
		if blocks[longest_chains[i]][2] == node_id:
			return longest_chains[i]
	return tie_break_by_random(longest_chains, node_id)


def tie_break_by_random(longest_chains, node_id):
	return secrets.choice(longest_chains)


def update_longest_chain(node_id, longest_chains, tie_breaking_function, r):
	# if(len(longest_chains) == 1 and node_id == 1):
	# 	print("round", r)
	block_to_mine_on = tie_breaking_function(longest_chains, node_id)
	# print(block_to_mine_on)
	nodes[node_id]['height'] = blocks[block_to_mine_on][0]
	nodes[node_id]['blocks'][blocks[block_to_mine_on][0]] = block_to_mine_on
	cur_height = nodes[node_id]['height']
	cur_block = block_to_mine_on
	# remove blocks out the window range (to save memory)
	hkeys = list(nodes[node_id]['blocks'].keys())
	hkeys = filter(lambda h: h < cur_height - WINDOW_LEN, hkeys)
	for h in hkeys:
		del nodes[node_id]['blocks'][h]
	# update blocks in the window range
	min_lim = max(cur_height - WINDOW_LEN, 1)
	while cur_height > min_lim:
		nodes[node_id]['blocks'][cur_height - 1] = blocks[cur_block][1]
		cur_block = blocks[cur_block][1]
		cur_height -= 1


def mine_block(node_id, longest_chains, tie_breaking_function, r):
	global num_blocks_mined_total
	global new_blocks_produced
	_ = random.uniform(0, 1)
	if _ > p:
		return
	block_to_mine_on = nodes[node_id]['blocks'][nodes[node_id]['height']]
	new_block_id = num_blocks_mined_total
	num_blocks_mined_total += 1
	new_blocks_produced += 1
	blocks[new_block_id] = (blocks[block_to_mine_on][0] + 1, block_to_mine_on, node_id, r)
	nodes[node_id]['blocks'][blocks[new_block_id][0]] = new_block_id
	nodes[node_id]['height'] = blocks[new_block_id][0]
	

def check_for_convergence():
	global max_convergence_height
	cur_conv_height = max_convergence_height + 1
	while True:
		conv_block_id = -1
		for i in range(0, n):
			if cur_conv_height not in nodes[i]['blocks']:
				return
			if conv_block_id == -1:
				conv_block_id = nodes[i]['blocks'][cur_conv_height]
			if conv_block_id != nodes[i]['blocks'][cur_conv_height]:
				return
		if conv_block_id == -1:
			return
		# print("height", str(cur_conv_height))
		# for i in range(n):
		# 	print(nodes[i]['blocks'])
		max_convergence_height = cur_conv_height
		cur_conv_height += 1


nb = []

def main():
	global new_blocks_produced
	prev_round_only_one_node_mined = 1
	random.seed(time.time())
	for r in range(1, MAX_ROUNDS + 1):
		longest_chains = get_longest_chains()
		if (r % 100 == 0):
			print("round ", r, "of", MAX_ROUNDS)
			# print(len(longest_chains))
		for i in range(n):
			# update_longest_chain(i, longest_chains, tie_break_by_random, r)
			update_longest_chain(i, longest_chains, tie_break_by_first_seen, r)
		check_for_convergence()
		consensus_height_by_round[r] = max_convergence_height
		for i in range(n):
			mine_block(i, longest_chains, tie_break_by_first_seen, r)
		nb.append(new_blocks_produced)
		if new_blocks_produced == 1:
			rounds_interval_only_one_node_mine.append(r)
			prev_round_only_one_node_mined = r
			# print("only one block mined at round ", r)
		new_blocks_produced = 0
		# print("round", str(r))
		# for i in range(n):
		# 	print(nodes[i]['blocks'])
		# print("")
	if len(rounds_interval_only_one_node_mine) == 0:
		print("There was never a round where only one node mined")
	else:
		print("average number of rounds it takes until only one node mines: ", MAX_ROUNDS / len(rounds_interval_only_one_node_mine))
	print("total number of blocks mined: ", num_blocks_mined_total)
	print("number of blocks in consensus: ", max_convergence_height)
	print("percentage discarded: ", 1 - max_convergence_height / num_blocks_mined_total)

	# for i in range(n):
	# 	print(nodes[i]['blocks'])
	plt.plot(range(1, MAX_ROUNDS + 1), consensus_height_by_round[1:])
	# plt.plot(range(1, MAX_ROUNDS + 1), nb[0:])
	plt.show()

if __name__ == '__main__':
	main()