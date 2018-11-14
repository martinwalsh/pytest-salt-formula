{% from "two/map.jinja" import two with context %}

include:
  - one

two_package:
  pkg.installed:
    - name: vim-minimal
    - require:
      - sls: one
