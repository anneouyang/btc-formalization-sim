from Sim import Sim
from matplotlib import pyplot as plt

def main():

	first_seen = []
	random = []
	sim_time = 100

	# N, P, R

	for i in range(sim_time):

		sr = Sim(100, 1, 100, "r")
		sf = Sim(100, 1, 100, "f")

		sr_res = sr.run()
		sf_res = sf.run()

		# print("random: ", sr_res)
		# print("first_seen: ", sf_res)
		first_seen.append(sf_res)
		random.append(sr_res)

		print("round: ", i)
		# print("first seen: ", sum(first_seen) / len(first_seen))
		# print(first_seen)
		# print("random: ", sum(random) / len(random))
		# print(random)

	print(first_seen)
	print(random)

	plt.scatter(range(sim_time),first_seen,color='red')
	plt.hlines(sum(first_seen) / len(first_seen), 0, sim_time, colors='red')
	plt.scatter(range(sim_time),random,color='blue')
	plt.hlines(sum(random) / len(random), 0, sim_time, colors='blue')
	plt.show()

if __name__ == '__main__':
	main()