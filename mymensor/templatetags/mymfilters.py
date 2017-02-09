from django import template

register = template.Library()

@register.filter(name="lookupvpnumber")
def lookupvpnumber(value, key):
    try:
        return value.key
    except:
        return key


@register.filter(name="frommillistoseconds")
def frommillistoseconds(value):
    return int(value/1000)


class GlobalVariable( object ):
  def __init__( self, varname, varval ):
    self.varname = varname
    self.varval  = varval
  def name( self ):
    return self.varname
  def value( self ):
    return self.varval
  def set( self, newval ):
    self.varval = newval

class GlobalVariableSetNode( template.Node ):
  def __init__( self, varname, varval ):
    self.varname = varname
    self.varval  = varval
  def render( self, context ):
    gv = context.get( self.varname, None )
    if gv:
      gv.set( self.varval )
    else:
      gv = context[self.varname] = GlobalVariable( self.varname, self.varval )
    return ''
def setglobal( parser, token ):
  try:
    tag_name, varname, varval = token.contents.split(None, 2)
  except ValueError:
    raise template.TemplateSyntaxError("%r tag requires 2 arguments" % token.contents.split()[0])
  return GlobalVariableSetNode( varname, varval )
register.tag( 'setglobal', setglobal )

class GlobalVariableGetNode( template.Node ):
  def __init__( self, varname ):
    self.varname = varname
  def render( self, context ):
    try:
      return context[self.varname].value()
    except AttributeError:
      return ''
def getglobal( parser, token ):
  try:
    tag_name, varname = token.contents.split(None, 1)
  except ValueError:
    raise template.TemplateSyntaxError("%r tag requires arguments" % token.contents.split()[0])
  return GlobalVariableGetNode( varname )
register.tag( 'getglobal', getglobal )

class GlobalVariableIncrementNode( template.Node ):
  def __init__( self, varname ):
    self.varname = varname
  def render( self, context ):
    gv = context.get( self.varname, None )
    if gv is None:
      return ''
    gv.set( int(gv.value()) + 1 )
    return ''
def incrementglobal( parser, token ):
  try:
    tag_name, varname = token.contents.split(None, 1)
  except ValueError:
    raise template.TemplateSyntaxError("%r tag requires arguments" % token.contents.split()[0])
  return GlobalVariableIncrementNode(varname)
register.tag( 'incrementglobal', incrementglobal )