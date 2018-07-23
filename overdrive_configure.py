
import sys
import os
import os.path
import hashlib
import json
import argparse
import re
from pprint import pprint

exit_codes = {
	"config_file_nexits":1,
	"profile_overwrite": 2
}

def parse_adapter(i, info, info_len):
	''' buscar "Adapter" '''
	words = [
		"Adapter",
		"Asic Family",
		"Flash Type",
		"Product Name is",
		"Bios Config File",
		"Bios P/N is",
		"Bios Version",
		"Bios Date is",
		"ROM header contents",
		"Signature",
		"PCIR offset",
		"PCI Data Structure",
		"Signature",
		"Vendor ID",
		"Device ID",
		"PCI Revision",
		"Image size",
		"Code revision",
		"Indicator",
		"Code type",
		"Legacy BIOS File Name",
		"Legacy BIOS Part Number",
		"Legacy BIOS Build Number",
		"Legacy BIOS Change List",
		"Binary BIOS_IDTF",
		"ByteCheckSum"
	]


	adapter_info = {
		"serial_number": "",
		"number" :			 "Not present",
		"asic_family" :		 "Not present",
		"flash_type" :		 "Not present",
		"product_name" :	 "Not present",
		"bios_config_file" : "Not present",
		"bios_pn" :			 "Not present",
		"bios_version" : 	 "Not present",
		"bios_date" :		 "Not present",	
		"rom_header": {
			"signature" :	 "Not present",
			"pcir_offset":   "Not present"
		},
		"pci_data" : {
			"signature" :	"Not present",
			"vendor_id" :   "Not present",
			"device_id" :	"Not present", 
			"pci_revision": "Not present", 
			"image_size": 	"Not present",
			"code_revision": "Not present",
			"indicator": "Not present",
			"code_type": "Not present"
		},
		"legacy_bios_file_name": "Not present",
		"legacy_bios_part_number": "Not present",
		"legacy_bios_build_number": "Not present",
		"legacy_bios_change_list": "Not present",
		"binary_bios_idtf": "Not present",
		"byte_check_sum": "Not present"

	};

	rom_header 	= False
	pci_data 	= False
	''' Tratado como si la lista de palabras estuviera ordenada segun aparecen'''
	for word in words:
		i , found = find_word(i, info, info_len, word)
		if found == False :
			return {}, i, True

		if word == 'Adapter' :
			adapter_info["number"] = info[i].split(' ')[2]
		elif word == "Asic Family" :
			adapter_info["asic_family"] = info[i].split(' :')[1].strip(" \n")
		elif word == "Flash Type" :
			adapter_info["flash_type"] = info[i].split(' :')[1].strip(" \n")
		elif word == "Product Name is" :
			adapter_info["product_name"] = info[i].split(' :')[1].strip(" \n")
		elif word == "Bios Config File" :
			adapter_info["bios_config_file"] = info[i].split(':')[1].strip(" \n")
		elif word == "Bios P/N is" :
			adapter_info["bios_pn"] = info[i].split(' :')[1].strip(" \n")
		elif word == "Bios Version" :
			adapter_info["bios_version"] = info[i].split(' :')[1].strip(" \n")
		elif word == "Bios Date is" :
			adapter_info["bios_date"] = info[i].split(' :')[1].strip(" \n")
		elif word == "ROM header contents" :
			rom_header = True
			pci_data = False
		
		elif word == "Signature" and rom_header==True:
			adapter_info['rom_header']["signature"] = info[i].replace(word, "").strip(" \n")
		elif word == "PCIR offset" and rom_header:
			adapter_info['rom_header']["pcir_offset"] = info[i].replace(word, "").strip(" \n")
		elif word == "PCI Data Structure" :
			rom_header = False
			pci_data = True
		elif word == "Signature" and pci_data:
			adapter_info["pci_data"]["signature"] = info[i].replace(word, "").strip(" \n")
		elif word == "Vendor ID" and pci_data:
			adapter_info["pci_data"]["vendor_id"] = info[i].replace(word, "").strip(" \n")
		elif word == "Device ID" and pci_data:
			adapter_info["pci_data"]["device_id"] = info[i].replace(word, "").strip(" \n")
		elif word == "PCI Revision" and pci_data:
			adapter_info["pci_data"]["pci_revision"] = info[i].replace(word, "").strip(" \n")
		elif word == "Image size" and pci_data:
			adapter_info["pci_data"]["image_size"] = info[i].replace(word, "").strip(" \n")
		elif word == "Code revision" and pci_data:
			adapter_info["pci_data"]["code_revision"] = info[i].replace(word, "").strip(" \n")
		elif word == 'Indicator' and pci_data :
			adapter_info["pci_data"]["indicator"] = info[i].replace(word, "").strip(" \n")
		elif word == "Code type" and pci_data:
			adapter_info["pci_data"]["code_type"] = info[i].replace(word, "").strip(" \n")
		elif word == "Legacy BIOS File Name" :
			rom_header = False
			pci_data = False 
			adapter_info["legacy_bios_file_name"] = info[i].replace(word, "").strip(" \n")
		elif word == "Legacy BIOS Part Number" : 
			adapter_info["legacy_bios_part_number"] = info[i].replace(word, "").strip(" \n")
		elif word == "Legacy BIOS Build Number" : 
			adapter_info["legacy_bios_build_number"] = info[i].replace(word, "").strip(" \n")
		elif word == "Legacy BIOS Change List" : 
			adapter_info["legacy_bios_change_list"] = info[i].replace(word, "").strip(" \n")
		elif word == "Binary BIOS_IDTF" :         
			adapter_info["binary_bios_idtf"] = info[i].replace(word, "").strip(" \n")
		elif word == "ByteCheckSum" :             
			adapter_info["byte_check_sum"] = info[i].replace(word, "").strip(" \n")
	


	prod_output = os.popen("atiflash_284\AtiFlash.exe -prod " + adapter_info["number"]).readlines()

	match_result = re.search('Production Serial Number: (.+)\n', prod_output[0], flags=re.IGNORECASE)

	if (match_result != None) :
		adapter_info["serial_number"] = match_result.group(1)

	adapter_info["number"] = str(int(adapter_info["number"]) + 1)

	return adapter_info, i, False



def find_word(i, info, info_len, word):
	found = False
	while (found == False and i < info_len):
		if info[i].find(word) > -1 :
			found = True
		else :
			i = i+1

	return i, found	

def sha256(input) :
	m = hashlib.sha256()
	m.update(input.encode())
	return m.hexdigest()

def overdrive_current() :
	info = os.popen("overdrive\OverdriveNTool.exe -getcurrent").readlines()
	overdrive_info = {}
	i = 0
	for element in info:
		config_list = element.split('|')
		pos = config_list[0].split(':')[0]
		if pos == '0' :
			continue
		config = [
			"[Profile_" + str(i) + ']',
			"Name=gpu" + pos 
		];
		for x in range(1,len(config_list)):
			config.append(config_list[x].strip(" \r\n"))
		overdrive_info[pos] = config

		i = i + 1

	return overdrive_info

def atiflash_ai():

	'''wmic PATH Win32_VideoController GET Description,PNPDeviceID'''

	info = os.popen("atiflash_284\AtiFlash.exe -ai").readlines()
	info_len = len(info)
	i = 0
	gpu_list = []
	gpu_profiles = []
	gpu_pos = 1;
	while (i < info_len):

		adapter, i, error = parse_adapter(i, info, info_len)
		if error == True :
			continue

		serial_number = adapter["serial_number"]
		if (serial_number != "") :

			gpu_hash_data = {
				"serial_number": serial_number,
		  		"asic_family": adapter["asic_family"],
				"flash_type": adapter["flash_type"],
				"product_name": adapter["product_name"],
				"bios_config_file": adapter["bios_config_file"],
				"bios_pn": adapter["bios_pn"],
				"bios_version": adapter["bios_version"],
				"bios_date": adapter["bios_date"],
				"pci_data": {
					"signature": adapter["pci_data"]["signature"],
				    "vendor_id": adapter["pci_data"]["vendor_id"],
				    "device_id": adapter["pci_data"]["device_id"],
				    "pci_revision": adapter["pci_data"]["pci_revision"],
				    "image_size": adapter["pci_data"]["image_size"],
				    "code_revision": adapter["pci_data"]["code_revision"],
				    "indicator": adapter["pci_data"]["indicator"],
				    "code_type": adapter["pci_data"]["code_type"]
				 },
				"legacy_bios_file_name": adapter["legacy_bios_file_name"],
				"legacy_bios_part_number": adapter["legacy_bios_part_number"],
				"legacy_bios_build_number": adapter["legacy_bios_build_number"],
				"legacy_bios_change_list": adapter["legacy_bios_change_list"],
				"binary_bios_idtf": adapter["binary_bios_idtf"]
			}	


			gpu_hash = sha256(json.dumps(gpu_hash_data))
			hash_error = 0
		else :
			gpu_hash = None
			hash_error = 1

		adapter["hash"] = gpu_hash
		adapter["hash_error"] = hash_error
		adapter["hash_error_msg"] = get_hash_error(hash_error).replace("{gpu_number}", str(gpu_pos)) 

		if serial_number != "" :
			gpu = {
				"profile" : "gpu" + str(gpu_pos),
				"serial_number": serial_number,
				"hash": gpu_hash,
			}
			gpu_profiles.append(gpu)

		gpu_list.append(adapter)
		gpu_pos = gpu_pos + 1

	return {"adapters": gpu_list , "profiles": gpu_profiles}


def get_hash_error(error_num) :
	error_msg = ""
	if error_num == 1 :
		error_msg = "GPU[{gpu_number}] has not \"Production Serial Number\" please see: atiflash -prod"  
	return error_msg

def cmd_info() :
	gpu_info = atiflash_ai()
	info = json.dumps(gpu_info["adapters"], sort_keys=False, indent=4, separators=(',', ': '))
	print(info)

def cmd_profile(args):

	if os.path.isfile(args["profile"]) :
		response = ""
		i = 0
		while i < 3 and response[0:1] != "y" and response[0:1] != "n" :
			response = input("File \"" + args["profile"] + "\" exist. Overwrite yes(y) or no(n) :")
			i = i + 1

		if response == 'n':
			sys.exit(exit_codes["profile_overwrite"])
		elif response != "y":
			print("Incorrect answer")
			sys.exit(exit_codes["profile_overwrite"]) 

	print("Getting GPU info")
	gpu_info = atiflash_ai()


	if len(gpu_info["adapters"]) != len(gpu_info["profiles"]) :
		for adapter in gpu_info["adapters"]:
			print(adapter["hash_error_msg"])

	gpu_map = get_hash_index(gpu_info["adapters"])
	profile_map = get_hash_index(gpu_info["profiles"])

	print("Getting OverdriveNTool info")
	overdrive_info = overdrive_current()

	profiles = []

	for key in gpu_map:
		gpu = gpu_map[key]
		number = gpu["number"]
		if number in overdrive_info and key in profile_map :
			profile = profile_map[key]
			if profile["bad"] == False :
				del profile["bad"]
				profile["overdrive_config"] = overdrive_info[number]
				profiles.append(profile)


	info = json.dumps(profiles, sort_keys=False, indent=4, separators=(',', ': '))


	print("Saving profile in " + args["profile"])
	f = open(args["profile"], 'w')
	f.write(info)
	f.close()


def get_hash_index(elements) :
	hash_map = {}
	for item in elements:
		if item["hash"] not in hash_map :
			hash_map[item["hash"]] = item
			hash_map[item["hash"]]["bad"] = False
		else :
			hash_map[item["hash"]]["bad"] = True
	return hash_map
		

def cmd_configure(args, execute = True) :

	''' UTF-16 LE '''
	# fp = open("overdrive\OverdriveNTool_2.ini",'rb')
	# ret = fp.read(-1)
	
	# print([ret.decode('utf-16-le')])
	
	# sys.exit(0)

	if execute == True  :
		filename = args["configure"]
	else :
		filename = args["test"]

	if not os.path.isfile(filename) :
		print("file \"" + filename + "\" not exist")
		exit(exit_codes["config_file_nexits"])


	print("Getting GPU info")
	gpu_info = atiflash_ai()

	print("Getting profile")
	with open(filename) as data_file:    
	    profiles = json.load(data_file)
	

	gpu_len = len(gpu_info["adapters"])

	gpu_map = get_hash_index(gpu_info["adapters"])
	
	cmd_list = ["overdrive\OverdriveNTool.exe"];

	profile_map = get_hash_index(profiles)
	

	overdrive_config = []

	print("Generting config")
	for key in profile_map :

		profile = profile_map[key]
		
		if profile["hash"] not in gpu_map : 
			print("skip(Not found GPU): " +  profile["hash"])
			continue
       
		if profile["bad"] == True :
			print("skip(repeated profile please check "+ filename +"): " + profile["hash"])
			continue

		gpu = gpu_map[profile["hash"]]

		if (gpu["bad"] == True) :
			print("skip(not unique): " + profile["hash"])
			continue 


		number = gpu["number"]
		if gpu_len >= 10 and len(number) == 1 :
			number = "0" + number

		pname = profile["profile"]
		''' -r1 -p1"gpu1" '''
		cmd_list.append("-r"+ number + " -p" + number +"\"" + pname + "\"")

		overdrive_config.append("\n".join(profile["overdrive_config"]))

		del gpu_map[profile["hash"]]

	for key in gpu_map:
		gpu = gpu_map[key]
		print("skip(Not found Profile): " + gpu["hash"])
		continue

	overdrive_config_str = "\n\n".join(overdrive_config)
	general = "\n".join(["[General]","MainWindowLeft=338","MainWindowTop=264"])
	overdrive_config_str = overdrive_config_str + "\n" + "\n" + general
	
	if execute == True :
		print("Saving OverdriveNTool.ini")
		f = open("overdrive\OverdriveNTool.ini", 'w', encoding="utf-16-le")
		f.write('\ufeff')
		f.write(overdrive_config_str)
		f.close()

	if len(cmd_list) > 1 :
		cmd_exec = " ".join(cmd_list)
		print("Execute: " + cmd_exec)
		if execute == True :
			os.system(cmd_exec)
	else :
		print("No profiles to apply")



def main():

	parser = argparse.ArgumentParser(prog="overdrive_configure.py",description='Configure amd gpu with overdrive',usage='%(prog)s [options]')
	
	parser.add_argument('--info', nargs='?',const='all', help='Usage: Get gpu info')
	parser.add_argument('--profile', help='Usage: Export profile to file ej: --profile filename')
	parser.add_argument('--test', help='Usage: Configure amd with profile file: --test filename')
	parser.add_argument('--configure', help='Usage: Configure amd with profile file: --configure filename')

	args = vars(parser.parse_args())

	if args["info"]:
		cmd_info()
	elif args["profile"] :
		cmd_profile(args)
	elif args["configure"] :
		cmd_configure(args, True)
	elif args["test"] :
		cmd_configure(args, False)
	else :
		parser.print_help()

	sys.exit(0)

''' Main ''' 
main()
