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
            hwp = win32.gencache.EnsureDispatch("HWPFrame.HwpObject")
            return hwp
        except Exception as e:
            raise RuntimeError(f"Failed to create HWP instance: {e}")

    @property
    def hwp(self) -> Any:
        """Get IHwpObject COM object, creating it if necessary."""
        if self._hwp is None:
            self._hwp = self._create_hwp_instance()
        return self._hwp

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

    def open_document(self, path: str, format: Optional[str] = None) -> HwpResult:
        """
        Open a document using IXHwpDocuments.Open() method.

        Args:
            path: File path to open
            format: Optional format string

        Returns:
            HwpResult with IXHwpDocument object reference
        """
        file_path = Path(path)
        if not file_path.exists():
            return HwpResult.fail(f"File not found: {path}")

        try:
            docs = self.hwp.XHwpDocuments
            if format:
                doc = docs.Open(str(file_path.absolute()), format)
            else:
                doc = docs.Open(str(file_path.absolute()))

            if doc is None:
                return HwpResult.fail(f"Failed to open document: {path}")

            return HwpResult.ok({
                "document": doc,
                "path": str(file_path.absolute())
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
            active_doc = docs.ActiveDocument
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

    def close_document(
        self, doc: Any, save_changes: bool = False
    ) -> HwpResult:
        """
        Close document using IXHwpDocument.Close() method.

        Args:
            doc: IXHwpDocument object
            save_changes: Whether to save changes before closing

        Returns:
            HwpResult indicating success or failure
        """
        try:
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
