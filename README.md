*All of this has started as simple script to download flash games from newgrounds...*

**Description:**

This is a python-powered tool to download required media files from sites. Dont set your hopes high tho - it only supports grabbing stuff thats accessible via page's html source (for more advanced needs check youtubedl or something like that) and only if you will feed it with search rules to find this data on page (out of box there are rules for [danbooru posts](./rules/danbooru-media.ini) and [newgrounds flash games](./rules/newgrounds-swf-games.ini), but these are pretty self-explanatory and you can easily write your own rulesets). If I wont lose interest, someday this may get more features and maybe even gui, but for now - thats what you get. Just a mere cli web scraper, configurable with .ini

**Dependencies:**

- python 3.8+
- python-requests

**Example Usage:**

`pmd-cli.py https://www.newgrounds.com/portal/view/746618 -r ./rules/newgrounds-swf-games.ini -d ./ng-games`

**License:**

[GPLv3](LICENSE)
