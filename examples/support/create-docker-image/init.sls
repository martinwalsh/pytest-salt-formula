clean-yum-caches:
  cmd.run:
    - name: yum clean all

remove-yum-cache-directory:
  file.absent:
    - name: /var/cache/yum

