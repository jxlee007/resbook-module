FROM odoo:20.0

USER root
RUN mkdir -p /mnt/extra-addons
COPY ./custom_addons /mnt/extra-addons
RUN chown -R odoo:odoo /mnt/extra-addons

USER odoo

# Use standard configuration execution flags
CMD ["odoo", "-c", "/etc/odoo/odoo.conf"]