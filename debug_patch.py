#!/usr/bin/env python3
"""
Patch to prevent mimetypes from hanging when reading Windows registry during debugging.
This should be imported before any other modules that might trigger openpyxl import.
"""
import mimetypes
import os

def patch_mimetypes_for_debugging():
    """Prevent mimetypes from reading Windows registry during debugging."""
    # Store original method
    original_read_windows_registry = mimetypes.MimeTypes.read_windows_registry
    
    # Create a no-op replacement
    def safe_read_windows_registry(self):
        """Skip Windows registry read to prevent debugger hang."""
        pass
    
    # Replace the method
    mimetypes.MimeTypes.read_windows_registry = safe_read_windows_registry
    print("DEBUG: Patched mimetypes to skip Windows registry read")

# Apply the patch
if __name__ != "__main__":
    patch_mimetypes_for_debugging()