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
    - template: jinja
    - makedirs: true
    - require_in:
      - file: single_confd_directory


single_rename_file:
  file.rename:
    - name: /etc/single/renamed.txt
    - source: /etc/single/rename-me.txt


single_append_to_file_with_text:
  file.append:
    - name: /etc/single/single.conf
    - text: |
        Text to append


single_append_to_file_with_source:
  file.append:
    - name: /etc/single/single.conf
    - source: salt://{{ slspath }}/files/append-single.txt


single_append_to_file_with_multiple_sources:
  file.append:
    - name: /etc/single/single.conf
    - sources:
        - salt://{{ slspath }}/files/append-one.txt
        - salt://{{ slspath }}/files/append-two.txt


single_recurce_directory:
  file.recurse:
    - name: /etc/single-recurse
    - source: salt://{{ slspath }}/files/single-recurse


single_file_managed_with_multiple_sources_first:
  file.managed:
    - name: /etc/single/multisource-pickone.txt
    - source:
      - salt://{{ slspath }}/files/this-one-exists.txt
      - salt://{{ slspath }}/files/this-one-does-not-exist.txt


single_file_managed_with_multiple_sources_second:
  file.managed:
    - name: /etc/single/multisource-picktwo.txt
    - source:
      - salt://{{ slspath }}/files/this-one-does-not-exist.txt
      - salt://{{ slspath }}/files/this-one-exists.txt


single_manage_service:
  service.dead:
    - name: chrony
    - enable: false
