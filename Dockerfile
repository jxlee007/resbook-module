FROM odoo:20.0

USER root
RUN mkdir -p /mnt/extra-addons
COPY ./custom_addons /mnt/extra-addons
RUN chown -R odoo:odoo /mnt/extra-addons

USER odoo

# Pass Odoo's default entrypoint script plus initialization parameters cleanly
ENTRYPOINT ["/entrypoint.sh", "odoo", "-i", "base,resource_booking", "--without-demo=False"]