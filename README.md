quadpy - Quadtree implementation for Python
===========================================

Based on javascript implementation by Patrick DeHaan:
[github.com/pdehn/jsQuad](https://github.com/pdehn/jsQuad)


Requirements
------------
Python 2.6+ should work


Demo app
--------
Demo GUI app is included, to set it up for the first time do:

    python bootstrap.py
    bin/buildout -c buildout-demo.cfg
    bin/develop activate hsmpy
    bin/buildout -c buildout-demo.cfg  # makes buildout aware of hsmpy

Then you can run it using:
    
    bin/mypy_demo -m demo.demo

**Note**: demo app has dependency on Tkinter for GUI. If you get
Tkinter-related ImportError try installing `python-tk` package on your system.

If you get hsmpy-related error either you didn't activate the hsmpy package
using commands above or I've broken compatibility and didn't update demo app.


Differences between quadpy and jsQuad
-------------------------------------
* dropped requirements for contained objects to implement `QTenclosed`,
  `QToverlaps`, `QTquadrantNode`, those checks are now performed by
  quadtree - that is enough for coarse querying, exact hit testing is left to
  the user
* changed requirement for `QTsetParent` and `QTgetParent`, see next point
* **contained objects are required to expose these two properties** (must
  be able to set their values):
  - **`bounds`** - 4-tuple specifying sides *(left_x, top_y, right_x, bottom_y)*
  - **`qt_data`** - will be set by quadpy upon inserting

* method names converted from camelCase to underscore_format
* quadrants are placed in different order: TL, TR, BL, BR
* `subdivide` is a method of Node

* original code had following bugs:
  - removing would cause infinite loop (*jsQuad.js line 120*: `.remove` should
    be `._remove`)
  - removing last element from node didn't remove the node (nor its parents)

* added method `get_children_under_point` (works by calling
  get_overlapped_children with zero-dimensions rectangle)

* removed methods: 
  - `selectChildren` (use `get_children`)
  - `selectEnclosed` (use `get_enclosed_children`)
  - `selectOverlapping` (use `get_overlapped_children`)
  - `mapChildren`
  - `mapEnclosed`
  - `mapOverlapping`
  - `applyChildren`
  - `applyEnclosed`
  - `applyOverlapping`


Note that although this implementation is currently *MX-CIF* as the one it's
based on, that might change in the future if need be.



*original readme below*

- - -


jsQuad
===
Author: Patrick DeHaan <me@pdehaan.com>

Brief:  MX-CIF Quadtrees implementation in javascript.

Overview
===
MX-CIF quadtrees store region bounded objects in the smallest sub-node that fully encloses them. Nodes may have any number of children and may or may not have four quadrant sub-nodes. The current implementation does not support placing a given object into a multiple trees simultaneously.

This form of quadtree is useful for storing objects with 2d spatial dimensions while providing efficient methods of searching for objects with given spatial properties (overlapping regions, enclosed by regions, enclosing regions, etc.)

Note that it is also perfectly reasonable to store point objects as well, just pretend it's boundaries are the same.


Object method requirements
---
For flexability, this implementation defers certain logic to the contained objects, thus requiring that they provide the following methods:

	.QTenclosed(xMin, yMin, xMax, yMax) -> boolean
return true if the object fits entirely within the boundary given.

	.QToverlaps(xMin, yMin, xMax, yMax) -> boolean
return true if the object overlaps the boundary given.

	.QTquadrantNode(root, x, y) -> number
return null if the object overlaps x or y. If not, return root.q1, root.q2, root.q3, or root.q4, corresponding to the relative quadrant the object is a part of. Quadrant numbers start to the upper left and go counter-clockwise.

	.QTsetParent(parent) -> void
store the given parent node somewhere it can be recalled. Previous values may be overwritten (it's not a stack).

	.QTgetParent() -> node
return the previously stored parent node.

No access to the objects will occur except through these methods. This enables object boundary definitions to be handled in whatever manner is most suitable for that type. Note that if objects are moved they should call the quadtree's .reinsert(child) method in order to rebuild the tree.

Useage
===
Creation
---
	var tree = new Quadtree(xMin, yMin, xMax, yMax, maxDepth);

[xMin], [yMin], [xMax], and [yMax] define the boundaries of the quadtree.

[maxDepth] defines the maximum number of times to subdivide the tree nodes. A value of 0 indicates no subdivisions.

Insertion
---
	tree.insert(object);

[object] is expected to implement the methods detailed below in order for the quadtree to manage it correctly.

Manipulation
---
	tree.reinsert(child)

[child] is removed from the tree and re-inserted. This method should be used for any object whose boundaries have changed. While the end result is the same, this can be faster than using tree.remove(child) and tree.insert(child). It achieves this by determining how far the child has moved from it's parent.
If that value is sufficiently small, fewer insertion recursions are required.

	tree.remove(child)
[child] is removed from the tree.

Retrieval
---
	tree.getChildren()
returns all objects in the tree

	tree.getEnclosed(xMin, yMin, xMax, yMax)
returns all objects that are entirely enclosed by the given boundary.

	tree.getOverlapping(xMin, yMin, xMax, yMax)
return all objects that are overlapping the given boundary.

Mapping
---
These methods work like the retrieval methods, but the returned list contains
the result of executing [callback] with each object instead of the objects.

	tree.map(callback)
	tree.mapEnclosed(xMin, yMin, xMax, yMax, callback)
	tree.mapOverlapping(xMin, yMin, xMax, yMax, callback)

Iterating
---
These functions are nearly identical to the mapping functions, but do not
return the results.

	tree.apply()
	thee.applyEnclosed(...)
	tree.applyOverlapping(...)

Clearing
---
	tree.clear()
This empties the tree (all children and sub-nodes are removed).

