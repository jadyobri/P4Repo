import pyhop
import json

def check_enough (state, ID, item, num):
	if getattr(state,item)[ID] >= num: return []
	return False

def produce_enough (state, ID, item, num):
	return [('produce', ID, item), ('have_enough', ID, item, num)]

pyhop.declare_methods ('have_enough', check_enough, produce_enough)

def produce (state, ID, item):
	return [('produce_{}'.format(item), ID)]

pyhop.declare_methods ('produce', produce)

def make_method (name, rule):
	
	priorityList = [
		"wood",
		"bench",
		"plank",
		"cobble",
		"ingot",
		"stick",
		"wooden_pickaxe",
		"furnace",
		"coal",
		"stone_pickaxe",
		"ore",
		"cart",
		"rail",
		"wooden_axe",
		"stone_axe",
		"iron_axe",
		"iron_pickaxe",
		]

	""" priorityList = [
		"wood",
		"plank",
		"bench",
		"stick",
		"wooden_axe",
		"wooden_pickaxe",
		"coal",
		"cobble",
		"furnace",
		"stone_axe",
		"stone_pickaxe",
		"ore",
		"ingot",
		"cart",
		"rail",
		"iron_axe",
		"iron_pickaxe",
		] """
	
	# priorityList.reverse()
	tempList = []

	if "Requires" in rule.keys():
		for requisite, value in rule["Requires"].items():
			tempList.append((requisite, value))

	if "Consumes" in rule.keys():
		for requisite, value in rule["Consumes"].items():
			tempList.append((requisite, value))
	
	tempList.sort(key=lambda x: priorityList.index(x[0]))
	# print(tempList)

	def method (state, ID):
		# your code here

		# return [('have_enough', ID, 'wood', 1), ('op_craft_plank', ID)]
		
		returnList = []
		if(len(tempList) > 0):
			returnList = [('have_enough', ID, req, val) for req, val in tempList]
		returnList.append(('op_{}'.format(name), ID))

		return returnList
	method.__name__ = format(name)
	return method

def declare_methods (data):
	# some recipes are faster than others for the same product even though they might require extra tools
	# sort the recipes so that faster recipes go first

	# your code here
	# hint: call make_method, then declare the method to pyhop using pyhop.declare_methods('foo', m1, m2, ..., mk)	
	#methods = []
	
	dictionary = {}
	timeDict = {}
	for name, rule in data["Recipes"].items():
		#make operator
		#print(rule)
		#make_operator(rule)

		production = next(iter(rule["Produces"]))
		newMethod = make_method(name, rule)
		timeDict[newMethod] = rule["Time"]
		if(production in dictionary.keys()):
			dictionary[production].append(newMethod)
		else:
			dictionary[production] = [newMethod]
		#methods.append(make_method(name, rule))
		#dictionary
	#timeDict["iron_pickaxe for ore"] = 20
	for key, value in dictionary.items():
		value.sort(key=lambda x: timeDict[x])
		pyhop.declare_methods('produce_{}'.format(key), *value)
	#for 
	#pyhop.declare_methods('produce_{}'.format(),operations)
	pass			

def make_operator (rule):
	name, recipe = rule

	# for requisite, value in recipe["Requires"].items():
	# 	print(requisite)
	# 	print(value)
	def operator (state, ID):
		
		if state.time[ID] < recipe["Time"]:
			return False
		
		if "Requires" in recipe.keys():
			for requisite, value in recipe["Requires"].items():
				if getattr(state, requisite)[ID] < value:
					return False

		if "Consumes" in recipe.keys():
			for requisite, value in recipe["Consumes"].items():
				if getattr(state, requisite)[ID] < value:
					return False
			
			for requisite, value in recipe["Consumes"].items():
				getattr(state, requisite)[ID] -= value

		for product, value in recipe["Produces"].items():
			getattr(state, product)[ID] += value

		state.time[ID] -= recipe["Time"]

		return state

	operator.__name__ = 'op_{}'.format(name)

	return operator

def declare_operators (data):
	# your code here
	# hint: call make_operator, then declare the operator to pyhop using pyhop.declare_operators(o1, o2, ..., ok)
	operations = []
	for rule in data["Recipes"].items():
		#make operator
		#print(rule)
		#make_operator(rule)
		operations.append(make_operator(rule))
	
	pyhop.declare_operators(*operations)
	pass

def add_heuristic (data, ID):
	# prune search branch if heuristic() returns True
	# do not change parameters to heuristic(), but can add more heuristic functions with the same parameters: 
	# e.g. def heuristic2(...); pyhop.add_check(heuristic2)
	def heuristic (state, curr_task, tasks, plan, depth, calling_stack):
		# your code here
		# return feasible if there is one
		# if heuristic that eliminates some branches
		# if you got a tool that produces wood, do not consider one that produces wood in same thought line
		# if you want

		# if the plan returns it, it knows the goal
		# reduced planning heuristic
		# brother goal clobers brother goal
		# mental search is calling stack

		# order what we need (not just given these tools)
		# brothers goals in any order
		# pyhop has line of get me methods of these tasks, cereally considers like selector in behavior tree going till first works
		# change would be let write heuristic to intercept that with one line change the pyhop.
		# slight bit of it here, set preference of iron over wood in some situation.
		# more dynamic one.  For this particular goal ...
		# just for pruning

		tools = ["bench",
			"furnace",
			"iron_axe",
			"iron_pickaxe",
			"stone_axe",
			"stone_pickaxe",
			"wooden_axe",
			"wooden_pickaxe"]

		if(len(calling_stack) <= 1):
			return False

		if(curr_task[0] == "have_enough"):
			state.enough[curr_task[2]] = curr_task[3]
		
		if(curr_task[0] == "produce"):

			if (getattr(state, curr_task[2])[ID] - 4 > state.enough[curr_task[2]]):
				return True

			if (curr_task[2] == "iron_pickaxe"):
				for task in tasks:
					if task[0] == "have_enough" and task[2] == "ingot":
						if task[3] < 7:
							state.prunes += 1
							print("prunes: ", state.prunes)
							return True
						return False
				return True

			if (curr_task[2] == "wooden_axe"):
				for task in tasks:
					if task[0] == "have_enough" and task[2] == "wood":
						if task[3] < 2:
							state.prunes += 1
							print("prunes: ", state.prunes)
							return True
						return False
				return True

			for task in calling_stack:
				if(task[0] == "produce" and task == curr_task and task[2] in tools):
					#print("got here")
					#print(calling_stack)
					#print(tasks)
					#print(curr_task)
					return True
		
		return False # if True, prune this branch

	pyhop.add_check(heuristic)


def set_up_state (data, ID, time=0):
	state = pyhop.State('state')
	state.time = {ID: time}

	for item in data['Items']:
		setattr(state, item, {ID: 0})

	for item in data['Tools']:
		setattr(state, item, {ID: 0})

	for item, num in data['Initial'].items():
		setattr(state, item, {ID: num})

	return state

def set_up_goals (data, ID):
	goals = []
	for item, num in data['Goal'].items():
		goals.append(('have_enough', ID, item, num))

	return goals

if __name__ == '__main__':
	rules_filename = 'crafting.json'

	with open(rules_filename) as f:
		data = json.load(f)

	state = set_up_state(data, 'agent', time=239) # allot time here
	goals = set_up_goals(data, 'agent')

	# my own stuff
	state.enough = {}
	state.prunes = 0

	declare_operators(data)
	declare_methods(data)
	add_heuristic(data, 'agent')

	# pyhop.print_operators()
	# pyhop.print_methods()

	# Hint: verbose output can take a long time even if the solution is correct; 
	# try verbose=1 if it is taking too long
	pyhop.pyhop(state, goals, verbose=1)
	# pyhop.pyhop(state, [('have_enough', 'agent', 'cart', 1),('have_enough', 'agent', 'rail', 20)], verbose=3)
	#pyhop.pyhop(state, [('have_enough', 'agent', 'wood', 1)], verbose=3)
