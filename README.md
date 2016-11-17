# Zubax Docs

This repository contains sources of the Zubax Docs website.

## Contribution

If you found a mistake on the website or just would like to improve it in some way,
feel free to fork this repo and send us a pull request. Thanks in advance!

### Markup and directory structure

Markup language is the standard Markdown with Github extensions.
Also, a few custom extensions are introduced:

* Tags `<info>`, `<warning>`, `<danger>`.
* All images are post-processed automatically to make them enlarge on click,
so an image can be inserted simply like that: `<img src="image.jpg" title="Blah">`.
* Add style `thumbnail` to make a thumbnail image: `<img src="image.jpg" title="Blah" class="thumbnail">`.
* All links, including image `src` attributes, can be relative URLs.
* In order to use an image in preview of the current document,
add ID `preview`, e.g.: `<img src="picture.png" id="preview">`.

File and directory naming pattern is as follows: `<weight> <title>`.
Zero weight is a special case - it is used to indicate that the given page is the index page for the current section.

Index page and menus are generated automatically.
Excerpts are built from the first paragraph of the corresponding section's index page.

Still have questions? Check out the existing pages for details.

## Running on a local machine

Install the following dependencies:

* Python 3.4+
* pip
* LESS compiler (lessc)
* libffi-dev

On a Debian-based system the dependencies can be installed as follows:

```bash
sudo apt-get install python3-dev python3-pip node-less libffi-dev
```

Once the dependencies are satisfied, clone this repo and then execute the following:

```bash
pip3 install -r requirements.txt
export SESSION_SECRET='Joo Janta 200 Super-Chromatic Peril Sensitive Sunglasses'
./run.py
```

Then navigate to <http://localhost:4000>.

## License

Entire contents of this repository, excluding third-party components, is distributed under the terms of
[BY-NC-SA (Attribution + Noncommercial + ShareAlike)](https://creativecommons.org/licenses/by-nc-sa/4.0/).
