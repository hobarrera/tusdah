#!/usr/bin/env python2
# -*- coding: utf-8 -*-

# Copyright (c) 2012 Hugo Osvaldo Barrera <hugo@osvaldobarrera.com.ar>
#
# Permission todo use, copy, modify, and distribute this software for any
# purpose with or without fee is hereby granted, provided that the above
# copyright notice and this permission notice appear in all copies.
#
# THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES
# WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
# MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR
# ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
# WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN
# ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF
# OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.

import json, urllib, os, commands, tempfile, subprocess, sys, shutil
from xdg import BaseDirectory
from ConfigParser import SafeConfigParser

BASE_RPC_URL = "https://aur.archlinux.org/rpc.php"
BASE_PKG_URL = "https://aur.archlinux.org/"

EDITOR = os.environ.get('EDITOR', 'vi')

CONFIG_DIR = os.path.join(BaseDirectory.xdg_config_home, "tusdah/")
if not os.path.exists(CONFIG_DIR):
    os.makedirs(CONFIG_DIR)

CONFIG_FILE = os.path.join(CONFIG_DIR, "config")

if (len(sys.argv) < 2):
	print "Usage: tusdah PACKAGE_NAME"
	sys.exit(0)

def yesOrNo():
	answer = ""
	while answer != "y" and answer != "n":
		answer = raw_input()
	return answer == "y"

params = { "type" : "search", "arg": sys.argv[1] }
params = urllib.urlencode(params)

response = urllib.urlopen(BASE_RPC_URL + "?" + params).read()
response = json.loads(response, "UTF-8")

#print json.dumps(response, sort_keys=True, indent=4)

if response["type"] == "error":
	print "Sorry, I couldn't find anything. Bye!"
	sys.exit(0)

print "\033[1;37mLook at all the pretty packages I found for you!\033[1;m\n"

i = 0
for result in response["results"]:
	print str(i) + ") " + result["Name"] + " " + result["Version"]
	i += 1

print "\n\033[1;33mPick one!\033[1;m"

picked_one = raw_input()

package = response["results"][int(picked_one)]

tmpDir = tempfile.mkdtemp("-tusdah")
os.chdir(tmpDir)

srcPkgFileName = package["Name"] + ".tar.gz"

urllib.urlretrieve(BASE_PKG_URL + package["URLPath"], srcPkgFileName)[0]

print "\nExtracting source package..."
print commands.getoutput("tar xzvf " + srcPkgFileName)
os.chdir(os.path.join(tmpDir, package["Name"]))
print ""
#print commands.getoutput("makepkg -fsci")

print "\033[1;33mDo you want to review the PKGBUILD?\033[1;m"
line2 = "You really don't *need* to look at it.  "
line2 += "It's not like \033[1;37mI'm\033[1;m gonna source it anyway! \033[1;32m[y/n]\033[1;m"
print line2

if yesOrNo():
	cmd = EDITOR + ' ' + "PKGBUILD"
	subprocess.call(cmd, shell=True)

	print "Ok, can I build it now?"
	if not yesOrNo():
		print "\033[1;37mThat was boring. :( Bye then.\033[1;m\n"
		sys.exit(0)

#proc = subprocess.Popen(["makepkg","-fsci"], stdin=subprocess.PIPE, stdout=subprocess.PIPE)
subprocess.call("makepkg -fsci --noconfirm", shell=True)
#stdout, stderr = proc.communicate()

config = SafeConfigParser()
config.read(CONFIG_FILE)

def ask_repo_location():
	print "Where did you say your repo was?"
	return raw_input()	
def ask_repo_db():
	print "I'm quite positive you already told me where your repo db was, but could you repeat it just one more time?"
	return raw_input()	

if config.has_section("repo"):
	if config.has_option("repo", "location"):
		repo_location = config.get("repo", "location")
	else:
		repo_location = ask_repo_location()
	if config.has_option("repo", "db"):
		repo_db = config.get("repo", "db")
	else:
		repo_db = ask_repo_db()
else:
	repo_location = ask_repo_location()
	repo_db = ask_repo_db()


for aFile in os.listdir(os.getcwd()):
	if aFile.endswith(".pkg.tar.xz"):
		final_package = os.path.join(repo_location, aFile)
		os.rename(aFile, os.path.join(repo_location, aFile))
		break

print commands.getoutput("repo-add " + repo_db + " " + final_package)

print "Deleting tmp stuff..."
shutil.rmtree(tmpDir)
print "\033[1;37mThat was fun!  Bye!  :D\033[1;m"
