Magnet2
=======

Python XMPP MUC entertainment, informational and administration bot

Made by Grom PE

Additional documentation by Oreolek

Released as public domain.

Programming language: Python 2

See `PLUGINS.md` for the command list.

Setup
-----
- Grab xmpppy library and put in Magnet2 directory
- Make a copy of the file `magnet_config.py.example` as `magnet_config.py`
- Change the configuration file `magnet_config.py`
- Run `magnet2.py`

MUC configuration
-----------------
Currently there is no mechanism to add MUC on-the-fly, so every one is configured manually. The example is this:

    'name@server.address': {
       'options': [
         'timebomb',
         'simple_fun',
         '...'
       ],
       'commands_pm_only': ['image'],
       'commands_disabled': [],
     },

where `options` is a list of allowed commands. This list has to be present in the config, everything else is optional. So if you want to add a command, you enable a plugin and then add this command to `options` list.

Use `commands_pm_only` option for setting per-room PM only commands.
Use `commands_disabled` option for the command disabling per-room.

Troubleshooting
---------------
If a problem arises, try setting `log_level` to 4 (see config example).

If the problem still persists, find this string in magnet2.py:

    self.client = xmpp.Client(jid.getDomain(), debug=[])

and add `socket` to debug list, like this:

    self.client = xmpp.Client(jid.getDomain(), debug=['socket'])

Now you'll be able to see all XMPP traffic.
