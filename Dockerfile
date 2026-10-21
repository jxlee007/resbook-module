FROM odoo:20.0

USER root
RUN mkdir -p /mnt/extra-addons
COPY ./custom_addons /mnt/extra-addons
COPY ./render-entrypoint.sh /usr/local/bin/render-entrypoint.sh
RUN chmod 755 /usr/local/bin/render-entrypoint.sh
RUN chown -R odoo:odoo /mnt/extra-addons

USER odoo

ENTRYPOINT ["/usr/local/bin/render-entrypoint.sh"]
CMD ["odoo"]