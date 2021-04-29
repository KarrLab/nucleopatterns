from copy import deepcopy
import json, importlib.util
import yaml

from pathlib import Path

def flatten_dict(d):
	if not isinstance(d,dict):
		return d
	outd = dict()
	for k,v in d.items():
		v = flatten_dict(v)
		if isinstance(v,dict):
			for k1,v1 in v.items():
				outd[(k,*k1)] = v1
		else:
			outd[(k,)] = v
	return outd

def unflatten_dict(d):
	outd = dict()
	for k, v in d.items():
		priors, final = k[:-1], k[-1]
		refd = outd
		for k1 in priors:
			if (k1 in refd and not isinstance(refd[k1],dict)) or (k1 not in refd):
				refd[k1] = dict()
			refd = refd[k1]
		refd[final] = v
	return outd


def join_dicts(*dicts):
	# only one level of nesting
	return {k:v for d in dicts for k,v in d.items()}


class YamlUtil:
	@staticmethod
	def read(s):
		return yaml.load(s)

	@staticmethod
	def write(d):
		return yaml.dump(d,default_flow_style=False)

class JsonUtil:

	@staticmethod
	def read(s):
		return json.loads(s)

	@staticmethod
	def write(d):
		return json.dumps(d,indent=4)

class DataFileUtil:

	utils = {
		'yaml': YamlUtil,
		'json': JsonUtil
	}

	def __init__(self,folder='.'):
		self.folder = Path(folder)

	def read_file(self,filename,data_format=None):
		file = self.folder / filename
		if data_format is None:
			data_format = file.suffix[1:]
		txt = file.read_text()
		data = self.utils[data_format].read(txt)
		return data
		
	def write_file(self,data,filename,data_format=None):
		file = self.folder / filename
		if data_format is None:
			data_format = file.suffix[1:]
		txt = self.utils[data_format].write(data)
		if not self.folder.exists():
			self.folder.mkdir(parents=True)
		file.write_text(txt)
		return
