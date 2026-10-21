# Use the official Odoo 20.0 base image
FROM odoo:20.0

USER root

# Ensure directories exist and copy custom addons path
RUN mkdir -p /mnt/extra-addons
COPY ./custom_addons /mnt/extra-addons

# Set correct runtime permissions for the Odoo server user
RUN chown -R odoo:odoo /mnt/extra-addons

USER odoo