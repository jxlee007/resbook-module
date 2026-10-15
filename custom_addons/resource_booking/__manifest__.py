{
    'name': 'Resource Booking MVP',
    'version': '20.0.1.0.0',
    'summary': 'POC Manage and book local resources',
    'category': 'Services',
    'author': 'jxlee',
    'license': 'LGPL-3',
    'depends': ['base'],
    'data': [
        'security/ir.access.csv',
        'views/resource_views.xml',
    ],
    'installable': True,
    'application': True,
}