# Installation prerequisites
* python-cups bindings
* virtualenv

# Getting started

1. Setup a **new virtualenv** somewhere and **activate** it
1. easy_install or **pip install Jinja2 Werkzeug**
1. If your version of Python doesn't come with a native `json` module, you'll need to easy_install or **pip install simplejson**
1. **Clone into the root of the virtualenv**, so you should have `virtualenv_root/{photoreg,bin,include,lib}`
1. **mkdir for the collected data**, it's one file per registration (eg. `virtualenv_root/records/`)
1. **Copy the sample environment script** into the root of the virtualenv, and adjust parameters to suit


# Running the app

    cd root/of/virtualenv/
    source photoreg.env
    cd photoreg/
    python reg.py

