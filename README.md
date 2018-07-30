# PyChunkCopier

PyChunkCopier is a lightweight utility for selectively copying chunks from one Minecraft world to another. Currently,
it is capable of copying a single cuboid region across worlds.

### Requirements
PyChunkCopier requires Python 3 and no additional dependencies.

### Usage
Create two directories alongside the script called `source` and `target`, and copy the appropriate region files into
them. If unsure which files are relevant, [use this page](https://dinnerbone.com/minecraft/tools/coordinates/) or just
copy them all. The files may be directly under these directories, or in a `region` sub-directory.

```
python copy_chunks.py <x1> <z1> <x2> <z2>
```

Where (`x1`, `z1`) and (`x2`, `z2`) are two opposite corners (inclusive) of the cuboid region to be copied in chunk
coordinates. (This is trivial to compute from block coordinates: just divide by 16 and take the floor.) The cuboid will
be extracted from the region files in `source` and inserted into the region files in `target` with the results being
saved to a directory titled `merged` (the original files will remain unmodified).

### Use Cases
The main use case for this utility is restoring chunks from backup which have been damaged in some way, be it
corruption, griefing, or anything else, without restoring the entire region.

It could also possibly be used as a less-refined alternative to WorldEdit for the purpose of copying structures between
worlds.

### License
PyChunkCopier is released under the MIT License.
