#!/usr/bin/env python

##
# HaveTheyBeenPwned, bulk HaveIBeenPwned scraper, this script is a modifcation of https://github.com/Techno-Hwizrdry/checkpwnedemails
##
__author__  = "Chris Burton"
__version__ = "1.2"

from argparse import ArgumentParser
from time     import sleep

import time
import json
import sys
import traceback
import urllib
import urllib2
import os.path

PWNED_API_URL = "https://haveibeenpwned.com/api/v2/%s/%s"
HEADERS = {"User-Agent": "havetheybeenpwned"}

EMAILINDEX = 0
PWNEDINDEX = 1
DATAINDEX  = 2

BREACHED = "breachedaccount"
PASTEBIN = "pasteaccount"

def indent(lines, amount, ch=' '):
    padding = amount * ch
    return padding + ('\n'+padding).join(lines.split('\n'))

class PwnedArgParser(ArgumentParser):
	def error(self, message):
		sys.stderr.write('error: %s\n' %message)
		self.print_help()
		sys.exit(2)


def get_args():
	parser = PwnedArgParser()

	parser.add_argument('-i', dest='input_path',   help='Path to text file that lists email addresses.')
	parser.add_argument('-o', dest='output_path',  help='Path to output to text file.')
	parser.add_argument('-oR', dest='output_path_report',  help='Path to output to text file in report ready format.')
	parser.add_argument('-s', dest='rate_limit_sleep',  help='Obey the rate limit of the API.')

	if len(sys.argv) == 1:  # If no arguments were provided, then print help and exit.
		parser.print_help()
		sys.exit(1)

	return parser.parse_args()

#  Used for removing the trailing '\n' character on each email.
def clean_list(list_of_strings):
	return [str(x).strip() for x in list_of_strings]

def get_results(email_list, service, opts):
	results = []  # list of tuples (email adress, been pwned?, json data)
	for email in email_list:
		email = email.strip()
		data = []
		req  = urllib2.Request(PWNED_API_URL % (urllib.quote(service), urllib.quote(email)), headers=HEADERS)

                try:
                	response = urllib2.urlopen(req)  # This is a json object.
                        data     = json.loads(response.read())
			results.append( (email, True, data) )
                except urllib2.HTTPError as e:
                        if e.code == 400:
				print "%s does not appear to be a valid email address.  HTTP Error 400." % (email)
			if e.code == 403:
				print "Forbidden - no user agent has been specified in the request.  HTTP Error 403."
                        if e.code == 404:
				results.append( (email, False, data) )
			if e.code == 429:
				print "Too many requests; going over the request rate limit, sleeping for 1.6 seconds."
				sleep (1.6)

		if opts.rate_limit_sleep:
			sleep(float(opts.rate_limit_sleep))

		#if not opts.output_path:
		try:
			last_result = results[-1]

			if not last_result[PWNEDINDEX]:
				if service == BREACHED:
					pass
				else:
					pass
			elif data:
				found_email = []
				last_item = 0
				sys.stdout.write(('%s (' % (email)))
				for i in data:
					found_email.append( i['Title'] )

				sys.stdout.write(','.join(found_email))
				sys.stdout.write(')')
				outputString = (('%s' %email + ' (' + ','.join(found_email) + ')\r'))
				sys.stdout.flush()
				print ''

				if opts.output_path:
					with open(opts.output_path, "a") as outputFile:
						outputFile.write(outputString)

				if opts.output_path_report:
					with open(opts.output_path_report, "a") as outputFile:
						outputFile.write("- "+ outputString)


		except IndexError:
			pass

	return results

def file_len(fname):
	with open(fname) as f:
		for ii, l in enumerate(f):
			ii + 1
			pass
	total_time = 1.6 * ii / 60
	print ('[+] ' + fname + ' will take approx ' + str(total_time) + ' minutes.')

#  This function will convert every item, in dlist, into a string and
#  encode any unicode strings into an 8-bit string.
def clean_and_encode(dlist):
	cleaned_list = []

	for d in dlist:
		try:
			cleaned_list.append(str(d))
		except UnicodeEncodeError:
			cleaned_list.append(str(d.encode('utf-8')))  # Clean the data.

	return cleaned_list

def write_results_to_file(filename, results, opts):
	pass

def main():
	email_list = []
	opts = get_args()

	file_len(opts.input_path)
	email_list_file = open(opts.input_path, 'r')
	email_list      = clean_list(email_list_file.readlines())

	email_list_file.close()

	if opts.output_path:
		print "[+] Saving to file " + str(opts.output_path)
	if opts.output_path_report:
		print "[+] Saving to file " + str(opts.output_path_report)
	if os.path.isfile(opts.input_path):
		print "[+] Querying HaveIBeenPwned!"

        results = []

	results.append(get_results(email_list, BREACHED, opts))
	results.append(get_results(email_list, PASTEBIN, opts))


	if opts.output_path:
		pass

if __name__ == '__main__':
	main()
