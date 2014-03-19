from flask import Flask
app = Flask(__name__)

import ConfigParser
cp = ConfigParser.ConfigParser()

class DummyGlobalSectionHead(object):
    '''
    Useful to a dummy global section on top of an ini file so that it is
    parsable via ConfigParser.
    '''
    def __init__(self, fp):
        self.fp = fp
        self.sechead = '[global]\n'
    def readline(self):
        if self.sechead:
            try: return self.sechead
            finally: self.sechead = None
        else: return self.fp.readline()


def sections_as_dict(cp):
    '''
    Returns all the sections as a dictionary.
    '''
    d = dict(cp._sections)
    for section in d:
        for opt in d[section]:
            if opt != '__name__':
                d[section][opt] = cp.get(section, opt)
        d[section] = dict(cp._defaults, **d[section])
        d[section].pop('__name__', None)
    return d


cp.readfp(DummyGlobalSectionHead(open('rsyncd-osl.conf')))

# Get all the sections in the rsyncd config file.
sections = sections_as_dict(cp)

# Get all the modules in the rsyncd config file.
modules = sections.keys()

# To get items of a global section.
# global_items = cp.items('global')


@app.route("/")
def hello():
    return "Hello World!"

if __name__ == "__main__":
    app.run()
