pulse-volume
============

Easily read and set Pulse volume and mute status for a given sink from the 
command line.

Installation
------------

1. Check out the repository
2. Either stop there and run the script directly, or throw it in your path with 
   something like

   ```
   ln -s path/to/pulse-volume/pulse-volume.py ~/bin/pulse-volume.py
   ```

   You might want to name the symlink something more practical while you're at 
   it. Mine is called `volume`.

Usage
-----

See `pulse-volume.py --help` for full information.

Notifications
-------------

If the `--notify` option is given, `pulse-volume` expects to find
[`notify-send.sh`](https://github.com/vlevit/notify-send.sh)
in the `$PATH`, and uses it to raise a desktop notification with the current volume status.

Examples
--------

- Read the volume and mute status of the default sink:

  ```
  pulse-volume.py
  ```

- Toggle the mute status of the default sink and show a notification:

  ```
  pulse-volume.py --toggle --notify
  ```

- Mute the default sink:

  ```
  pulse-volume.py --mute
  ```

- Unmute the default sink with no output:

  ```
  pulse-volume.py --quiet --unmute
  ```

- Do something useful with the mute status (the `--muted` flag causes the script 
  to exit with a status code reflecting the mute status):

  ```
  pulse-volume.py --muted && do-something-useful || do-something-else
  ```

- Raise the volume of the sink with index 2 by 5% and show a notification:

  ```
  pulse-volume.py --sink=2 5%+ --notify
  ```

- Lower the volume of the default sink by 15 units and show a notification:

  ```
  pulse-volume.py 15- --notify
  ```

- Set the volume of the default sink to 25% and unmute it:

  ```
  pulse-volume.py --unmute 25%
  ```

- Set the volume of the default sink to 6400 units:

  ```
  pulse-volume.py 6400
  ```
