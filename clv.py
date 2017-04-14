"""Main file for CLV."""
import click
import json

# options are optional, duh
# arguments are mandatory and they come after the options
# @click.option('--word', help='Word to add to DB')
# for files, can use - for stdout


class Config(object):
  """A global configuration class.

  Set at initialization, before subcommands are called.
  """

  def __init__(self):
    """Use empty init for configuration."""
    self.db = None

pass_config = click.make_pass_decorator(Config, ensure=True)  # ensure=True to set Config on first use


@click.group()
@click.option('--input', type=click.File(), default='main.clvdb', help='Location of clvdb to be used')
@click.option('--output', type=click.File('w', atomic=True), default='main.clvdb',
              help='Location of clvdb to be used')  # atomic=True means don't ovewrite on open
@click.option('--verbose', is_flag=True, help='Turn on verbose mode')
@pass_config
def cli(config, input, output, verbose):
  """A CLI for all your vocab needs."""
  config.input   = input
  config.output  = output
  config.verbose = verbose
  config.data    = _load(input)


@cli.command()
@click.argument('word')
@click.argument('lang')
@click.argument('definition', required=False)
@click.option('--add_defintion', help='Add an additional definition,\
                                       otherwise the main definition will be overwritten',
                                 is_flag=True)
@pass_config
def add(config, word, lang, definition, add_defintion):
  """Add a word to the clvdb."""
  echo   = click.echo
  output = config.output
  data   = config.data

  entry = {'word':word
          ,'lang':lang
          ,'definitions':[definition]}
  data.append(entry)
  echo('Successfully added {}!'.format(word))
  if config.verbose:
    echo(json.dumps(entry))
  echo(json.dumps(data), file=output)


@cli.command()
@click.argument('word')
@click.argument('lang')
@click.argument('definition')
@click.option('--def_id', help='Number of definition to edit.', default=-1)
@click.option('-a', help='Add an additional definition,\
                          otherwise the main definition will be overwritten',
                          is_flag=True)
@pass_config
def edit(config, word, lang, definition, def_id, a):
  """Edit a word in the clvdb."""
  echo   = click.echo
  output = config.output
  data   = config.data
  rec_id = -1

  if a and def_id != -1:
    echo('Cannot add and edit an entry at the same time.')
    return False

  if def_id <= 0:
    echo('Must select a valid definition number.')
    return False

  for idx, d in enumerate(data):
    if d['word'] == word and d['lang'] == lang:
      rec_id = idx

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
  echo(json.dumps(data), file=output)


@cli.command()
@click.argument('lang', required=False)
@pass_config
def list(config, lang):
  """List words in the DB."""
  echo = click.echo
  data = config.data
  word_size = 10
  echo('{} | {} | {}'.format('entry'.ljust(word_size), 'lang', 'definition'))
  echo('{}-+-{}-+--------------'.format('-'.ljust(word_size, '-'), '-'.ljust(4, '-')))
  for d in data:
    if lang is None or d['lang'] == lang:
      definitions = _build_definitions(d['definitions'], word_size)
      echo('{} | {} | {}'.format(d['word'].ljust(word_size), d['lang'].ljust(4), definitions))


def _load(input):
  # create new db if no JSON to load
  try:
    data = json.load(input)
  except:
    data = []
  return data


def _build_definitions(definitions, offset):
  nums = '①②③④⑤⑥⑦⑧⑨⑩'
  out  = []
  padding = 0
  for idx, d in enumerate(definitions):
    if not d:
      continue
    if idx != 0:
      padding = offset + 10
    out.append('{}{} {}'.format(' ' * padding, nums[idx], d))
  return '\n'.join(out)
