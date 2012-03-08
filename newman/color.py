import sys

def with_color(string, color, bold):
    '''Returns string wrapped in ANSI color if terminal supports it.'''
    if not color_term(): return string
    
    c = color
    if bold:
        c = "1;%s" % c
    return "\033[%sm%s\033[0m" % (c, string)

def color_term():
    '''Returns boolean if term supports ANSI color.'''
    if hasattr(sys.stdout, "isatty") and sys.stdout.isatty():
        return True
    else:
        return False
    
# Red
def red(string, bold=None): 
    return with_color(string, 31, bold)

# Green
def green(string, bold=None):
    return with_color(string, 32, bold)

# Yellow
def yellow(string, bold=None):
    return with_color(string, 33, bold)

# Blue
def blue(string, bold=None):
    return with_color(string, 34, bold)

# Magenta
def magenta(string, bold=None):
    return with_color(string, 35, bold)

# Cyan
def cyan(string, bold=None):
    return with_color(string, 36, bold)

# White
def white(string, bold=None):
    return with_color(string, 37, bold)

