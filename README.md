*All of this has started as simple script to download flash games from newgrounds...*

**Description:**

This is a python-powered tool to download required media files from sites. Dont set your hopes high tho - it only supports grabbing stuff thats accessible via page's html source (for more advanced needs check youtubedl or something like that) and only if you will feed it with search rules to find this data on page (out of box there are rules for [danbooru/safebooru posts](./rules/danbooru-media.ini), [newgrounds flash games](./rules/newgrounds-swf-games.ini) and [joyreactor posts with pictures](./rules/joyreactor-images.ini), but these are pretty self-explanatory and you can easily write your own rulesets). If I wont lose interest, someday this may get more features and maybe even gui, but for now - thats what you get. Just a mere cli web scraper, configurable with .ini

**Dependencies:**

- python 3.8+
- python-requests

**Example Usage:**

`pmd-cli.py https://www.newgrounds.com/portal/view/746618 -d ./ng-games`

**QA:**

**Q:** - BUT WHY ARE YOU USING REGULAR EXPRESSIONS? THEY ARE SO BAD, USE BS4 INSTEAD

**A:** - Well... As I said in title, this project has started as tool to download flash games from newgrounds (coz adobe broke their browser extension and the only way to play *spicy pixel stuff* right now is via standalone flash player... or at least thats how things are on linux). And direct download links to these are hidden inside in-line javascript of game's webpage. And, since bs4 cant into js - I'd need to use regular expressions anyway (or something like slimit, which will bloat list of external dependencies even more). Surely I could go for it, but the thing is - *I have no clues how to design download rules for that*. Thus I went for "if it works - it works". I may change my opinion later, if necessary - but for now this nasty tool is fueled with regexp power.

**License:**

[GPLv3](LICENSE)
