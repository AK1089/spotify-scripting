
# Spotify Scripting

This documentation serves as a brief introduction to my Spotify Scripting language, which can construct custom playlists for you based on a complex set of rules.

Want a playlist to open with a random song from a list of good opening tracks, then be followed by a random Taylor Swift song, and then two Lady Gaga songs from different albums? This is easy to do with Spotify Scripting!

<br>

## Authors

- [AK1089](https://www.github.com/AK1089)

<br>

## Documentation

Each playlist should be contained in its own text file in the Playlists subfolder, named after its intended title. 

The syntax of the scripting language is as follows:

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