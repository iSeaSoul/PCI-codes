import sys

def print_dict(cdict, indent_num = 0):
	sys.stdout.write('{\n')
	for key, val in cdict.items():
		print_indent(indent_num + 1)
		print_val(key)
		sys.stdout.write(': ')
		print_obj(val, indent_num + 1)
		sys.stdout.write(',\n')
	print_indent(indent_num)
	sys.stdout.write('}')

def print_list(clist, indent_num):
	sys.stdout.write('[\n')
	for item in clist:
		print_indent(indent_num + 1)
		print_obj(item, indent_num + 1)
		sys.stdout.write(',\n')
	print_indent(indent_num)
	sys.stdout.write(']')

def print_obj(cobj, indent_num = 0, end = ''):
	if isinstance(cobj, dict):
		print_dict(cobj, indent_num)
	elif isinstance(cobj, list):
		print_list(cobj, indent_num)
	else:
		print_val(cobj)
	if end: sys.stdout.write(end)

def print_val(ckey):
	if isinstance(ckey, str):
		sys.stdout.write(str('\'' + ckey + '\'' ))
	elif isinstance(ckey, unicode):
		sys.stdout.write(str('u\'' + ckey + '\'' ))
	else:
		sys.stdout.write(str(ckey))

def print_indent(indent_num):
	for i in xrange(indent_num):
		sys.stdout.write('\t')

def my_print(cobj):
	# print tidy
	print_obj(cobj, end = '\n')

if __name__ == '__main__':
	a = [2, {1 : 2, 3 : 'a', 4 : {1 : 2, 2 : {1 : 2}}}]
	my_print(a)
	my_print([2, [1, {'2' : 3}]])