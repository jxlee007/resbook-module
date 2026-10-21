FROM odoo:20.0

USER root
RUN mkdir -p /mnt/extra-addons
COPY ./custom_addons /mnt/extra-addons
RUN chown -R odoo:odoo /mnt/extra-addons

USER odoo

# CRITICAL FIX: Added --db_port=5432 to route database traffic away from web ports
ENTRYPOINT ["/entrypoint.sh", "odoo", "--db_port=5432", "-i", "base,resource_booking", "--without-demo=False"]