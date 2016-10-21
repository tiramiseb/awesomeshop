=====================
AwesomeShop Changelog
=====================

This file summarizes the most important modifications to AwesomeShop...

+------------+---------+------------------------------------------------------+
| Date       | Type    | Subject                                              |
+============+=========+======================================================+
| 2016-10-21 | Feature | Miscelaneous improvements on the cart page           |
+------------+---------+------------------------------------------------------+
| 2016-10-12 | Feature | Simplify by hiding checkout part of the cart page    |
+------------+---------+------------------------------------------------------+
| 2016-10-10 | Misc    | Store the PDF invoice in the database                |
+------------+---------+------------------------------------------------------+
| 2016-10-09 | Misc    | Swap shop name and page name in page title           |
+------------+---------+------------------------------------------------------+
| 2016-10-06 | Feature | Frontend as static files                             |
+------------+---------+------------------------------------------------------+
| 2016-09-07 | Bugfix  | Allow decimal variations for kit products            |
+------------+---------+------------------------------------------------------+
| 2016-09-04 | Feature | Internal note (for instance, tips for preparation)   |
+------------+---------+------------------------------------------------------+
| 2016-08-26 | Feature | Image and popup on kit products options              |
+------------+---------+------------------------------------------------------+
| 2016-08-23 | Feature | Easier internal links between pages                  |
+------------+---------+------------------------------------------------------+
| 2016-07-05 | Feature | Easier navigation between shop and dashboard         |
+------------+---------+------------------------------------------------------+
| 2016-07-01 | Bugfix  | Allow creaton of categories without parents          |
+------------+---------+------------------------------------------------------+
| 2016-06-24 | Feature | Allow the customer to cancel an order                |
+------------+---------+------------------------------------------------------+
| 2016-06-21 | Feature | Shipping fee estimation for anonymous users          |
|            |         +------------------------------------------------------+
|            |         | Display a popup when products are added to the cart  |
|            |         +------------------------------------------------------+
|            |         | KitProduct: sell multiple products at once           |
|            |         +------------------------------------------------------+
|            |         | Deal with product variable data (eg for kitproducts) |
|            +---------+------------------------------------------------------+
|            | Misc    | CHANGELOG file creation                              |
+------------+---------+------------------------------------------------------+
| 2016-06-20 | Feature | Merge cart and checkout pages                        |
|            +---------+------------------------------------------------------+
|            | Bugfix  | Use correct shipping price when weight = threshold   |
+------------+---------+------------------------------------------------------+

TODO
====

The following are ideas of features that may (or may not) be implemented
in AwesomeShop...

Major modifications
-------------------

I think these changes are not easy to do:

* Customize shipping delays for each product
* Use Beaker to cache some results
* Toolbar on a "page" page, to easily include specific stuff in pages contents
  (``.. doc-list::``, links to other pages, images...)
* Same height for all products in a products list
* Allow for a product to not be sold anymore (end of life): absent from the "out of stock" list

Minor improvements
------------------

These may be easy to implement:

* When creating an order, do not empty the cart before the browser is
  redirected to the order page (or display a message to tell the user (s)he
  must wait)
* Dashboard : toolbar for signin in, logging out, changing language...

Bugs
====

/
