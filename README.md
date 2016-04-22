# Python MIDI Environment

### Setup
This envrionment uses Python 3 and a couple dependencies. 

You will need to add the [python-osc](https://pypi.python.org/pypi/python-osc) which you can install via the command ```$ pip install python-osc```.

If you have Max 6 or Max 7, simply open up the Max patch. Otherwise, download and use [Max Runtime](https://cycling74.com/downloads/older/#.VvhnEWMh6vk). We may include a download link to the standalone version of the patch in the near future.

### Simple Application
We have pre-written a couple melodies including the theme to the fugue in Benjamin Britten. The following simple program includes our library, sets the tempo, and plays the Britten line.

```
# britten.py

from playMaxNotes import *
setTempo(180)
playLine(britten)

```

Run the file using the following command:

```
$ python3 britten.py
```

And you should see something like this:

![](http://g.recordit.co/R9VQEERo6j.gif)
