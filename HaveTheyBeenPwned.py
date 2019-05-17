#!/usr/bin/env python

##
# HaveTheyBeenPwned, bulk HaveIBeenPwned scraper, this script is a modifcation
# of https://github.com/Techno-Hwizrdry/checkpwnedemails
##
__author__ = "Chris Burton"
__author__ = "Paul Williams"
__version__ = "1.4"

from argparse import ArgumentParser
from time import sleep

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
DATAINDEX = 2

BREACHED = "breachedaccount"
PASTEBIN = "pasteaccount"

# simple terminal colour


class term_colour:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def print_message(colour, bullet_point, message):
    print colour + "[" + bullet_point + "] " + term_colour.ENDC + message


def print_debug(message):
    print_message(term_colour.OKBLUE, "i", message)


def print_info(message):
    print_message(term_colour.OKGREEN, "+", message)


def print_warning(message):
    print_message(term_colour.FAIL, "!", message)


def indent(lines, amount, ch=' '):
    padding = amount * ch
    return padding + ('\n'+padding).join(lines.split('\n'))


class PwnedArgParser(ArgumentParser):
    def error(self, message):
        sys.stderr.write('error: {0}\n'.format(message))
        self.print_help()
        sys.exit(2)


def get_args():
    parser = PwnedArgParser()
    parser.add_argument('-i', dest='input_path', help='Path to text file that lists email addresses.')
    parser.add_argument('-o', dest='output_path', help='Path to output to text file.')
    parser.add_argument('-oR', dest='output_path_report', help='Path to output to text file in report ready format.')
    parser.add_argument('-s', dest='rate_limit_sleep', help='Set a wait time between each request (seconds). Default of 1.6 seconds - set to 0 for no wait.', default=1.6, type=float)
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
        req = urllib2.Request(PWNED_API_URL % (urllib.quote(service), urllib.quote(email)), headers=HEADERS)
        try:
            response = urllib2.urlopen(req)  # This is a json object.
            data = json.loads(response.read())
            results.append((email, True, data))
        except urllib2.HTTPError as e:
            if e.code == 400:
                print_warning("{0} does not appear to be a valid email address. HTTP Error 400.".format(email))
            if e.code == 403:
                print_warning("Forbidden - no user agent has been specified in the request.  HTTP Error 403.")
            if e.code == 404:
                results.append((email, False, data))
            if e.code == 429:
                print_warning("Too many requests; going over the request rate limit, sleeping for 1.6 seconds.")
            sleep(1.6)

        if opts.rate_limit_sleep:
            sleep(float(opts.rate_limit_sleep))

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
                for i in data:
                    found_email.append(i['Title'])
                    found_in_list = ', '.join(found_email)
                    # This is what gets put into the file
                    output_string = ("{0} ({1})\r\n".format(email, found_in_list))

                print_debug("found_email:{}".format(found_email))
                print_debug("email:{0}\r\nFound in list{1}".format(email, found_in_list))
                print_warning("{0} ({1})".format(email, found_in_list))

                if opts.output_path:
                    with open(opts.output_path, "a") as output_file:
                        output_file.write(output_string)

                if opts.output_path_report:
                    with open(opts.output_path_report, "a") as output_file:
                        output_file.write("- " + output_string)

        except IndexError:
            pass

    return results


def file_len(fname, sleeptime):
    with open(fname) as f:
        for ii, l in enumerate(f):
            ii + 1
            pass

    total_time = sleeptime * ii / 60
    print_info("{0} will take approx {1} minutes.".format(fname, str(total_time)))


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

    file_len(opts.input_path, opts.rate_limit_sleep)
    email_list_file = open(opts.input_path, 'r')
    email_list = clean_list(email_list_file.readlines())
    email_list_file.close()

    if opts.output_path:
        print_info("Saving to file {0}".format(str(opts.output_path)))
    if opts.output_path_report:
        print_info("Saving to file {0}".format(str(opts.output_path_report)))
    if os.path.isfile(opts.input_path):
        print_info("Querying HaveIBeenPwned!")
        results = []

    results.append(get_results(email_list, BREACHED, opts))
    results.append(get_results(email_list, PASTEBIN, opts))
    if opts.output_path:
        pass
    print_info("Finished!")


if __name__ == '__main__':
    main()
