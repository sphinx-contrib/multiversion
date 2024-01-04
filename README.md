# sphinx-multiversion

Fork of https://github.com/Holzhaus/sphinx-multiversion

Sphinx extension for building self-hosted versioned docs.

This extension aims to provide a clean implementation that tries to avoid messing with Sphinx internals as much as possible.

Documentation can be found at: https://holzhaus.github.io/sphinx-multiversion/

## Fork Additions

### Fixed temp directory issue

Fixed an issue with temp directories not initializing as valid Git repositories when cloning remote branches.
