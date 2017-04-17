# clv
_Command Line Vocab_: for all of you who wish you could play with vocabulary from the terminal.


## installation

_for local installation_
`$ pip install --editable .`
`$ cp default_config.ini config.ini`

_for global installation_
`pip3 install --upgrade  .`


## commands
_all commands use word and language as unique key, to prevent collision with homographs across languages_

flags are single dashes, options are double dashes.

* `add`: add an entry
* `edit`: edit an existing entry
  * _-a_: add a new definition
  * _--def_id_: edit an existing defintion (1-indexed to match terminal output in `list`)
* `delete`: delete an entry from the clvdb
* `tag`: add a tag to am entry
* `untag`: remove a tag from am entry
* `example`: add an example sentence for an entry
* `cloze`: get tested on a random cloze
  * a cloze is a sentence where part of it is marked to be hidden from the user, to help with recall. ex. if the example was 'near far {wherever} you are', _cloze_ would return 'near far {...} you are' and expect 'wherever' as the user's answer
* `list`: lists entries in clvdb
  * default argument: [LANG], filter by language
  * _-t_: display tags in table
  * _--tags_: filter by CSV list of tags
* `lookup`: lookup a word and its information


### configuration

* `set`: sets a reusable global config item, currently only sets the `lang` attribute
* `config`: view config items