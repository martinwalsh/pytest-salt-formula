{{ '{%' }} from "{{ cookiecutter.formula_name }}/map.jinja" import {{ cookiecutter.formula_name }} with context {{ '%}' }}

# {{ cookiecutter.formula_name }}_package:
#   pkg.installed:
#     - name: {{ cookiecutter.formula_name }}
#
# {{ cookiecutter.formula_name }}_main_config:
#   file.managed:
#     - name: /etc/{{ cookiecutter.formula_name }}/{{ cookiecutter.formula_name }}.conf
#     - source: salt://{{ '{{' }} slspath {{ '}}' }}/files/{{ cookiecutter.formula_name }}.conf
#     - owner: {{ cookiecutter.formula_name }}
#     - group: {{ cookiecutter.formula_name }}
#     - mode: '0644'
#     - require:
#       - pkg: {{ cookiecutter.formula_name}}_package
#
# {{ cookiecutter.formula_name }}_service:
#   service.running:
#     - name: {{ cookiecutter.formula_name }}
#     - enable: true
#     - watch:
#       - pkg: {{ cookiecutter.formula_name }}_package
#       - file: {{ cookiecutter.formula_name }}_config
