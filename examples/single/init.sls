{% from "single/map.jinja" import single with context %}

single_install_dependencies:
  pkg.installed:
    - names:
      - unzip
      - curl


single_install_package:
  pkg.installed:
    - name: htop
    - version: latest
    - require:
      - pkg: single_install_dependencies


single_manage_main_config:
  file.managed:
    - name: /etc/single/single.conf
    - source: salt://{{ slspath }}/files/single.conf
    - makedirs: true
    - require:
      - pkg: single_install_package


single_confd_directory:
  file.directory:
    - name: /etc/single/conf.d
    - makedirs: true
    - clean: true


single_confd_entry:
  file.managed:
    - name: /etc/single/conf.d/entry.conf
    - source: salt://{{ slspath }}/templates/entry.conf.j2
    - makedirs: true
    - require_in:
      - file: single_confd_directory


single_manage_service:
  service.dead:
    - name: chrony
    - enable: false
