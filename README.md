#The Ultimate Super Duper Aur Helper

I wanted something that could push packages from AUR straight to my shared repo at home (were I pull packages from several machines).

I didn't like any of the alternatives, and someone told me "why don't you roll your own?".
That was about two hour ago :)

I might do some more stuff to TUSDAH, like dependency resolving and stuff. </lie>

## Configuration

The config files goes in ~/.config/tusdah/config

Here's my example:

   [repo]
   location = /srv/http/default/archlinux/packages
   db = /srv/http/default/archlinux/packages/hugo.db.tar.gz
