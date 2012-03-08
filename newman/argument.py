from decorators import task

class Argument(object):
  """Used to compose the exposed API via the @expose decorator
  """
  # The following attributes are the only ones allowed on an Argument
  __slots__ = ('name', 'datatype', 'description', 'example', 'required',
      'choices', 'default')

  def __init__(self, name, datatype, description=None, example=None, required=True, 
               choices=None, default=None):
    self.name = name
    self.datatype = datatype
    self.description = description
    self.example = example
    self.required = bool(required)
    self.choices = choices
    self.default = default

    if not description:
      self.description = "N/A"

  def __lt__(self, other_arg):
    return self.name < other_arg.name

  def __repr__(self):
    """Pretty print out of pertinent info on this argument
    """
    chunks = [u'<Argument ']
    if self.required:
      chunks.append(u'REQ ')
    else:
      chunks.append(u'OPT ')
    chunks.append(u"'%s' " % self.name)
    if isinstance(self.datatype, (list, tuple)):
      chunks.append(u" or ".join([t.__name__ for t in self.datatype]))
      chunks.append(u' ')
    else:
      chunks.append(u"%s " % self.datatype.__name__)
    #chunks.append(u"%s " % self.description[:25]) # up to 25 chars worth

    if self.default is not None:
      chunks.append(u"default:%s " % self.default)

    if hasattr(self, 'value'):
      chunks.append(u'VAL:%s' % self.value)

    #if self.example:
    #  chunks.append(u'(e.g. %s)' % self.example)
    chunks.append(u'>')
    return "".join(chunks)

  def parser_args(self):
    return dict(
      type=self.datatype,
      help=self.description,
      required=self.required,
      default=self.default
    )
