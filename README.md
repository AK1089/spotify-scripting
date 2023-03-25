
# Spotify Scripting

This documentation serves as a brief introduction to my Spotify Scripting language, which can construct custom playlists for you based on a complex set of rules.

Want a playlist to open with a random song from a list of good opening tracks, then be followed by a random Taylor Swift song, and then two Lady Gaga songs from different albums? This is easy to do with Spotify Scripting!

<br>

## Authors

- [AK1089](https://www.github.com/AK1089)

<br>

## Setup

The main directory should contain `interpreter.py`, as well as the files: <br>
`config.txt` filled in with your Spotify API details <br>
`playlists.txt` which contains specified playlist details (the API's playlist search is notoriously bad.) <br>
`tracks.json` which can be left empty to start (the program will build out a track cache as you use it.) <br>
<br>
Each playlist you create should be contained in its own text file (.txt) in the Playlists subfolder, named after its intended title.
<br>
To use the program, run `python3 interpreter.py playlist` (with playlist being the name of your desired playlist) in the directory. The first time you run the program, you'll have to log in with Spotify to grant access to your details.
<br>
<br>



## Documentation

The syntax of the scripting language is detailed in the rest of this document. Each line should begin with a keyword from the following table.

<br>

| Keyword | Function                                       |
| ------- | ---------------------------------------------- |
| #       | a comment (line does nothing)                  |
| var     | declares / alters a variable                   |
| if      | branching logic                                |
| elseif  | branching logic                                |
| else    | branching logic                                |
| fi      | closes a branch of if/elseif/else              |
| pass    | no operation (does nothing)                    |
| jumpto  | jumps to a line number or the specified coda   |
| coda    | trigger for jumpto                             |
| quit    | halts execution                                |

<br>
<br>

### Declaring Variables

Variables are declared and set using the **var** keyword. For example,  
`var a = 3`  
initialises the variable `a` to the value of 3. As in Python, there is no syntactic difference between declaring new variables and changing the value of existing ones. Variables can only take floating point values. Boolean values are represented by 1 and 0 for True and False.

<br>

### Operators

The basic operators are:  
|    |                             |
| -- | --------------------------- |
| \+ | addition                    |
| \- | subtraction                 |
| \* | multiplication              |
| \/ | division                    |
| \^ | exponentiation              |


The comparative operators are:
|     |                            |
| --- | -------------------------- |
| \== | equal to                   |
| \!= | not equal to               |
| \>  | greater than               |
| \>= | strictly greater than      |
| \<  | less than                  |
| \<= | strictly less than         |

The logical operators are:
|    |                             |
| -- | --------------------------- |
| \! | NOT                         |
| \| | OR                          |
| \& | AND                         |

Parentheses are used as normal to bracket the order of expressions.
Comparative and logical operators return either 0 or 1.

Some random features are available in variables too. <br>
`rand()` -> a random float uniformly distributed across [0, 1] <br>
`randint(a, b)` -> a random integer uniformly distributed across [a, b] (where a<b) <br>
`choose(a, b, c, ...)` -> returns one of a, b, c, etc. with equal chance <br>

<br>
<br>

### Branching Logic

```
a = rand()
if a < 4

  # this code runs if a is less than 4
  var b = 10

elseif a < 5

  # this code runs if a is less than 5, but was not less than 4
  var b = 8

else

  # this code runs if a is neither less than 4 nor less than 5
  var b = 12

fi
```
This works like nearly all other languages.
<br>
<br>

### Jumping Logic

The `jumpto` keyword can take two types of arguments: integers (line numbers), and keywords.
These two uses are demonstrated below: line number jumps skip to the beginning of that line,
and keyword jumps skip to the next line containing `coda <keyword>`.

```
 1 |  var a = 10
 2 |  jumpto trigger
 3 |  
 4 |  # the following line is not run, as we are jumping to trigger
 5 |  var a = 20
 6 |  
 7 |  coda trigger
 8 |  var a = 30
 9 |  jumpto 14
10 |
11 |  # the following line is also not run, as we are jumping to line 14
12 |  var a = 40
13 |
14 |  var a = 50
```
This sets the variable `a` to 10 on line 1, then 30 on line 8, then 50 on line 14.
All other lines are skipped by the two types of jumpto.
<br>
<br>

### The "pass" and "quit" keywords

The `pass` and `quit` keywords are very simple. A line which starts with pass does nothing, and a line starting with quit halts the entire program.
<br>
<br>

## Actually Playing Music

Finally, the good bit! To play music, use the `play` keyword. For example:
<br><br>
```
play 2 from playlist("my favourite songs")
```
The first number can be literal, a variable you've defined, or the word "all". The line above will play 2 (different, randomly selected) songs from the selected playlist.
<br><br>
```
play 1 from album("future nostalgia")
```
will play a random song from the album *Future Nostalgia* by Dua Lipa.
<br><br>
```
play 1 from album(choose("1989 deluxe", "reputation", "lover"))
```
will select a random album from *1989 (Deluxe)*, *reputation*, or *Lover* by Taylor Swift, then play a random song from there.
<br><br>
```
play all from choose(artist("lady gaga").albums)
```
will select a random album from all of Lady Gaga's discography, then play it through.
<br><br>
More complicated expressions are also available, including using the "filtered by" keyword! For example,
```
var a = randint(2, 3)
play a from playlist(choose("party playlist", "best sad songs")) filtered by (year=span(None, 2018))
```
will pick either the "party playlist" or "best sad songs" playlist, filter that playlist down to songs which were released during or before 2018, and then play either 2 or 3 songs from the resulting shortlist.
<br><br>
Note that you can filter by year, duration, popularity, or track_number (position within its album). Use span(lower, upper) to denote an inclusive range, with None being an acceptable endpoint (eg. span(None, 2018) denotes "during or before 2018").
<br><br>

### Accepted Music Sources (functions)
The functions you can use to find music in script code include:<br>
`artist("name")` finds an artist by the given name. You can access the .albums attribute. <br>
`album("name")` finds an album by the given name. You can access the .tracks attribute, as well as the .artist, .year, and .length attributes. <br>
`playlist("name")` finds a playlist by the given name, either through the playlists.txt file or through Spotify search.<br>
`track("name")` finds a track by the given name.<br>
<br>

## A Full Example (also found in example.txt)
```
# plays 1 from a random album out of the ones listed
play 1 from album(choose("reputation", "lover", "1989 deluxe"))

# plays two 2018-2020 song from the pres playlist
play 2 from playlist("pres") filtered by (year=span(2018,2020))

# plays a song from the first four from my current obsessions playlist
play 1 from playlist("songs i'm currently obsessed with")[:4]

# plays a song from the top thirteen taylor playlist
play 1 from playlist("top thirteen taylor")

# sets a to a random value out of 1 / 2 and plays that many songs from one of these albums (that's 2-4 minutes long)
var a = randint(1, 2)
play a from album(choose("future nostalgia", "mercurial world")) filtered by (duration=span(120, 240))

# if a was set to 2, play a random carly rae jepsen song
if a == 2
  play 1 from choose(artist("carly rae jepsen").albums)

# otherwise if a was 1, play a fairly popular 3-3.5 minute song from the NYE party playlist
else
  play 1 from playlist("nye party playlist") filtered by (duration=span(180, 210), popularity=span(70, 90))
fi

# 99% chance we end here
if rand() < 0.99
  quit
fi

play 1 from track("never gonna give you up")

```