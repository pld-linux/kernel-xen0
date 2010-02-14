#!/usr/bin/python

# Update kernel.conf based on kernel .config file
# arekm@pld-linux.org
# glen@pld-linux.org

import sys
import re
from UserDict import UserDict

if len(sys.argv) != 4:
    print "Usage: %s target_arch kernel.conf .config" % sys.argv[0]
    sys.exit(1)

arch = sys.argv[1]
kernelconf = sys.argv[2]
dotconfig = sys.argv[3]

# odict (Ordered Dict) from http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/107747
class odict(UserDict):
    def __init__(self, dict = None):
        self._keys = []
        UserDict.__init__(self, dict)

    def __delitem__(self, key):
        UserDict.__delitem__(self, key)
        self._keys.remove(key)

    def __setitem__(self, key, item):
        UserDict.__setitem__(self, key, item)
        if key not in self._keys: self._keys.append(key)

    def clear(self):
        UserDict.clear(self)
        self._keys = []

    def copy(self):
        dict = UserDict.copy(self)
        dict._keys = self._keys[:]
        return dict

    def items(self):
        return zip(self._keys, self.values())

    def keys(self):
        return self._keys

    def popitem(self):
        try:
            key = self._keys[-1]
        except IndexError:
            raise KeyError('dictionary is empty')

        val = self[key]
        del self[key]

        return (key, val)

    def setdefault(self, key, failobj = None):
        UserDict.setdefault(self, key, failobj)
        if key not in self._keys: self._keys.append(key)

    def update(self, dict):
        UserDict.update(self, dict)
        for key in dict.keys():
            if key not in self._keys: self._keys.append(key)

    def values(self):
        return map(self.get, self._keys)

dict = odict()

rc = 0
f = open(kernelconf, 'r')
i = 0;
allarch = {}
for l in f:
    if l[:6] == 'CONFIG_':
        sys.stderr.write("Omit CONFIG_ when specifing symbol name: %s\n" % l)
        rc = 1
        continue

    if re.match('^#', l) or re.match('^\s*$', l):
        dict[i] = l.strip()
        i = i + 1
        continue

    if not re.match('^[0-9A-Z]+', l):
        sys.stderr.write("Unknown line: %s\n" % l)
        rc = 1
        continue

    c = l.strip().split()
    symbol = c[0]

    # inline symbol: for current arch, may override config one
    if symbol.find('=') > 0:
        (symbol, value) = symbol.split('=')

        if not dict.has_key(symbol):
            dict[symbol] = odict()

        dict[symbol][arch] = value
        continue

    if dict.has_key(symbol):
        sys.stderr.write("Duplicate symbol: %s\n" % symbol)
        rc = 1
        continue

    dict[symbol] = odict()
    for item in c[1:]:
        (key, value) = item.split('=')
        if not allarch.has_key(key):
            allarch[key] = 1
        dict[symbol][key] = value

#    sys.stderr.write("Add symbol: %s=%s\n" % (symbol, dict[symbol]))

f.close()

# not really an arch :)
if allarch.has_key('all'):
	del allarch['all']

if not rc == 0:
    sys.exit(1)

# read keys from .config
f = open(dotconfig, 'r')
dotdict = {}
for l in f:
    # 'y'es, 'm'odule and string, numeric values
    m = re.match("^CONFIG_(.*)=(.*)$", l)
    if not m == None:
        symbol = m.group(1)
        value = m.group(2)
    else:
        # no values
        m = re.match("^# CONFIG_(.*) is not set$", l)
        if not m == None:
            symbol = m.group(1)
            value = "n"
    # other irrelevant data
    if m == None:
        continue

    dotdict[symbol] = value
#    sys.stderr.write("Add .config symbol: %s=%s\n" % (symbol, dotdict[symbol]))

f.close()

dict[i] = ""
i += 1
dict[i] = "#"
i += 1
dict[i] = "# New symbols"
i += 1
dict[i] = "#"
i += 1

# compare kernel.conf and .config
# add new items to kernel.conf
for symbol in dotdict.keys():
    value = dotdict[symbol]
    if dict.has_key(symbol):
        c = dict[symbol]

        # if we have arch key, we use regardless there's 'all' present
        if c.has_key(arch):
            c[arch] = value
        elif c.has_key('all') and c['all'] != value:
            # new value from this arch
            c[arch] = value
        elif not c.has_key('all'):
            # symbol present in config.conf, but without our arch, add our value
            c[arch] = value

        dict[symbol] = c
    else:
        # new symbol gets by default assigned to 'all'
        c = {}
        c['all'] = value
        dict[symbol] = c
f.close()

# printout time
for symbol in dict.keys():
    c = dict[symbol]
#    sys.stderr.write("s=%s, c=%s\n" % (type(symbol), type(c)))
    if type(symbol) == int:
        # comments
        print c
        continue

    # go over symbols which no longer present in .config
    # and remove from our arch.
    if not dotdict.has_key(symbol):
        c = dict[symbol]
        if c.has_key('all') or c.has_key(arch):
            c[arch] = ''

    # blacklist
    # TODO: use some list here instead
    if symbol == "LOCALVERSION":
        # .specs updates this
        continue

    # join arch=value back into string
    s = ''
    for k in c.keys():
        s += ' %s=%s' % (k, c[k])

    print "%s %s" % (symbol, s.strip())
