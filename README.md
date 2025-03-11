# Web Application (Version 1)
An application that allows museum visitors and other interested parties to query the database.

---

## The Application

`runserver.py`. When executed with `-h` as a command-line argument, the program displays the following help message describing the program's behavior:

```
$ python runserver.py -h
usage: runserver.py [-h] port

The YUAG search application

positional arguments:
  port        the port at which the server should listen

optional arguments:
  -h, --help  show this help message and exit
```

`runserver.py` runs an instance of the Flask test server on the specified port, which must in turn run your application.

---
## Specific Endpoints

There are three endpoints:
1. `/` returns the primary page, with the input fields filled in having the values of the most recent search query
  * If the user has previously made a search query, the table containing the results of the most recent query is displayed on this page
2. `/search?...` returns the results of a search using the parameters in the query string (that is, those that the user entered on the primary page).
   * The parameters accepted by the `/search` endpoint are `l` (for the label), `a` (for the agent name), `c` (for the classifiers), and `d` (for the date)
3. `/obj/<int:obj_id>` returns the secondary page populated with information about the object with the `obj_id` provided in the query string.

Adapted from Assignment 3 for COS 333 &copy;2021 by Robert M. Dondero, Jr., Princeton university
