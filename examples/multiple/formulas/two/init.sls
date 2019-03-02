{% from slspath ~ '/map.jinja' import settings with context %}

include:
  - one

two_package:
  pkg.installed:
    - name: vim-minimal
    - require:
      - sls: one
