

Installation

Prerequisites:
- Python 2.6.1+
- SASS
- Watchdog
- Django

##View Controller Helper Functions

###$.go(controller, [data])
Function to change hash to new page. Allows you to also send parameters with it

```javascript
$.go('home', {title:"Hey there dolly", id: "SAFDGSDFGDSFG"})
```

###$.goReplace(controller, [data, [isQuiet]])

Same as $.go but replaces current hash with new page.
If isQuiet is set to true then hash will be replaced without dispatching the change signal to change the page

```javascript
//Removes current hash from history and forwards to new hash
$.goReplace('home', {title:"Hey there dolly", id: "SAFDGSDFGDSFG"})

//Removes old hash from history, changes hash, but does not dispatch signal to the hasher to change page
$.goReplace('login', {title:"Hey there dolly", id: "SAFDGSDFGDSFG"}, true)
```

###$.partial(partialName, data)

Returns partial html rendered with given params, partial are to be located in the "partial" folder
