Safebooru Post Grabber
======================

I intend on doing more with this tool in the future, I will most likely add
the ability to search with tags/ pid/ limit, but at this moment in time the
tool basically just downloads an image from the post ID that is entered.


How to Use
----------

Either edit `main()` at the bottom of safebooru.py directly -

Or

Download using ID:

    $ python safebooru.py -i 3664652

Download using tags and page:

    $ python safebooru.py -t "serial_experiments_lain" -p 2

    # To download a specific post on this page.
    $ python safebooru.py -t "serial_experiments_lain" -p 2 -n 3
