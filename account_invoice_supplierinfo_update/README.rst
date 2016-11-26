.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

=====================================================
Update Supplier Info of product from Supplier Invoice
=====================================================
This module allows in the supplier invoice, to automatically update all
products whose unit price on the line is different from the supplier price.
It creates a new supplier price if there is not or it updates the first.


Usage
=====

.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
   :alt: Try me on Runbot
   :target: https://runbot.odoo-community.org/runbot/142/8.0

Bug Tracker
===========

Bugs are tracked on GitHub Issues. In case of trouble, please check there
if your issue has already been reported. If you spotted it first,
help us smashing it by providing a detailed and welcomed feedback.

Known Issues / Roadmap
======================

* This module does not manage correctly different if
    * invoice line UoM are not the same as Supplierinfo UoM
    * invoice line taxes are not the same as products taxes

Credits
=======

Contributors
------------

* Chafique Delli <chafique.delli@akretion.com>
* Sylvain LE GAL (https://twitter.com/legalsylvain)

Maintainer
----------
 
.. image:: https://odoo-community.org/logo.png
   :alt: Odoo Community Association
   :target: https://odoo-community.org

This module is maintained by the OCA.

OCA, or the Odoo Community Association, is a nonprofit organization whose mission is to support the collaborative development of Odoo features and promote its  widespread use.

To contribute to this module, please visit https://odoo-community.org.
