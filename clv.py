"""Main file for CLV."""
import click
import json
import re
import configparser
import appdirs
import os
from random import randint


class Config(object):
  """A global configuration class.

  Set at initialization, before subcommands are called.
  """

  def __init__(self):
    """Use empty init for configuration."""
    self.db = None

pass_config = click.make_pass_decorator(Config, ensure=True)  # ensure=True to set Config on first use
echo        = click.echo
nums        = '①②③④⑤⑥⑦⑧⑨⑩'
cfg         = configparser.ConfigParser()
_dir        = appdirs.AppDirs('clv','parry.cadwallader')

if os.path.exists('config.ini'):
  cfg_loc = 'config.ini'
else:
  cfg_loc = os.path.join(_dir.user_data_dir, 'config.ini')

if os.path.exists('main.clvdb'):
  db_loc = 'main.clvdb'
else:
  db_loc = os.path.join(_dir.user_data_dir, 'main.clvdb')

# in local dev mode
if os.path.exists(cfg_loc):
  cfg.read(cfg_loc)
else:
  cfg['config'] = {}
  cfg['config']['lang'] = 'xx'
  os.makedirs(_dir.user_data_dir)
  with open(cfg_loc, 'w+') as configfile:
    cfg.write(configfile)
  open(db_loc, 'a').close()

lang = cfg['config']['lang']


@click.group()
@click.option('--input', type=click.File(), default=db_loc, help='Location of clvdb to be used')
@click.option('--output', type=click.File('w', atomic=True), default=db_loc,
              help='Location of clvdb to be used')  # atomic=True means don't ovewrite on open
@click.option('--verbose', is_flag=True, help='Turn on verbose mode')
@click.option('--lang', help='Language of the entry', default=lang)
@click.version_option()
@pass_config
def cli(config, input, output, verbose, lang):
  """A CLI for all your vocab needs."""
  config.input   = input
  config.output  = output
  config.verbose = verbose
  config.data    = _load(input)
  config.lang    = lang


@cli.command()
@click.argument('word')
@click.argument('definition', required=False)
@click.option('--add_defintion', help='Add an additional definition,\
                                       otherwise the main definition will be overwritten',
                                 is_flag=True)
@pass_config
def add(config, word, definition, add_defintion):
  """Add a word to the clvdb."""
  data   = config.data

  entry = {'word':word
          ,'lang':config.lang
          ,'definitions':[definition]
          ,'tags':[]
          ,'examples':[]}
  data.append(entry)
  echo('Successfully added {}!'.format(word))
  if config.verbose:
    echo(json.dumps(entry))
  _save(data, config)


@cli.command()
@click.argument('word')
@click.argument('definition')
@click.option('--def_id', help='Number of definition to edit.', default=-1)
@click.option('-a', help='Add an additional definition,\
                          otherwise the main definition will be overwritten',
                          is_flag=True)
@pass_config
def edit(config, word, definition, def_id, a):
  """Edit a word in the clvdb."""
  if a and def_id != -1:
    echo('Cannot add and edit an entry at the same time.')
    return False

  if def_id <= 0:
    echo('Must select a valid definition number.')
    return False

  data   = config.data
  lang   = config.lang
  rec_id = _find(data, word, lang)

  if rec_id == -1:
    echo('Could not find entry.')
    return False

  if config.verbose:
    echo('Before:')
    echo(json.dumps(data[rec_id]))

  if a:
    data[rec_id]['definitions'].append(definition)
  else:
    try:
      # 1 indexed to match the terminal output
      data[rec_id]['definitions'][def_id - 1] = definition
    except:
      echo('{} only has {} definitions.'.format(data[rec_id]['word'], len(data[rec_id]['definitions'])))
      return False

  echo('Successfully edited {}!'.format(word))
  if config.verbose:
    echo('After:')
    echo(json.dumps(data[rec_id]))
  _save(data, config)


@cli.command()
@click.argument('word')
@click.argument('tag')
@pass_config
def tag(config, word, tag):
  """Tag a word in the clvdb."""
  data   = config.data
  lang   = config.lang
  rec_id = _find(data, word, lang)
  data[rec_id]['tags'].append(tag)
  echo('Added tag to {}'.format(word))
  if config.verbose:
    echo(json.dumps(data[rec_id]))
  _save(data, config)


@cli.command()
@click.argument('word')
@click.argument('tag')
@pass_config
def untag(config, word, tag):
  """Remove a tag from a word in the clvdb."""
  data   = config.data
  lang   = config.lang
  rec_id = _find(data, word, lang)
  tags   = data[rec_id]['tags']
  data[rec_id]['tags'] = [t for t in tags if t != tag]
  echo('Removed tag from {}'.format(word))
  if config.verbose:
    echo(json.dumps(data[rec_id]))
  _save(data, config)


@cli.command()
@click.argument('word')
@click.argument('example')
@pass_config
def example(config, word, example):
  """Add an example to an entry."""
  data   = config.data
  lang   = config.lang
  rec_id = _find(data, word, lang)
  data[rec_id]['examples'].append(example)
  echo('Added example to {}'.format(word))
  if config.verbose:
    echo(json.dumps(data[rec_id]))
  _save(data, config)


@cli.command()
@click.argument('lang', required=False)
@click.option('-t', help='Display tags', is_flag=True)
@click.option('--tags', help='Filter by tags (comma separated)')
@pass_config
def list(config, lang, t, tags):
  """List words in the DB."""
  data = config.data
  if tags:
    tags = tags.split(',')
  word_size = 10
  echo('{} | {} | {}'.format('entry'.ljust(word_size), 'lang', 'definition'))
  echo('{}-+-{}-+--------------'.format('-'.ljust(word_size, '-'), '-'.ljust(4, '-')))
  for d in data:
    if lang is None or d['lang'] == lang:
      # if tags are being filtered on, pass if entry isn't tagged with the tag
      if tags and not set(tags).issubset(d['tags']):
        continue
      definitions = _build_definitions(d['definitions'], word_size)
      echo('{} | {} | {}'.format(d['word'].ljust(word_size), d['lang'].ljust(4), definitions))
      if t and d['tags']:
        _tags = ['#{}'.format(tag) for tag in d['tags']]
        echo(', '.join(_tags))


@cli.command()
@click.argument('word')
@click.argument('lang', required=False)
@click.option('--show_cloze', help='Shows text marked as a cloze if enabled', is_flag=True)
@pass_config
def lookup(config, word, lang, show_cloze):
  """Look up a single word from the DB."""
  data   = config.data
  rec_id = _find(data, word, lang)
  entry  = data[rec_id]
  echo('{} ({})'.format(word, lang))
  for idx, d in enumerate(entry['definitions']):
    echo('{} {}'.format(nums[idx], d))

  for e in entry['examples']:
    if not show_cloze:
      e = e.replace('{','').replace('}','')
    echo(e)

  if entry['tags']:
    _tags = ['#{}'.format(tag) for tag in entry['tags']]
    echo(', '.join(_tags))


@cli.command()
@pass_config
def cloze(config):
  """Get a random cloze from the DB."""
  data    = config.data
  clozes  = []
  success = False
  for d in data:
    for e in d['examples']:
      if '{' in e:
        clozes.append(e)
  cloze = clozes[randint(0, len(clozes) - 1)]
  ans   = re.search(r'\{(.*?)\}', cloze)
  if ans:
    ans = ans.group(1)
  cloze = re.sub(r'\{.*?\}','{...}', cloze)
  echo(cloze)
  while not success:
    val = click.prompt('Answer')
    if val == ans:
      success = True
      echo('Correct!')
    else:
      echo('Try again.')


@cli.command()
@click.argument('word')
@pass_config
def delete(config, word):
  """Delete an entry from the clvdb."""
  data   = config.data
  rec_id = _find(data, word, config.lang)
  entry  = data.pop(rec_id)

  echo('Successfully deleted {}!'.format(word))
  if config.verbose:
    echo(json.dumps(entry))
  _save(data, config)


@cli.command()
@click.argument('key')
@click.argument('value')
def set(key, value):
  """Set a configuration value."""
  cfg['config'][key] = value
  with open('config.ini', 'w') as configfile:
    cfg.write(configfile)


@cli.command()
@pass_config
def config(config):
  """Display current configuration of clv."""
  echo('lang:{}'.format(config.lang))
  echo('db:{}'.format(config.input.name))
  echo('config:{}'.format(cfg_loc))


######################
# INTERNAL FUNCTIONS #
######################


def _save(data, config):
  echo(json.dumps(data), file=config.output)


def _load(input):
  # create new db if no JSON to load
  try:
    data = json.load(input)
  except:
    data = []
  return data


def _find(data, word, lang):
  """Return record index of an entry."""
  rec_id = -1
  for idx, d in enumerate(data):
    if d['word'] == word and d['lang'] == lang:
      rec_id = idx
  return rec_id


def _build_definitions(definitions, offset):
  out  = []
  padding = 0
  for idx, d in enumerate(definitions):
    if not d:
      continue
    if idx != 0:
      padding = offset + 10
    out.append('{}{} {}'.format(' ' * padding, nums[idx], d))
  return '\n'.join(out)
