*This file contains information regarding how to work with existing pymediadump rules and how to write your own*

# Introduction

Usually web pages are html-formatted text files. In order to determine, which parts of html source contains information you are seeking for, pymediadump uses **rules**. As for now, these are **.ini files with small addition of custom formatting**. Each rule file includes list of sites it applies to, human-readable description of what exactly it will try to download and set of rules that gets passed to program in order to serve said downloads.

# Using third-party rules

In order to make your installation of pymediadump utilize third party rules - **simply drop them into script's /rules/ subfolder**. When you will launch script again - it will seek through all .ini files in this directory and try to apply all rules that match provided urls. As for the moment of writing, the only way to avoid some rule from getting used is to **remove it from /rules/ directory or rename to something that isnt .ini file** (say, "rule.ini.old") - but Im working on that.

# Writing your own rules

As said above, rules are but simple .ini files with a bit of custom formatting. Making your own rules is extremely easy, once you know the basics. Thus, lets get started:

## Formatting

As for the moment of writing, the following formatting is supported:
- Square brackets to announce categories: `[Name of category]`
- Equality sign to split key and values (works fine with spaces): `Key = Value`
- Hashtags to make comments. Its highly recommended to only use these on separate lines: `#This is how comment looks like`
- Binary operator **with spaces around it** to introduce multiple values per key. `Key = first value | second value | etc etc`

Aside from said, its worth mentioning importance of **correctly capitalizing your content**. Because "Main" and "main" are **CONSIDERED DIFFERENT THINGS**.

## Basic rule's content

The very basic rule file that would be considered a valid by pymediadump would look like that:
`[Main]
Name = Example.com Urls
Description = Download every url from example.com
URLs = example.com

[Rules]
Find = "url":"(.*?)"`

While it should be pretty much self-explanatory, lets dive deeper into currently introduced keys:
- **Name**. Well, the name of rule. Usually kind of short version of description. `Name = Sitename Pictures`
- **Description**. Description of what exactly this rule tries to get and from where. `Description = Download all images from sitename`
- **URLs**. List of urls, this rule will apply to. Despite being in category dedicated for human-readable content, its one of the most important parts of your rule - **if you will spell its content incorrectly, script wont consider it matching your urls**. Also its worth mentioning that its the only entry of "Main" that **supports regular expressions**. Meaning instead of "one.sitename.com | two.sitename.com | three.sitename.com" you can just use ".*sitename.com". `URLs = sitename.com"`
Above are the only keys in "Main" category. The rest, including optional keys, will be content of "Rules" category. Keep in mind that categories arent just to make things look pretty - **keys located in incorrect categories wont be recognized and will be considered missing**.

Now about "Rules" category. As for now, there is but one key that necessary has to be there. The rest are optional things, we will talk about them later.
- **Find**. Regular expression that determines, which content on page contains data that will be further processed (or, in case it already returns a well-preserved direct link that doesnt require any additional rules to work - pass this link to built-in files downloader). This may be complicated to write, requiring you to both know how regular expressions work (there are many good articles online) and how web pages you are trying to process are looking from inside (just use your browser's "developer mode" to open web page's source. Then ctrl+f to find data you are looking for. Since different pages of same type on same site usually tend to have similar template - content of required type on one will usually be located in similar place on another. Thats how we make rules work site-wide). But once you figure this once or twice - you kinda get used to it. Lets take a look on this example: `Find = "url":"(.*?)"`. What it does is basically finds everything that match `"url":"somecontent"`. E.g, say, `"url":"example.com/file.jpg"`, `"url":"anotherexample.com/otherfile.zip"`. You've got the idea. Keep in mind that **this rule will try to find every single match on page**. Meaning sometimes you will need to use optional keys to polish the output.

These are the only keys you should know for writing basic rule file. With just these, it will be considered valid and used by program. However, there are multiple optional keys that may come handy in some cases. We will talk about them below

## Optional Keys
Depending on page's layout, its possible that content you are trying to find collides with some unwanted things. You can probably solve this by writing even more complicated regexp rule... Or, well - rely on optional keys. These are additional entries to "Rules" category that **affect data gathered with "Find"**. Meaning not all of them need to exist in rule file at once. But if some do - they will get applied. As for the moment of writing, there are the following optional rules, in order of their execution:
- **Exclude**. Exclude data entry if it matches provided regexp mask. Say, `Exclude = .*/comment/` will remove `example.com/comment/picture.jpeg`, but leave `example.com/post/picture.jpeg` be
- **Clear**. Remove provided parts/symbols from data entries. Say, `Clear = \` will remove all backslashes from data, turning `example.com\/path\/file.png` into `example.com/path/file.png`
