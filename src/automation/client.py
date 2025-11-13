"""HWP Automation API client using OLE Object Model.

Based on Idris2 formal specification in Specs/AutomationMCP.idr and
HwpBooks/HwpAutomation_2504.pdf reference document.

Uses OLE Automation approach (properties/methods on objects)
rather than ActionTable approach (action IDs with parameter sets).
"""

from typing import Optional, Any, Union
from pathlib import Path

try:
    import win32com.client as win32
    import pythoncom
except ImportError:
    raise ImportError(
        "pywin32 is required for HWP automation. "
        "Install it with: uv pip install pywin32"
    )

from ..common.types import HwpResult


class AutomationClient:
    """
    HWP Automation API client using OLE Object Model.

    Based on Idris2 formal specification in Specs/AutomationMCP.idr and
    HwpAutomation_2504.pdf reference document.

    This uses the object-oriented Automation API:
    - IHwpObject (root application object)
    - IXHwpDocuments (document collection)
    - IXHwpDocument (individual document)
    - IXHwpWindows (window collection)
    - IXHwpWindow (individual window)
    """

    def __init__(self):
        """Initialize HWP Automation client."""
        self._hwp: Optional[Any] = None

    def _ensure_com_initialized(self) -> None:
        """Ensure COM is initialized for the current thread."""
        try:
            pythoncom.CoInitialize()
        except Exception:
            pass  # Already initialized

    def _create_hwp_instance(self) -> Any:
        """Create HWP COM instance (IHwpObject)."""
        self._ensure_com_initialized()
        try:
            # Use DispatchEx for late binding (like working scripts)
            # This avoids issues with gencache type library binding
            hwp = win32.DispatchEx("HWPFrame.HwpObject")
            return hwp
        except Exception as e:
            raise RuntimeError(f"Failed to create HWP instance: {e}")

    @property
    def hwp(self) -> Any:
        """Get IHwpObject COM object, creating it if necessary."""
        if self._hwp is None:
            self._hwp = self._create_hwp_instance()
        return self._hwp

    def register_security_module(self, module_path: str) -> HwpResult:
        """
        Register security module to bypass file access approval messages.

        Args:
            module_path: Full path to FilePathCheckerModuleExample.dll

        Returns:
            HwpResult indicating success or failure

        Note:
            The security module (FilePathCheckerModuleExample.dll) handles
            file validity and security checks, preventing security approval
            messages when accessing or saving local files.

            See Security/SecurityModule.md for details.
        """
        try:
            module_file = Path(module_path)
            if not module_file.exists():
                return HwpResult.fail(f"Security module not found: {module_path}")

            self.hwp.RegisterModule("FilePathCheckDLL", str(module_file.absolute()))
            return HwpResult.ok({
                "module": "FilePathCheckDLL",
                "path": str(module_file.absolute())
            })
        except Exception as e:
            return HwpResult.fail(f"Failed to register security module: {e}")

    def get_documents(self) -> HwpResult:
        """
        Get the XHwpDocuments collection from IHwpObject.

        Returns:
            HwpResult with IXHwpDocuments object reference
        """
        try:
            docs = self.hwp.XHwpDocuments
            if docs is None:
                return HwpResult.fail("XHwpDocuments collection not available")
            return HwpResult.ok({"documents": docs, "count": docs.Count})
        except Exception as e:
            return HwpResult.fail(f"Failed to get documents collection: {e}")

    def open_document(
        self,
        path: str,
        format: Optional[str] = "HWP",
        options: Optional[str] = ""
    ) -> HwpResult:
        """
        Open a document using IHwpObject.Open() method.

        Args:
            path: File path to open
            format: File format (default: "HWP")
            options: Open options (e.g., "readonly:true")

        Returns:
            HwpResult with document info
        """
        file_path = Path(path)
        if not file_path.exists():
            return HwpResult.fail(f"File not found: {path}")

        try:
            # Use IHwpObject.Open() method (not XHwpDocuments.Open)
            result = self.hwp.Open(str(file_path.absolute()), format, options)

            if not result:
                return HwpResult.fail(f"Failed to open document: {path}")

            # Get the active document after opening
            active_result = self.get_active_document()
            if active_result.success:
                return HwpResult.ok({
                    "document": active_result.value["document"],
                    "path": str(file_path.absolute()),
                    "opened": result
                })
            else:
                # Even if we can't get the active doc, opening succeeded
                return HwpResult.ok({
                    "path": str(file_path.absolute()),
                    "opened": result
                })
        except Exception as e:
            return HwpResult.fail(f"Failed to open document: {e}")

    def get_active_document(self) -> HwpResult:
        """
        Get the currently active document.

        Returns:
            HwpResult with IXHwpDocument object reference
        """
        try:
            docs = self.hwp.XHwpDocuments
            if docs.Count == 0:
                return HwpResult.fail("No documents open")

            # Get the first document (typically the active one)
            # Note: XHwpDocuments doesn't have ActiveDocument property,
            # so we use Item(0) to get the first document
            active_doc = docs.Item(0)
            if active_doc is None:
                return HwpResult.fail("No active document")
            return HwpResult.ok({"document": active_doc})
        except Exception as e:
            return HwpResult.fail(f"Failed to get active document: {e}")

    def get_document_property(self, doc: Any, property_name: str) -> HwpResult:
        """
        Get a property value from IXHwpDocument.

        Args:
            doc: IXHwpDocument object
            property_name: Name of property (Path, IsModified, DocumentName, etc.)

        Returns:
            HwpResult with property value
        """
        try:
            value = getattr(doc, property_name)
            return HwpResult.ok({property_name: value})
        except AttributeError:
            return HwpResult.fail(f"Property not found: {property_name}")
        except Exception as e:
            return HwpResult.fail(f"Failed to get property {property_name}: {e}")

    def set_document_property(
        self, doc: Any, property_name: str, value: Any
    ) -> HwpResult:
        """
        Set a property value on IXHwpDocument (if writable).

        Args:
            doc: IXHwpDocument object
            property_name: Name of property
            value: New value

        Returns:
            HwpResult indicating success or failure
        """
        try:
            setattr(doc, property_name, value)
            return HwpResult.ok({property_name: value})
        except AttributeError:
            return HwpResult.fail(f"Property not found or read-only: {property_name}")
        except Exception as e:
            return HwpResult.fail(f"Failed to set property {property_name}: {e}")

    def invoke_document_method(
        self, doc: Any, method_name: str, *args
    ) -> HwpResult:
        """
        Invoke a method on IXHwpDocument.

        Args:
            doc: IXHwpDocument object
            method_name: Name of method (Save, SaveAs, Close, etc.)
            *args: Method arguments

        Returns:
            HwpResult with method return value
        """
        try:
            method = getattr(doc, method_name)
            result = method(*args)
            return HwpResult.ok({"result": result})
        except AttributeError:
            return HwpResult.fail(f"Method not found: {method_name}")
        except Exception as e:
            return HwpResult.fail(f"Failed to invoke method {method_name}: {e}")

    def save_document(
        self,
        doc: Any,
        format: Optional[str] = None,
        options: Optional[str] = None
    ) -> HwpResult:
        """
        Save document using IXHwpDocument.Save() method.

        Args:
            doc: IXHwpDocument object
            format: Optional save format
            options: Optional save options

        Returns:
            HwpResult indicating success or failure
        """
        try:
            args = []
            if format:
                args.append(format)
            if options:
                args.append(options)

            result = doc.Save(*args) if args else doc.Save()
            return HwpResult.ok({"saved": result})
        except Exception as e:
            return HwpResult.fail(f"Failed to save document: {e}")

    def save_document_as(
        self,
        path: str,
        format: Optional[str] = "HWP",
        options: Optional[str] = None
    ) -> HwpResult:
        """
        Save the active document to a new path using HAction FileSaveAs_S.

        This is a convenience method that wraps the HAction approach for
        SaveAs operations, commonly used in scripts.

        Args:
            path: File path to save to
            format: Save format (default: "HWP")
            options: Optional save options

        Returns:
            HwpResult indicating success or failure
        """
        try:
            # Get active document first
            active_result = self.get_active_document()
            if not active_result.success:
                return HwpResult.fail("No active document to save")

            # Use HAction FileSaveAs_S approach
            self.hwp.HAction.GetDefault("FileSaveAs_S", self.hwp.HParameterSet.HFileOpenSave.HSet)
            self.hwp.HParameterSet.HFileOpenSave.filename = str(Path(path).absolute())
            self.hwp.HParameterSet.HFileOpenSave.Format = format
            self.hwp.HParameterSet.HFileOpenSave.Attributes = 1

            result = self.hwp.HAction.Execute("FileSaveAs_S", self.hwp.HParameterSet.HFileOpenSave.HSet)

            if result:
                return HwpResult.ok({
                    "saved_as": str(Path(path).absolute()),
                    "format": format
                })
            else:
                return HwpResult.fail(f"Failed to save document as: {path}")
        except Exception as e:
            return HwpResult.fail(f"Failed to save document as: {e}")

    def close_document(
        self, doc: Optional[Any] = None, save_changes: bool = False
    ) -> HwpResult:
        """
        Close document using IXHwpDocument.Close() method.

        Args:
            doc: IXHwpDocument object (if None, closes active document)
            save_changes: Whether to save changes before closing

        Returns:
            HwpResult indicating success or failure
        """
        try:
            # If no doc specified, use active document
            if doc is None:
                active_result = self.get_active_document()
                if not active_result.success:
                    return HwpResult.fail("No active document to close")
                doc = active_result.value["document"]

            result = doc.Close(save_changes)
            return HwpResult.ok({"closed": result})
        except Exception as e:
            return HwpResult.fail(f"Failed to close document: {e}")

    def get_windows(self) -> HwpResult:
        """
        Get the XHwpWindows collection from IHwpObject.

        Returns:
            HwpResult with IXHwpWindows object reference
        """
        try:
            windows = self.hwp.XHwpWindows
            if windows is None:
                return HwpResult.fail("XHwpWindows collection not available")
            return HwpResult.ok({"windows": windows, "count": windows.Count})
        except Exception as e:
            return HwpResult.fail(f"Failed to get windows collection: {e}")

    def get_active_window(self) -> HwpResult:
        """
        Get the currently active window.

        Returns:
            HwpResult with IXHwpWindow object reference
        """
        try:
            windows = self.hwp.XHwpWindows
            active_window = windows.ActiveWindow
            if active_window is None:
                return HwpResult.fail("No active window")
            return HwpResult.ok({"window": active_window})
        except Exception as e:
            return HwpResult.fail(f"Failed to get active window: {e}")

    def get_hwp_property(self, property_name: str) -> HwpResult:
        """
        Get a property value from IHwpObject.

        Args:
            property_name: Name of property (Version, IsEmpty, EditMode, Path)

        Returns:
            HwpResult with property value
        """
        try:
            value = getattr(self.hwp, property_name)
            return HwpResult.ok({property_name: value})
        except AttributeError:
            return HwpResult.fail(f"Property not found: {property_name}")
        except Exception as e:
            return HwpResult.fail(f"Failed to get property {property_name}: {e}")

    def set_hwp_property(self, property_name: str, value: Any) -> HwpResult:
        """
        Set a property value on IHwpObject (if writable).

        Args:
            property_name: Name of property (e.g., EditMode)
            value: New value

        Returns:
            HwpResult indicating success or failure
        """
        try:
            setattr(self.hwp, property_name, value)
            return HwpResult.ok({property_name: value})
        except AttributeError:
            return HwpResult.fail(f"Property not found or read-only: {property_name}")
        except Exception as e:
            return HwpResult.fail(f"Failed to set property {property_name}: {e}")

    def quit(self) -> HwpResult:
        """
        Quit the HWP application using IHwpObject.Quit() method.

        Returns:
            HwpResult indicating success or failure
        """
        try:
            self.hwp.Quit()
            self._hwp = None
            return HwpResult.ok({"quit": True})
        except Exception as e:
            return HwpResult.fail(f"Failed to quit HWP: {e}")

    # ------------------------------------------------------------------------
    # State Query Methods (EventHandler Alternative - Option B)
    # Based on Specs/AutomationState.idr
    # ------------------------------------------------------------------------

    def is_document_modified(self) -> HwpResult:
        """
        Check if the current document has been modified.

        EventHandler alternative: Replaces DocumentChange event detection.
        Based on Specs/AutomationState.idr - ModificationStatus type.

        Returns:
            HwpResult with {"is_modified": bool}
        """
        active_result = self.get_active_document()
        if not active_result.success:
            return HwpResult.fail("No active document to check modification status")

        doc = active_result.value["document"]
        try:
            is_modified = doc.IsModified
            return HwpResult.ok({
                "is_modified": bool(is_modified),
                "status": "Modified" if is_modified else "Unmodified"
            })
        except Exception as e:
            return HwpResult.fail(f"Failed to check modification status: {e}")

    def get_document_path(self) -> HwpResult:
        """
        Get the file path of the current document.

        EventHandler alternative: Helps detect DocumentAfterOpen/DocumentAfterSave.
        Based on Specs/AutomationState.idr - DocumentPath type.

        Returns:
            HwpResult with {"has_path": bool, "path": str}
        """
        active_result = self.get_active_document()
        if not active_result.success:
            return HwpResult.fail("No active document to get path")

        doc = active_result.value["document"]
        try:
            path = doc.Path
            has_path = bool(path and path.strip())
            return HwpResult.ok({
                "has_path": has_path,
                "path": path if has_path else "",
                "status": "Path exists" if has_path else "No path (new document)"
            })
        except Exception as e:
            return HwpResult.fail(f"Failed to get document path: {e}")

    def get_edit_mode(self) -> HwpResult:
        """
        Get the current edit mode of the HWP application.

        EventHandler alternative: Detects if document is read-only or editable.
        Based on Specs/AutomationState.idr - EditMode type.

        Returns:
            HwpResult with {"edit_mode": str} (ReadOnly, Editable, or Locked)
        """
        try:
            # EditMode property on IHwpObject
            edit_mode = self.hwp.EditMode
            # Map numeric value to string
            # Typical values: 0=ReadOnly, 1=Editable (actual mapping may vary)
            mode_str = "Editable" if edit_mode else "ReadOnly"
            return HwpResult.ok({
                "edit_mode": mode_str,
                "raw_value": edit_mode
            })
        except Exception as e:
            return HwpResult.fail(f"Failed to get edit mode: {e}")

    def get_document_count(self) -> HwpResult:
        """
        Get the number of currently open documents.

        EventHandler alternative: Helps detect DocumentAfterOpen/DocumentAfterClose.
        Based on Specs/AutomationState.idr - DocumentStateSnapshot.documentCount.

        Returns:
            HwpResult with {"count": int}
        """
        docs_result = self.get_documents()
        if not docs_result.success:
            return HwpResult.fail("Failed to get documents collection")

        return HwpResult.ok({"count": docs_result.value["count"]})

    def get_state_snapshot(self) -> HwpResult:
        """
        Get a complete state snapshot of the current document.

        Combines all state query methods into a single snapshot for efficient
        change detection. Based on Specs/AutomationState.idr - DocumentStateSnapshot.

        Returns:
            HwpResult with complete state snapshot:
            {
                "is_modified": bool,
                "has_path": bool,
                "path": str,
                "edit_mode": str,
                "document_count": int
            }
        """
        snapshot = {}

        # Get document count (always succeeds even if no documents open)
        count_result = self.get_document_count()
        snapshot["document_count"] = count_result.value["count"] if count_result.success else 0

        # If no documents, return partial snapshot
        if snapshot["document_count"] == 0:
            return HwpResult.ok({
                "is_modified": False,
                "has_path": False,
                "path": "",
                "edit_mode": "ReadOnly",
                "document_count": 0,
                "status": "No open documents"
            })

        # Get modification status
        mod_result = self.is_document_modified()
        snapshot["is_modified"] = mod_result.value["is_modified"] if mod_result.success else False

        # Get document path
        path_result = self.get_document_path()
        if path_result.success:
            snapshot["has_path"] = path_result.value["has_path"]
            snapshot["path"] = path_result.value["path"]
        else:
            snapshot["has_path"] = False
            snapshot["path"] = ""

        # Get edit mode
        mode_result = self.get_edit_mode()
        snapshot["edit_mode"] = mode_result.value["edit_mode"] if mode_result.success else "Unknown"

        return HwpResult.ok(snapshot)

    def cleanup(self) -> None:
        """Clean up COM resources."""
        if self._hwp is not None:
            try:
                self._hwp.Quit()
            except Exception:
                pass
            finally:
                self._hwp = None
                pythoncom.CoUninitialize()
