NotIRSSI
========
Use libnotify / osx notification / growl / dbus over SSH to alert user
of highlight.

This code is a quick and dirty hack to get notifications over ssh from my server
running irssi to my mac laptop. Aimed to be extended with other notification
systems.

Original Idea
=============
The original idea came from
 * http://m0g.net/notossh/
 * http://github.com/guyzmo/notossh
 * http://i.got.nothing.to/blog/2010/06/21/on-screen-notifications-from-irssi-over-ssh

for original notify.pl code :
 * http://lewk.org/log/code/irssi-notify

Install
=======
Remote host running irssi
-------------------------
* git clone https://github.com/crisidev/notirssi ~/notirssi
* cd ~/.irssi/scripts/autorun
* ln -s ~/notirssi/plugins/notirssi.pl .
* /load perl
* /script load autorun/notirssi
* /hilight -regex bla|bla

Local laptop running ssh client
-------------------------------
* git clone https://github.com/crisidev/notirssi ~/notirssi
* cd ~/.notirssi
* python setup.py install (or sudo)
* configure SSH to forward the correct port
* notirssi start
* notirssi stop
* notirssi --help

Options
=======
```
  usage: /usr/local/bin/notirssi [-h] [-f] [-S] [-V] [-H HOST] [-P PORT]
                                 [-G GROWL] [-N NOTIFY] [-T NOTIFIER] [-L LABEL]
                                 {start,stop} ...

  IRSSI Notify Listener

  positional arguments:
    {start,stop}
      start               Starts the service
      stop                Stops the service

  optional arguments:
    -h, --help            show this help message and exit
    -f, --foreground      Make the notifications stick
    -S, --sticky          Make the notifications stick
    -V, --verbose         Make the listener verbose
    -H HOST, --host HOST  Host to listen on
    -P PORT, --port PORT  Port to listen on
    -G GROWL, --with-growl GROWL
                          Path to growl executable
    -N NOTIFY, --with-notify NOTIFY
                          Path to notify executable
    -T NOTIFIER, --with-terminal-notifier NOTIFIER
                          Path to terminal-notifier executable
    -L LABEL, --label LABEL
                          Label for terminal-notifier

  By Matteo Bigoi with patches from Bernard Guyzmo Pratz, Charles
  doublerebel Philips, Rui Abreu Ferreira, Cooper Ry Lees, Kevin Mershon
```

Configuration
=============

Add to your .ssh/config those lines:

    Host REMOTE_HOST
      LocalCommand "/path/to/bin/notossh start"
      RemoteForward REMOTE_PORT localhost:LOCAL_PORT

Notifications
=============

to change the way notifications behaves, like on Fedora systems, you can change the notification
line to the following, making it transient :

    return [args.notify, '--hint', 'int:transient:1', '-i', 'dialog-information', '-t', '5000', ':'.join(args[1:]), args[0]]


TODO
====
* check method is not working if the server is stopped
* exceptions in NotIRSSINotifier are bizantine :)
* move away from the ugly forking model to a threaded and sane one
* make it a real daemon, aware of more than one client connected


Licences
========

Since 2010, that code is aimed to be hacked.
Thanks to Charles `doublerebel` Philips, Rui Abreu Ferreira and Cooper Ry Lees for their hacks!

notify.pl is under GPL (because I copy/pasted it from Luke Macken and Paul W. Frields)

everything else is WTFPL (because I don't care what you do with it, but if you don't 
tell me you've improved it it, you're just a moron)

And if you like it, buy me a beer ! 

By Bernard `Guyzmo` Pratz
Mail-me on guyzmo at m0g dot net.

 * WTFPL

        DO WHAT THE FUCK YOU WANT TO PUBLIC LICENSE 
                    Version 2, December 2004 

 Copyright (C) 2004 Sam Hocevar <sam@hocevar.net> 

 Everyone is permitted to copy and distribute verbatim or modified 
 copies of this license document, and changing it is allowed as long 
 as the name is changed. 

            DO WHAT THE FUCK YOU WANT TO PUBLIC LICENSE 
   TERMS AND CONDITIONS FOR COPYING, DISTRIBUTION AND MODIFICATION 

  0. You just DO WHAT THE FUCK YOU WANT TO.

 * GPLv2

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 2 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.

EOF
