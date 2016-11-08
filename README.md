# HaveTheyBeenPwned
Modification of a script, it takes an input file (-i file.txt) containing email addresses and uses the HaveIBeenPwned API

# Usages Examples

Simplest method to seach for all emails in emails.txt and output the results to screen, no rate limit rule but if it hits the rate limit error that entry will be excluded from the results.
./HaveTheyBeenPwned.py -i emails.txt 

To search HIBP for all emails in emails.txt and output the results as seen on screen to found.txt, tries one entry from emails.txt every 1.6 seconds
./HaveTheyBeenPwned.py -i emails.txt -o found.txt -s 1.6

To search HIBP for all eamils in emails.txt and output the results to found.txt prefixing each line with a dash (-), tries one entry from emails.txt evert 1.6 seconds
./HaveTheyBeenPwned.py -i emails.txt -oR found.txt -s 1.6
