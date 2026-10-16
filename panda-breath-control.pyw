"""Double-click launcher (Windows runs .pyw files without a console window).

Same as `python -m panda_breath_control`. Add --demo to try it without a heater.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from panda_breath_control.ui import main  # noqa: E402

sys.exit(main())
