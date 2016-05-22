# README

This module provides a simple interface to control an Energenie power socket.

Tested devices:
- EG-PMS2-LAN

The Energenie module is released under the MIT licence. Feel free to copy or modify this module. If you do some
improvements or changes, it would be nice if you would share the changes with me!

## Use the Energenie class directly

energenie = Energenie('192.168.1.10', 'socket password')
energenie.login()
print energenie.get_socket_state()
print energenie.get_socket_state(1)
print energenie.get_socket_state(2)
energenie.set_socket_state(3, False)
print energenie.get_socket_state()
energenie.logout()

## Command line

Get the state of all sockets
```
python energenie.py --ip '192.168.1.10' --password 'socket password' -g
{1: True, 2: False, 3: False, 4: False}
```

Get the state of socket 3
```
python energenie.py --ip '192.168.1.10' --password 'socket password' -s 3 -g
False
```

Enable socket 3
```
python energenie.py --ip '192.168.1.10' --password 'socket password' -s 3 -e
```

Enable all sockets
```
python energenie.py --ip '192.168.1.10' --password 'socket password' -e
```

## If you think my work was useful for you, you might buy me a beer

<form action="https://www.paypal.com/cgi-bin/webscr" method="post" target="_top">
<input type="hidden" name="cmd" value="_s-xclick">
<input type="hidden" name="encrypted" value="-----BEGIN PKCS7-----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-----END PKCS7-----
">
<input type="image" src="https://www.paypalobjects.com/de_DE/CH/i/btn/btn_donateCC_LG.gif" border="0" name="submit" alt="Jetzt einfach, schnell und sicher online bezahlen – mit PayPal.">
<img alt="" border="0" src="https://www.paypalobjects.com/de_DE/i/scr/pixel.gif" width="1" height="1">
</form>