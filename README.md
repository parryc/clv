# clv
_Command Line Vocab_: for all of you who wish you could play with vocabulary from the terminal.


## installation
```
$ pip install --editable .
$ clv --help
```

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
* `list`: lists entries in clvdb
  * default argument: [LANG], filter by language
  * _-t_: display tags in table
  * _--tags_: filter by CSV list of tags