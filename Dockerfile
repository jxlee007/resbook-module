FROM odoo:20.0

USER root
RUN mkdir -p /mnt/extra-addons
COPY ./custom_addons /mnt/extra-addons
RUN chown -R odoo:odoo /mnt/extra-addons

USER odoo

# Executes using default environment variables natively
ENTRYPOINT ["/entrypoint.sh", "odoo", "-i", "base,resource_booking", "--without-demo=False"]