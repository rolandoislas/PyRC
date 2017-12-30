# Regex

The following are regexes  that are used for IRC message parsing.

**Note: These regexes use named groups, which are not supported in all parsers.**

## IRC Message Format Regex

**Note: The $PARAMS variable is a reference to [IRC Message Params](#IRC Message Params).**

```
^(?::(?<servername_or_nick>[^!@\s]+)(?:!(?<user>[^@\s]+))?(?:@(?<host>[^\s]+))?\s)?(?<command>[A-Za-z0-9]+)(?<params_all>$PARAMS+)(?:\r?\n?)
```

## IRC Message Command Params

```
(?<params>\s(?:(?::(?<param_trailing>.*))|(?:(?<param_middle>[^\s]+))))
```